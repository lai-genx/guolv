"""
分发模块 - 邮件、企业微信发送
"""
import json
from datetime import datetime
from typing import List, Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
import smtplib

import httpx
from loguru import logger

from config import settings
from models import WeeklyReport


class EmailSender:
    """邮件发送器"""
    
    def __init__(self):
        self.smtp_server = settings.distribution.smtp_server
        self.smtp_port = settings.distribution.smtp_port
        self.smtp_user = settings.distribution.smtp_user
        self.smtp_password = settings.distribution.smtp_password
        self.use_tls = settings.distribution.smtp_use_tls
        self.sender = settings.distribution.email_sender or self.smtp_user
        self.recipients = settings.distribution.email_recipients_list
    
    def is_configured(self) -> bool:
        """检查是否已配置"""
        return all([
            self.smtp_server,
            self.smtp_user,
            self.smtp_password,
            self.recipients
        ])
    
    async def send_report(self, report: WeeklyReport) -> bool:
        """
        发送周报邮件
        
        Args:
            report: 周报对象
        
        Returns:
            是否发送成功
        """
        if not self.is_configured():
            logger.warning("邮件未配置，跳过发送")
            return False
        
        try:
            # 创建邮件
            msg = MIMEMultipart('alternative')
            msg['Subject'] = Header(f"通信设备产业情报周报 | 第{report.issue_no}期", 'utf-8')
            msg['From'] = self.sender
            msg['To'] = ', '.join(self.recipients)
            
            # 添加纯文本版本
            text_part = MIMEText(report.report_md, 'plain', 'utf-8')
            msg.attach(text_part)
            
            # 添加HTML版本
            html_part = MIMEText(report.report_html, 'html', 'utf-8')
            msg.attach(html_part)
            
            # 连接SMTP服务器并发送
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                if self.use_tls:
                    server.starttls()
                
                server.login(self.smtp_user, self.smtp_password)
                server.sendmail(self.sender, self.recipients, msg.as_string())
            
            logger.info(f"周报邮件发送成功: 第{report.issue_no}期")
            return True
        
        except Exception as e:
            logger.error(f"发送邮件失败: {e}")
            return False
    
    async def send_simple(self, subject: str, content: str, is_html: bool = False) -> bool:
        """发送简单邮件"""
        if not self.is_configured():
            return False
        
        try:
            msg = MIMEMultipart()
            msg['Subject'] = Header(subject, 'utf-8')
            msg['From'] = self.sender
            msg['To'] = ', '.join(self.recipients)
            
            content_type = 'html' if is_html else 'plain'
            msg.attach(MIMEText(content, content_type, 'utf-8'))
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                if self.use_tls:
                    server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.sendmail(self.sender, self.recipients, msg.as_string())
            
            logger.info(f"邮件发送成功: {subject}")
            return True
        
        except Exception as e:
            logger.error(f"发送邮件失败: {e}")
            return False


class WeChatSender:
    """企业微信发送器"""
    
    def __init__(self):
        self.webhook_url = settings.distribution.wechat_webhook_url
    
    def is_configured(self) -> bool:
        """检查是否已配置"""
        return bool(self.webhook_url)
    
    async def send_markdown(self, content: str) -> bool:
        """
        发送Markdown消息到企业微信
        
        Args:
            content: Markdown格式内容
        
        Returns:
            是否发送成功
        """
        if not self.is_configured():
            logger.warning("企业微信未配置，跳过发送")
            return False
        
        # 企业微信消息长度限制
        max_length = 4096
        if len(content) > max_length:
            content = content[:max_length - 100] + "\n\n...[内容过长，请查看完整报告]"
        
        payload = {
            "msgtype": "markdown",
            "markdown": {
                "content": content
            }
        }
        
        return await self._send(payload)
    
    async def send_text(self, content: str, mentioned_list: List[str] = None) -> bool:
        """
        发送文本消息
        
        Args:
            content: 文本内容
            mentioned_list: @用户列表
        
        Returns:
            是否发送成功
        """
        if not self.is_configured():
            return False
        
        payload = {
            "msgtype": "text",
            "text": {
                "content": content,
                "mentioned_list": mentioned_list or []
            }
        }
        
        return await self._send(payload)
    
    async def send_news(self, title: str, description: str, url: str, pic_url: str = "") -> bool:
        """
        发送图文消息
        
        Args:
            title: 标题
            description: 描述
            url: 点击跳转链接
            pic_url: 图片链接
        
        Returns:
            是否发送成功
        """
        if not self.is_configured():
            return False
        
        payload = {
            "msgtype": "news",
            "news": {
                "articles": [
                    {
                        "title": title,
                        "description": description,
                        "url": url,
                        "picurl": pic_url
                    }
                ]
            }
        }
        
        return await self._send(payload)
    
    async def _send(self, payload: dict) -> bool:
        """发送消息到企业微信"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.webhook_url,
                    json=payload,
                    timeout=30
                )
                response.raise_for_status()
                
                result = response.json()
                if result.get("errcode") == 0:
                    logger.info("企业微信消息发送成功")
                    return True
                else:
                    logger.error(f"企业微信发送失败: {result}")
                    return False
        
        except Exception as e:
            logger.error(f"企业微信发送失败: {e}")
            return False
    
    async def send_report_summary(self, report: WeeklyReport) -> bool:
        """
        发送周报摘要到企业微信 - 增强版（包含Top5条目而非仅元数据）

        Args:
            report: 周报对象

        Returns:
            是否发送成功
        """
        from database import db
        from datetime import timedelta

        date_range = f"{report.date_start.strftime('%Y-%m-%d')} ~ {report.date_end.strftime('%Y-%m-%d')}"

        # 从数据库查询本周的最重要条目（decision_value=True, importance>=4）
        top_items = db.get_items_for_report(days=7)  # 获取本周条目
        top_items = [item for item in top_items if item.decision_value and item.importance >= 4]
        top_items = sorted(top_items, key=lambda x: x.importance, reverse=True)[:5]

        # 构建微信消息
        summary = f"""## 通信设备产业情报周报 | 第{report.issue_no}期

**{date_range}**

"""

        # 发送 Top5 核心条目
        if top_items:
            summary += f"### 📌 本周核心情报（共{len(top_items)}条）\n\n"
            for i, item in enumerate(top_items, 1):
                summary += f"**{i}. {item.title[:50]}**\n"
                summary += f"   {item.one_line_insight or item.summary_zh[:80]}\n"
                summary += f"   [来源: {item.source_name}]({item.source_url})\n\n"
        else:
            summary += "本周暂无重大事件\n\n"

        # 添加统计概览
        summary += f"""### 📊 本周概览
- 情报条目: **{report.total_items}** 条
- 决策价值: **{len(top_items)}** 条
- 监控公司数: **{len(report.importance_distribution)}** 个维度

### 📬 查看详情
完整报告已发送至邮箱，敬请查收。
"""

        # 企业微信消息长度限制
        max_length = 4096
        if len(summary) > max_length:
            summary = summary[:max_length - 100] + "\n\n...[内容过长，请查看完整报告]"

        return await self.send_markdown(summary)


class Distributor:
    """分发管理器"""
    
    def __init__(self):
        self.email_sender = EmailSender()
        self.wechat_sender = WeChatSender()
    
    async def distribute_report(self, report: WeeklyReport) -> dict:
        """
        分发周报
        
        Args:
            report: 周报对象
        
        Returns:
            分发结果
        """
        results = {
            'email': False,
            'wechat': False
        }
        
        # 邮件发送
        if settings.distribution.enable_email and self.email_sender.is_configured():
            results['email'] = await self.email_sender.send_report(report)
            if results['email']:
                report.sent_email = True
        
        # 企业微信发送（发送摘要）
        if settings.distribution.enable_wechat and self.wechat_sender.is_configured():
            results['wechat'] = await self.wechat_sender.send_report_summary(report)
            if results['wechat']:
                report.sent_wechat = True
        
        # 更新发送状态
        if results['email'] or results['wechat']:
            report.sent_at = datetime.now()
            from database import db
            db.save_weekly_report(report)
        
        logger.info(f"周报分发完成: 邮件={results['email']}, 微信={results['wechat']}")
        
        return results
    
    async def send_notification(self, message: str, channels: List[str] = None) -> dict:
        """
        发送通知

        Args:
            message: 消息内容
            channels: 发送渠道 ['email', 'wechat']

        Returns:
            发送结果
        """
        if channels is None:
            channels = ['email', 'wechat']

        results = {}

        if 'email' in channels:
            results['email'] = await self.email_sender.send_simple(
                "CT产业情报Agent通知",
                message
            )

        if 'wechat' in channels:
            results['wechat'] = await self.wechat_sender.send_text(message)

        return results

    async def send_collect_summary(self, analyzed_items: List) -> bool:
        """
        发送采集结果摘要邮件

        Args:
            analyzed_items: 分析后的情报条目列表

        Returns:
            是否发送成功
        """
        if not analyzed_items or not self.email_sender.is_configured():
            logger.warning("采集结果为空或邮件未配置，跳过发送")
            return False

        try:
            # 统计数据
            total_items = len(analyzed_items)
            by_source = {}
            by_category = {}
            by_importance = {}

            for item in analyzed_items:
                # 按来源统计
                source = item.source_name or item.source_type
                by_source[source] = by_source.get(source, 0) + 1

                # 按分类统计
                category = item.category.value if item.category else "未分类"
                by_category[category] = by_category.get(category, 0) + 1

                # 按重要性统计
                importance = f"{item.importance}分"
                by_importance[importance] = by_importance.get(importance, 0) + 1

            # 构建邮件内容（HTML格式）
            html_content = f"""
            <html>
            <head>
                <meta charset="utf-8">
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; color: #333; }}
                    h1 {{ color: #0066cc; border-bottom: 2px solid #0066cc; padding-bottom: 10px; }}
                    h2 {{ color: #333; margin-top: 20px; }}
                    .summary {{ background-color: #f0f8ff; padding: 15px; border-radius: 5px; margin: 15px 0; }}
                    .stat {{ margin: 10px 0; }}
                    table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
                    th, td {{ padding: 10px; text-align: left; border: 1px solid #ddd; }}
                    th {{ background-color: #0066cc; color: white; }}
                    .high {{ color: #ff6600; font-weight: bold; }}
                    .footer {{ margin-top: 30px; padding-top: 15px; border-top: 1px solid #ddd; color: #666; font-size: 12px; }}
                </style>
            </head>
            <body>
                <h1>📊 通信设备产业情报采集结果报告</h1>

                <div class="summary">
                    <h2>采集概览</h2>
                    <div class="stat"><strong>采集时间:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</div>
                    <div class="stat"><strong>采集条目数:</strong> <span class="high">{total_items}</span> 条</div>
                </div>

                <h2>按来源分布</h2>
                <table>
                    <tr>
                        <th>来源</th>
                        <th>数量</th>
                    </tr>
            """

            for source, count in sorted(by_source.items(), key=lambda x: x[1], reverse=True):
                html_content += f"<tr><td>{source}</td><td>{count}</td></tr>"

            html_content += """
                </table>

                <h2>按分类分布</h2>
                <table>
                    <tr>
                        <th>分类</th>
                        <th>数量</th>
                    </tr>
            """

            for category, count in sorted(by_category.items(), key=lambda x: x[1], reverse=True):
                html_content += f"<tr><td>{category}</td><td>{count}</td></tr>"

            html_content += """
                </table>

                <h2>按重要性分布</h2>
                <table>
                    <tr>
                        <th>重要性</th>
                        <th>数量</th>
                    </tr>
            """

            for importance in sorted(by_importance.keys()):
                count = by_importance[importance]
                html_content += f"<tr><td>{importance}</td><td>{count}</td></tr>"

            html_content += """
                </table>

                <h2>TOP 10 高重要性条目</h2>
                <table>
                    <tr>
                        <th>标题</th>
                        <th>来源</th>
                        <th>重要性</th>
                        <th>分类</th>
                    </tr>
            """

            # 按重要性排序，取前10条
            top_items = sorted(analyzed_items, key=lambda x: x.importance, reverse=True)[:10]
            for item in top_items:
                category = item.category.value if item.category else "未分类"
                html_content += f"""
                <tr>
                    <td>{item.title[:60]}...</td>
                    <td>{item.source_name or item.source_type}</td>
                    <td>{item.importance}分</td>
                    <td>{category}</td>
                </tr>
                """

            html_content += """
                </table>

                <div class="footer">
                    <p>本报告由 CT产业情报Agent 自动生成</p>
                    <p>详细信息和完整条目可登录系统查看</p>
                </div>
            </body>
            </html>
            """

            # 发送邮件
            subject = f"✉️ 通信设备产业情报采集结果 - {total_items}条新情报"
            result = await self.email_sender.send_simple(subject, html_content, is_html=True)

            if result:
                logger.info(f"采集结果邮件发送成功: {total_items}条情报")

            return result

        except Exception as e:
            logger.error(f"发送采集结果邮件失败: {e}")
            return False

