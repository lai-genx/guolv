"""
周报生成器模块
"""
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from collections import defaultdict

from loguru import logger

from config import settings
from database import db
from models import IntelItem, WeeklyReport, Category, Industry, TechDomain, ActionType
from reporters.supply_chain_report import SupplyChainReport


class ReportGenerator:
    """周报生成器"""

    def __init__(self):
        self.db = db
        self.supply_chain_report = SupplyChainReport()
    
    async def generate_weekly_report(
        self,
        days: int = 7,
        save_to_file: bool = True
    ) -> Optional[WeeklyReport]:
        """
        生成周报
        
        Args:
            days: 统计天数
            save_to_file: 是否保存到文件
        
        Returns:
            周报对象
        """
        # 1. 获取期号
        issue_no = self.db.get_latest_issue_no()
        
        # 2. 计算时间范围
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # 3. 获取情报数据
        items = self.db.get_items_for_report(days=days)
        items = [item for item in items if item.source_type != "vvihot"]
        
        if not items:
            logger.warning("本周没有符合条件的情报数据")
            # 仍然生成空报告
            items = []
        
        logger.info(f"获取到 {len(items)} 条情报用于生成周报")
        
        # 4. 统计数据
        stats = self._calculate_stats(items)
        
        # 5. 生成报告内容
        report_md = self.supply_chain_report.generate_supply_chain_markdown(
            items=items,
            issue_no=issue_no,
            date_range=f"{start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')}",
            stats=stats
        )

        report_html = self.supply_chain_report.generate_supply_chain_html(
            items=items,
            issue_no=issue_no,
            date_range=f"{start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')}",
            stats=stats
        )
        
        # 6. 创建周报对象
        report = WeeklyReport(
            issue_no=issue_no,
            date_start=start_date,
            date_end=end_date,
            report_md=report_md,
            report_html=report_html,
            total_items=len(items),
            importance_distribution=stats['importance'],
            category_distribution=stats['category']
        )
        
        # 7. 保存到数据库
        self.db.save_weekly_report(report)
        
        # 8. 保存到文件
        if save_to_file:
            await self._save_report_files(report)
        
        return report
    
    def _calculate_stats(self, items: List[IntelItem]) -> Dict[str, Any]:
        """计算统计数据"""
        stats = {
            'total': len(items),
            'importance': defaultdict(int),
            'category': defaultdict(int),
            'industry': defaultdict(int),
            'tech_domain': defaultdict(int),
            'company': defaultdict(int),
            'source_type': defaultdict(int)
        }
        
        for item in items:
            # 重要性分布
            stats['importance'][f"{item.importance}分"] += 1
            
            # 分类分布
            if item.category:
                stats['category'][item.category.value] += 1
            
            # 行业分布
            if item.industry:
                stats['industry'][item.industry.value] += 1
            
            # 技术领域分布
            if item.tech_domain:
                stats['tech_domain'][item.tech_domain.value] += 1
            
            # 公司统计
            for company in item.companies_mentioned[:1]:  # 只统计第一个公司
                stats['company'][company] += 1
            
            # 来源类型
            if item.source_type:
                stats['source_type'][item.source_type] += 1
        
        # 转换为普通dict
        return {
            'importance': dict(stats['importance']),
            'category': dict(stats['category']),
            'industry': dict(stats['industry']),
            'tech_domain': dict(stats['tech_domain']),
            'company': dict(stats['company']),
            'source_type': dict(stats['source_type']),
            'total': len(items)
        }
    
    def _generate_markdown(
        self,
        issue_no: int,
        start_date: datetime,
        end_date: datetime,
        items: List[IntelItem],
        stats: Dict[str, Any]
    ) -> str:
        """生成Markdown格式报告（包含去重、竞争对比、action_type分组等）"""
        date_range = f"{start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')}"
        shown_ids = set()  # 追踪已展示的条目ID，实现跨板块去重

        md = f"""# 通信设备产业情报周报 | 第{issue_no}期

**{date_range}**

---

## 【本周核心决策洞察】

"""

        # 核心决策洞察：所有 importance>=5 的条目
        top_items = [item for item in items if item.importance >= 5]
        top_items = sorted(top_items, key=lambda x: x.importance, reverse=True)  # 无数量限制

        if top_items:
            for item in top_items:
                md += f"- **{item.title}**\n"
                md += f"  - {item.one_line_insight or item.summary_zh[:100]}\n"
                md += f"  - 来源: {item.source_name} | [查看原文]({item.source_url})\n\n"
                shown_ids.add(id(item))
        else:
            md += "- 本周无重大事件\n\n"

        # 竞争对比表：Top5公司横向对比
        md += "---\n\n## 【竞争态势快览】\n\n"

        company_stats = defaultdict(lambda: {'count': 0, 'rnd_count': 0, 'market_count': 0, 'max_importance': 0})
        for item in items:
            for company in item.companies_mentioned:
                company_stats[company]['count'] += 1
                if item.importance > company_stats[company]['max_importance']:
                    company_stats[company]['max_importance'] = item.importance
                if item.action_type == ActionType.RND:
                    company_stats[company]['rnd_count'] += 1
                elif item.action_type == ActionType.MARKET:
                    company_stats[company]['market_count'] += 1

        top_companies = sorted(company_stats.items(), key=lambda x: x[1]['count'], reverse=True)[:5]

        if top_companies:
            md += "| 公司 | 动态数 | 研发动作 | 市场动作 | 最高重要度 |\n"
            md += "|------|--------|----------|----------|----------|\n"
            for company, stats_dict in top_companies:
                md += f"| {company} | {stats_dict['count']} | {stats_dict['rnd_count']} | {stats_dict['market_count']} | "
                md += f"{'⭐' * stats_dict['max_importance']} |\n"
            md += "\n"

        # 核心企业动态（按action_type分组）
        md += "---\n\n## 一、核心企业动态\n\n"

        company_items = self._group_by_company(items)
        for company, company_intel in sorted(company_items.items(), key=lambda x: len(x[1]), reverse=True)[:10]:
            md += f"### {company}\n\n"

            # 研发动作
            rnd_items = [item for item in company_intel if item.action_type == ActionType.RND and id(item) not in shown_ids][:3]
            if rnd_items:
                md += "**🔬 研发动态**\n\n"
                for item in rnd_items:
                    md += f"- **{item.title}** (重要度: {'⭐' * item.importance})\n"
                    md += f"  - {item.one_line_insight or item.summary_zh[:150]}\n"
                    md += f"  - 分类: {item.category.value if item.category else '未分类'} | 来源: {item.source_name}\n\n"
                    shown_ids.add(id(item))

            # 市场动作
            market_items = [item for item in company_intel if item.action_type == ActionType.MARKET and id(item) not in shown_ids][:3]
            if market_items:
                md += "**📊 市场动态**\n\n"
                for item in market_items:
                    md += f"- **{item.title}** (重要度: {'⭐' * item.importance})\n"
                    md += f"  - {item.one_line_insight or item.summary_zh[:150]}\n"
                    md += f"  - 分类: {item.category.value if item.category else '未分类'} | 来源: {item.source_name}\n\n"
                    shown_ids.add(id(item))

            # 其他动作
            other_items = [item for item in company_intel if item.action_type in [ActionType.OTHER, None] and id(item) not in shown_ids][:2]
            if other_items:
                for item in other_items:
                    md += f"- **{item.title}** (重要度: {'⭐' * item.importance})\n"
                    md += f"  - {item.one_line_insight or item.summary_zh[:150]}\n"
                    md += f"  - 分类: {item.category.value if item.category else '未分类'} | 来源: {item.source_name}\n\n"
                    shown_ids.add(id(item))

        # 技术与研发（跳过已展示的条目）
        md += "---\n\n## 二、技术与研发\n\n"

        tech_items = self._group_by_tech_domain(items)
        for domain, domain_items in tech_items.items():
            filtered_items = [item for item in domain_items if id(item) not in shown_ids][:5]
            if filtered_items:
                md += f"### {domain}\n\n"
                for item in filtered_items:
                    md += f"- **{item.title}**\n"
                    md += f"  - {item.one_line_insight or item.summary_zh[:120]}\n\n"
                    shown_ids.add(id(item))

        # 市场与下游（跳过已展示的条目）
        md += "---\n\n## 三、市场与下游应用\n\n"

        industry_items = self._group_by_industry(items)
        for industry, ind_items in industry_items.items():
            filtered_items = [item for item in ind_items if id(item) not in shown_ids][:5]
            if filtered_items:
                md += f"### {industry}\n\n"
                for item in filtered_items:
                    md += f"- **{item.title}**\n"
                    md += f"  - {item.one_line_insight or item.summary_zh[:120]}\n\n"
                    shown_ids.add(id(item))

        # 数据概览
        md += "---\n\n## 四、数据概览\n\n"
        md += f"### 本周采集统计\n\n"
        md += f"- 情报条目总数: **{stats['total']}**\n"
        md += f"- 监控公司数: **{len(stats['company'])}**\n\n"

        if stats['importance']:
            md += "### 重要性分布\n\n"
            for importance, count in sorted(stats['importance'].items()):
                md += f"- {importance}: {count}条\n"
            md += "\n"

        if stats['category']:
            md += "### 分类分布\n\n"
            for category, count in sorted(stats['category'].items(), key=lambda x: x[1], reverse=True):
                md += f"- {category}: {count}条\n"
            md += "\n"

        if stats['tech_domain']:
            md += "### 技术领域分布\n\n"
            for domain, count in sorted(stats['tech_domain'].items(), key=lambda x: x[1], reverse=True):
                md += f"- {domain}: {count}条\n"
            md += "\n"

        # 下周监控重点
        md += "---\n\n## 五、下周监控重点\n\n"

        # 异常活跃公司
        active_companies = sorted(stats['company'].items(), key=lambda x: x[1], reverse=True)[:3]
        if active_companies:
            md += "### 异常活跃公司\n\n"
            for company, count in active_companies:
                md += f"- **{company}**: 本周{count}条动态，建议重点关注\n"
            md += "\n"

        # 技术热点
        hot_domains = sorted(stats['tech_domain'].items(), key=lambda x: x[1], reverse=True)[:3]
        if hot_domains:
            md += "### 技术热点\n\n"
            for domain, count in hot_domains:
                md += f"- **{domain}**: {count}条相关情报\n"
            md += "\n"

        # 全部情报条目（重要性>=3）
        md += "---\n\n## 【全部情报条目】（重要性≥3分）\n\n"
        all_items_3plus = [item for item in items if item.importance >= 3]
        all_items_3plus = sorted(all_items_3plus, key=lambda x: (x.importance, x.created_at), reverse=True)

        if all_items_3plus:
            md += f"共 {len(all_items_3plus)} 条情报\n\n"
            for i, item in enumerate(all_items_3plus, 1):
                md += f"**{i}. {item.title}** (重要度: {'⭐' * item.importance})\n"
                md += f"   - 一句话洞察: {item.one_line_insight or item.summary_zh[:150]}\n"
                md += f"   - 分类: {item.category.value if item.category else '未分类'} | 来源: {item.source_name}\n"
                md += f"   - 链接: [{item.source_url}]({item.source_url})\n\n"
        else:
            md += "无\n\n"

        md += "---\n\n*本报告由CT产业情报Agent自动生成*\n"
        md += f"*生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*"

        return md
    
    def _generate_html(
        self,
        issue_no: int,
        start_date: datetime,
        end_date: datetime,
        items: List[IntelItem],
        stats: Dict[str, Any]
    ) -> str:
        """生成HTML格式报告（包含完整的5个section）"""
        date_range = f"{start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')}"
        shown_ids = set()  # 追踪已展示的条目ID，实现跨板块去重

        # HTML头部和样式
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>通信设备产业情报周报 - 第{issue_no}期</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Microsoft YaHei', sans-serif; line-height: 1.6; max-width: 900px; margin: 0 auto; padding: 20px; color: #333; }}
        h1 {{ color: #1a73e8; border-bottom: 2px solid #1a73e8; padding-bottom: 10px; }}
        h2 {{ color: #2c5aa0; margin-top: 30px; border-left: 4px solid #2c5aa0; padding-left: 10px; }}
        h3 {{ color: #444; margin-top: 20px; }}
        .date-range {{ color: #666; font-size: 14px; }}
        .highlight {{ background: #fff3cd; padding: 15px; border-radius: 5px; margin: 10px 0; }}
        .item {{ margin: 15px 0; padding: 10px; background: #f8f9fa; border-radius: 5px; }}
        .item-title {{ font-weight: bold; color: #1a73e8; }}
        .item-meta {{ color: #666; font-size: 12px; margin-top: 5px; }}
        .importance-5 {{ border-left: 4px solid #dc3545; }}
        .importance-4 {{ border-left: 4px solid #fd7e14; }}
        .importance-3 {{ border-left: 4px solid #ffc107; }}
        table {{ border-collapse: collapse; width: 100%; margin: 15px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background: #f2f2f2; }}
        a {{ color: #1a73e8; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
        .footer {{ margin-top: 40px; padding-top: 20px; border-top: 1px solid #ddd; color: #999; font-size: 12px; text-align: center; }}
        .section-title {{ font-size: 14px; font-weight: bold; color: #2c5aa0; margin-top: 10px; }}
    </style>
</head>
<body>
    <h1>通信设备产业情报周报 | 第{issue_no}期</h1>
    <p class="date-range">{date_range}</p>

    <h2>【本周核心决策洞察】</h2>
"""

        # 核心决策洞察：所有 importance>=5 的条目
        top_items = [item for item in items if item.importance >= 5]
        top_items = sorted(top_items, key=lambda x: x.importance, reverse=True)  # 无数量限制

        if top_items:
            html += '<div class="highlight">'
            for item in top_items:
                html += f'<div class="item importance-{item.importance}">'
                html += f'<div class="item-title">{item.title}</div>'
                html += f'<div>{item.one_line_insight or item.summary_zh[:100]}</div>'
                html += f'<div class="item-meta">来源: {item.source_name} | <a href="{item.source_url}">查看原文</a></div>'
                html += '</div>'
                shown_ids.add(id(item))
            html += '</div>'
        else:
            html += '<p>本周无重大事件</p>'

        # 竞争态势快览
        html += '<h2>【竞争态势快览】</h2>'

        company_stats = defaultdict(lambda: {'count': 0, 'rnd_count': 0, 'market_count': 0, 'max_importance': 0})
        for item in items:
            for company in item.companies_mentioned:
                company_stats[company]['count'] += 1
                if item.importance > company_stats[company]['max_importance']:
                    company_stats[company]['max_importance'] = item.importance
                if item.action_type == ActionType.RND:
                    company_stats[company]['rnd_count'] += 1
                elif item.action_type == ActionType.MARKET:
                    company_stats[company]['market_count'] += 1

        top_companies = sorted(company_stats.items(), key=lambda x: x[1]['count'], reverse=True)[:5]

        if top_companies:
            html += '<table>'
            html += '<tr><th>公司</th><th>动态数</th><th>研发动作</th><th>市场动作</th><th>最高重要度</th></tr>'
            for company, stats_dict in top_companies:
                importance_stars = '⭐' * stats_dict['max_importance']
                html += f'<tr><td>{company}</td><td>{stats_dict["count"]}</td><td>{stats_dict["rnd_count"]}</td><td>{stats_dict["market_count"]}</td><td>{importance_stars}</td></tr>'
            html += '</table>'

        # 核心企业动态
        html += '<h2>一、核心企业动态</h2>'
        company_items = self._group_by_company(items)
        for company, company_intel in sorted(company_items.items(), key=lambda x: len(x[1]), reverse=True)[:10]:
            html += f'<h3>{company}</h3>'

            # 研发动作
            rnd_items = [item for item in company_intel if item.action_type == ActionType.RND and id(item) not in shown_ids][:3]
            if rnd_items:
                html += '<div class="section-title">🔬 研发动态</div>'
                for item in rnd_items:
                    html += f'<div class="item importance-{item.importance}">'
                    html += f'<div class="item-title">{item.title}</div>'
                    html += f'<div>{item.one_line_insight or item.summary_zh[:150]}</div>'
                    html += f'<div class="item-meta">分类: {item.category.value if item.category else "未分类"} | 来源: {item.source_name}</div>'
                    html += '</div>'
                    shown_ids.add(id(item))

            # 市场动作
            market_items = [item for item in company_intel if item.action_type == ActionType.MARKET and id(item) not in shown_ids][:3]
            if market_items:
                html += '<div class="section-title">📊 市场动态</div>'
                for item in market_items:
                    html += f'<div class="item importance-{item.importance}">'
                    html += f'<div class="item-title">{item.title}</div>'
                    html += f'<div>{item.one_line_insight or item.summary_zh[:150]}</div>'
                    html += f'<div class="item-meta">分类: {item.category.value if item.category else "未分类"} | 来源: {item.source_name}</div>'
                    html += '</div>'
                    shown_ids.add(id(item))

        # 技术与研发（Section 2 - 之前缺失）
        html += '<h2>二、技术与研发</h2>'

        tech_items = self._group_by_tech_domain(items)
        for domain, domain_items in tech_items.items():
            filtered_items = [item for item in domain_items if id(item) not in shown_ids][:5]
            if filtered_items:
                html += f'<h3>{domain}</h3>'
                for item in filtered_items:
                    html += f'<div class="item importance-{item.importance}">'
                    html += f'<div class="item-title">{item.title}</div>'
                    html += f'<div>{item.one_line_insight or item.summary_zh[:120]}</div>'
                    html += f'<div class="item-meta">来源: {item.source_name}</div>'
                    html += '</div>'
                    shown_ids.add(id(item))

        # 市场与下游应用（Section 3 - 之前缺失）
        html += '<h2>三、市场与下游应用</h2>'

        industry_items = self._group_by_industry(items)
        for industry, ind_items in industry_items.items():
            filtered_items = [item for item in ind_items if id(item) not in shown_ids][:5]
            if filtered_items:
                html += f'<h3>{industry}</h3>'
                for item in filtered_items:
                    html += f'<div class="item importance-{item.importance}">'
                    html += f'<div class="item-title">{item.title}</div>'
                    html += f'<div>{item.one_line_insight or item.summary_zh[:120]}</div>'
                    html += f'<div class="item-meta">来源: {item.source_name}</div>'
                    html += '</div>'
                    shown_ids.add(id(item))

        # 数据概览
        html += '<h2>四、数据概览</h2>'
        html += f'<p>本周共采集 <strong>{stats["total"]}</strong> 条情报</p>'

        if stats['importance']:
            html += '<h3>重要性分布</h3><table>'
            html += '<tr><th>重要性</th><th>数量</th></tr>'
            for importance, count in sorted(stats['importance'].items()):
                html += f'<tr><td>{importance}</td><td>{count}</td></tr>'
            html += '</table>'

        if stats['category']:
            html += '<h3>分类分布</h3><table>'
            html += '<tr><th>分类</th><th>数量</th></tr>'
            for category, count in sorted(stats['category'].items(), key=lambda x: x[1], reverse=True):
                html += f'<tr><td>{category}</td><td>{count}</td></tr>'
            html += '</table>'

        # 下周监控重点（Section 5）
        html += '<h2>五、下周监控重点</h2>'

        active_companies = sorted(stats['company'].items(), key=lambda x: x[1], reverse=True)[:3]
        if active_companies:
            html += '<h3>异常活跃公司</h3><ul>'
            for company, count in active_companies:
                html += f'<li><strong>{company}</strong>: 本周{count}条动态，建议重点关注</li>'
            html += '</ul>'

        hot_domains = sorted(stats['tech_domain'].items(), key=lambda x: x[1], reverse=True)[:3]
        if hot_domains:
            html += '<h3>技术热点</h3><ul>'
            for domain, count in hot_domains:
                html += f'<li><strong>{domain}</strong>: {count}条相关情报</li>'
            html += '</ul>'

        # 全部情报条目（重要性>=3）
        html += '<h2>【全部情报条目】（重要性≥3分）</h2>'
        all_items_3plus = [item for item in items if item.importance >= 3]
        all_items_3plus = sorted(all_items_3plus, key=lambda x: (x.importance, x.created_at), reverse=True)

        if all_items_3plus:
            html += f'<p>共 {len(all_items_3plus)} 条情报</p>'
            html += '<table>'
            html += '<tr><th>#</th><th>标题</th><th>重要度</th><th>分类</th><th>来源</th><th>链接</th></tr>'
            for i, item in enumerate(all_items_3plus, 1):
                html += f'<tr>'
                html += f'<td>{i}</td>'
                html += f'<td>{item.title}</td>'
                html += f'<td>{"⭐" * item.importance}</td>'
                html += f'<td>{item.category.value if item.category else "未分类"}</td>'
                html += f'<td>{item.source_name}</td>'
                html += f'<td><a href="{item.source_url}">查看原文</a></td>'
                html += f'</tr>'
            html += '</table>'
        else:
            html += '<p>无</p>'

        # 页脚
        html += f'''
    <div class="footer">
        <p>本报告由CT产业情报Agent自动生成</p>
        <p>生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
</body>
</html>'''

        return html
    
    def _group_by_company(self, items: List[IntelItem]) -> Dict[str, List[IntelItem]]:
        """按公司分组"""
        groups = defaultdict(list)
        for item in items:
            companies = item.companies_mentioned or ['其他']
            primary = companies[0]
            groups[primary].append(item)
        return dict(groups)
    
    def _group_by_tech_domain(self, items: List[IntelItem]) -> Dict[str, List[IntelItem]]:
        """按技术领域分组"""
        groups = defaultdict(list)
        for item in items:
            domain = item.tech_domain.value if item.tech_domain else '其他'
            groups[domain].append(item)
        return dict(groups)
    
    def _group_by_industry(self, items: List[IntelItem]) -> Dict[str, List[IntelItem]]:
        """按行业分组"""
        groups = defaultdict(list)
        for item in items:
            industry = item.industry.value if item.industry else '其他'
            groups[industry].append(item)
        return dict(groups)
    
    async def _save_report_files(self, report: WeeklyReport):
        """保存报告文件"""
        try:
            from pathlib import Path
            
            reports_dir = settings.data_dir / "reports"
            reports_dir.mkdir(exist_ok=True)
            
            date_str = report.date_end.strftime('%Y%m%d')
            
            # 保存Markdown
            md_path = reports_dir / f"weekly_report_{date_str}_{report.issue_no}.md"
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write(report.report_md)
            logger.info(f"Markdown报告已保存: {md_path}")
            
            # 保存HTML
            html_path = reports_dir / f"weekly_report_{date_str}_{report.issue_no}.html"
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(report.report_html)
            logger.info(f"HTML报告已保存: {html_path}")
        
        except Exception as e:
            logger.error(f"保存报告文件失败: {e}")
