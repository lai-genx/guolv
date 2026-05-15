"""
供应链感知的报告生成模块
支持按产业链结构生成报告
"""
import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from collections import defaultdict

from loguru import logger

from models import IntelItem
from config import settings


class SupplyChainReport:
    """按产业链结构生成报告"""

    SUPPLY_CHAIN_CONFIG_FILE = settings.knowledge_base_dir / "supply_chain_config.yaml"

    # 上中下游产业链分类映射
    UPSTREAM_CHAINS = [
        "芯片与半导体",
        "光通信器件与模块",
    ]

    MIDSTREAM_CHAINS = [
        "无线接入设备",
        "光传输与接入",
        "核心网与数据中心",
    ]

    DOWNSTREAM_CHAINS = [
        "物联网与终端",
        "电信运营与基础设施",
    ]

    # 基于 tech_domain 推断上中下游的映射
    TECH_DOMAIN_TO_POSITION = {
        # 上游：芯片/器件相关
        "其他": "其他",
    }

    # 基于 category 推断上中下游的辅助映射
    CATEGORY_TO_POSITION = {
        # 下游：消费电子、汽车等
        "下游产业应用": "下游",
        "其他": "其他",
    }

    def __init__(self):
        """加载产业链配置"""
        self.supply_chain_config = self._load_supply_chain_config()

    def _load_supply_chain_config(self) -> Dict[str, Any]:
        """加载产业链配置"""
        try:
            with open(self.SUPPLY_CHAIN_CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                return config.get('supply_chain_structure', {})
        except Exception as e:
            logger.warning(f"加载供应链配置失败: {e}")
            return {}

    def _classify_supply_chain_position(self, item: IntelItem) -> str:
        """根据supply_chain字段判断上中下游，如果为空则根据tech_domain和category推断"""

        # 首先尝试使用 supply_chain 字段
        chain = item.supply_chain or ""
        if chain and chain != "其他":
            if chain in self.UPSTREAM_CHAINS:
                return "上游"
            elif chain in self.MIDSTREAM_CHAINS:
                return "中游"
            elif chain in self.DOWNSTREAM_CHAINS:
                return "下游"

        # 如果 supply_chain 为空，根据 tech_domain 推断
        tech_domain = item.tech_domain.value if item.tech_domain else ""

        # 上游相关技术领域
        upstream_tech = ["光通信", "核心网"]
        # 中游相关技术领域
        midstream_tech = ["无线通信", "传输承载", "接入网", "终端设备"]

        if any(t in tech_domain for t in upstream_tech):
            return "上游"
        elif any(t in tech_domain for t in midstream_tech):
            return "中游"

        # 如果还是无法判断，根据 category 推断
        category = item.category.value if item.category else ""

        if category == "下游产业应用":
            return "下游"
        elif category == "新技术":
            # 新技术如果是芯片/半导体相关，归为上游
            content = (item.title + " " + item.summary_zh).lower()
            if any(kw in content for kw in ["芯片", "半导体", "光模块", "光器件", "硅", "晶圆"]):
                return "上游"
            elif any(kw in content for kw in ["网络", "设备", "系统", "基站", "终端"]):
                return "中游"

        # 涉及公司的进一步推断
        companies_text = " ".join(item.companies_mentioned or [])

        # 上游公司关键词
        upstream_companies = ["高通", "英伟达", "博通", "英特尔", "AMD", "联发科", "展锐",
                            "博世", "德州仪器", "思佳讯", "Qorvo", "Skyworks", "村田"]
        # 中游公司关键词
        midstream_companies = ["华为", "中兴", "爱立信", "诺基亚", "思科", "Juniper",
                              "新易盛", "中际旭创", "光迅科技", "Lumentum", "Ciena"]
        # 下游公司关键词
        downstream_companies = ["中国移动", "中国电信", "中国联通", "Verizon", "AT&T",
                              "T-Mobile", "Orange", "沃达丰", "软银"]

        if any(c in companies_text for c in upstream_companies):
            return "上游"
        elif any(c in companies_text for c in midstream_companies):
            return "中游"
        elif any(c in companies_text for c in downstream_companies):
            return "下游"

        return "其他"

    def _group_items_by_upstream_midstream_downstream(
        self, items: List[IntelItem]
    ) -> Dict[str, List[IntelItem]]:
        """按上中下游分组"""
        groups = {
            "上游": [],
            "中游": [],
            "下游": [],
            "其他": []
        }

        for item in items:
            position = self._classify_supply_chain_position(item)
            groups[position].append(item)

        return groups

    def _build_weekly_summary(self, items: List[IntelItem], stats: Dict[str, Any]) -> Dict[str, Any]:
        """生成不依赖额外LLM调用的本期总结。"""
        important_items = sorted(
            [item for item in items if item.importance >= 4],
            key=lambda item: (item.importance, item.created_at),
            reverse=True,
        )

        company_activity = defaultdict(int)
        chain_activity = defaultdict(int)
        category_activity = defaultdict(int)
        source_activity = defaultdict(int)

        for item in items:
            for company in item.companies_mentioned or []:
                company_activity[company] += 1
            if item.supply_chain:
                chain_activity[item.supply_chain] += 1
            if item.category:
                category_activity[item.category.value] += 1
            if item.source_type:
                source_activity[item.source_type] += 1

        top_companies = sorted(company_activity.items(), key=lambda x: x[1], reverse=True)[:5]
        top_chains = sorted(chain_activity.items(), key=lambda x: x[1], reverse=True)[:3]
        top_categories = sorted(category_activity.items(), key=lambda x: x[1], reverse=True)[:3]
        top_sources = sorted(source_activity.items(), key=lambda x: x[1], reverse=True)
        highlights = important_items[:5]

        return {
            "total": len(items),
            "important_count": len(important_items),
            "top_companies": top_companies,
            "top_chains": top_chains,
            "top_categories": top_categories,
            "top_sources": top_sources,
            "highlights": highlights,
        }

    def _summary_markdown(self, items: List[IntelItem], stats: Dict[str, Any]) -> str:
        summary = self._build_weekly_summary(items, stats)
        md = "## 本期总结\n\n"
        md += (
            f"本期共纳入 **{summary['total']}** 条情报，其中重要性4分及以上 "
            f"**{summary['important_count']}** 条。"
        )

        if summary["top_chains"]:
            chains = "、".join(f"{name}({count}条)" for name, count in summary["top_chains"])
            md += f" 活跃产业链主要集中在：{chains}。"
        if summary["top_categories"]:
            categories = "、".join(f"{name}({count}条)" for name, count in summary["top_categories"])
            md += f" 主要事件类型为：{categories}。"
        md += "\n\n"

        if summary["top_companies"]:
            companies = "、".join(f"{name}({count}条)" for name, count in summary["top_companies"])
            md += f"- **重点企业**：{companies}\n"
        if summary["top_sources"]:
            sources = "、".join(f"{name}({count}条)" for name, count in summary["top_sources"])
            md += f"- **来源结构**：{sources}\n"
        if summary["highlights"]:
            md += "- **优先关注**：\n"
            for item in summary["highlights"]:
                insight = item.one_line_insight or item.summary_zh[:120]
                md += f"  - {item.title}：{insight}\n"
        md += "\n---\n\n"
        return md

    def _summary_html(self, items: List[IntelItem], stats: Dict[str, Any]) -> str:
        summary = self._build_weekly_summary(items, stats)
        html = '<h2>本期总结</h2>'
        html += '<div class="highlight">'
        html += (
            f'<p>本期共纳入 <strong>{summary["total"]}</strong> 条情报，其中重要性4分及以上 '
            f'<strong>{summary["important_count"]}</strong> 条。</p>'
        )
        if summary["top_chains"]:
            chains = "、".join(f"{name}({count}条)" for name, count in summary["top_chains"])
            html += f'<p><strong>活跃产业链：</strong>{chains}</p>'
        if summary["top_categories"]:
            categories = "、".join(f"{name}({count}条)" for name, count in summary["top_categories"])
            html += f'<p><strong>主要事件类型：</strong>{categories}</p>'
        if summary["top_companies"]:
            companies = "、".join(f"{name}({count}条)" for name, count in summary["top_companies"])
            html += f'<p><strong>重点企业：</strong>{companies}</p>'
        if summary["top_sources"]:
            sources = "、".join(f"{name}({count}条)" for name, count in summary["top_sources"])
            html += f'<p><strong>来源结构：</strong>{sources}</p>'
        if summary["highlights"]:
            html += '<p><strong>优先关注：</strong></p><ul>'
            for item in summary["highlights"]:
                insight = item.one_line_insight or item.summary_zh[:120]
                html += f'<li>{item.title}：{insight}</li>'
            html += '</ul>'
        html += '</div>'
        return html

    def generate_supply_chain_markdown(
        self,
        items: List[IntelItem],
        issue_no: int,
        date_range: str,
        stats: Dict[str, Any]
    ) -> str:
        """按产业链结构生成Markdown报告"""

        md = f"""# 通信设备产业情报周报 | 第{issue_no}期

**{date_range}**

---

{self._summary_markdown(items, stats)}

## 【本周核心决策洞察】

"""

        # 核心决策洞察：所有 importance>=5 的条目
        decision_items = [
            item for item in items
            if item.importance >= 5
        ]
        decision_items = sorted(
            decision_items,
            key=lambda x: x.importance,
            reverse=True
        )  # 无数量限制

        if decision_items:
            for i, item in enumerate(decision_items, 1):
                md += f"{i}. **{item.title}**\n"
                md += f"   - {item.one_line_insight or item.summary_zh[:100]}\n"
                md += f"   - [{item.source_name}]({item.source_url})\n\n"
        else:
            md += "- 本周无重大事件\n\n"

        # 风险预警
        md += "---\n\n## 【风险与机会预警】\n\n"
        risk_items = [
            item for item in items
            if item.importance >= 4 and item.subsector_type in ["政策变化", "关键企业动态"]
        ]
        if risk_items:
            for item in risk_items[:3]:
                md += f"⚠️ **{item.supply_chain} - {item.subsector_type}**\n"
                md += f"   {item.title}\n\n"
        else:
            md += "本周无特别风险预警\n\n"

        # 按产业链结构生成
        sorted_chains = sorted(
            self.supply_chain_config.items(),
            key=lambda x: x[1].get('order', 999)
        )

        for chain_key, chain_config in sorted_chains:
            chain_name = chain_config.get('display_name', chain_key)
            chain_items = [
                item for item in items
                if item.supply_chain == chain_name
            ]

            if not chain_items:
                continue

            md += f"---\n\n## {chain_config.get('order', '')}. {chain_name}\n\n"
            md += f"*{chain_config.get('description', '')}*\n\n"

            # 按二级分类组织
            subsector_types = [
                "政策变化",
                "关键企业动态",
                "研发动态",
                "市场动态",
                "投融资"
            ]

            for subsector_type in subsector_types:
                subsector_items = [
                    item for item in chain_items
                    if item.subsector_type == subsector_type
                ]

                if not subsector_items:
                    continue

                # 根据类型选择图标
                icons = {
                    "政策变化": "📋",
                    "关键企业动态": "🏢",
                    "研发动态": "🔬",
                    "市场动态": "📊",
                    "投融资": "💰"
                }
                icon = icons.get(subsector_type, "•")

                md += f"### {icon} {subsector_type}\n\n"

                # 按细分环节进一步分组
                segment_groups = defaultdict(list)
                for item in subsector_items:
                    segment = item.supply_chain_segment or "其他"
                    segment_groups[segment].append(item)

                for segment, segment_items in sorted(segment_groups.items()):
                    if segment != "其他":
                        md += f"**{segment}**\n\n"

                    for item in segment_items:
                        # 按重要性显示
                        importance_display = "⭐" * item.importance
                        md += f"- **{item.title}** {importance_display}\n"
                        md += f"  - {item.one_line_insight or item.summary_zh[:150]}\n"

                        # 公司信息
                        if item.companies_mentioned:
                            companies_str = ", ".join(item.companies_mentioned)
                            md += f"  - 涉及企业: {companies_str}\n"

                        # 来源信息
                        md += f"  - 来源: {item.source_name}\n\n"

                    if segment != "其他":
                        md += "\n"

        # 数据概览
        md += "---\n\n## 数据概览\n\n"
        md += f"- 本周采集情报: **{len(items)}** 条\n"
        md += f"- 决策价值条目: **{len(decision_items)}** 条\n"
        md += f"- 涉及产业链: **{len(set(i.supply_chain for i in items if i.supply_chain))}** 条\n\n"

        if stats.get('importance'):
            md += "### 重要性分布\n"
            for importance, count in sorted(stats['importance'].items()):
                md += f"- {importance}: {count}条\n"
            md += "\n"

        # 监控重点
        md += "---\n\n## 下周监控重点\n\n"

        # 按产业链统计活跃度
        chain_activity = defaultdict(int)
        for item in items:
            if item.supply_chain:
                chain_activity[item.supply_chain] += 1

        top_chains = sorted(chain_activity.items(), key=lambda x: x[1], reverse=True)[:3]
        if top_chains:
            md += "### 活跃产业链\n"
            for chain, count in top_chains:
                md += f"- **{chain}**: 本周{count}条动态\n"
            md += "\n"

        # 重点企业
        company_activity = defaultdict(int)
        for item in items:
            for company in item.companies_mentioned:
                company_activity[company] += 1

        top_companies = sorted(company_activity.items(), key=lambda x: x[1], reverse=True)[:5]
        if top_companies:
            md += "### 重点关注企业\n"
            for company, count in top_companies:
                md += f"- **{company}**: {count}条动态\n"
            md += "\n"

        # 全部情报条目（重要性>=3，按上中下游分组）
        md += "---\n\n## 【全部情报条目】（重要性≥3分，按产业链位置分组）\n\n"

        all_items_3plus = [item for item in items if item.importance >= 3]
        all_items_3plus = sorted(all_items_3plus, key=lambda x: (x.importance, x.created_at), reverse=True)

        if all_items_3plus:
            # 按上中下游分组
            grouped_items = self._group_items_by_upstream_midstream_downstream(all_items_3plus)

            total_count = len(all_items_3plus)
            md += f"共 {total_count} 条情报\n\n"

            # 定义顺序
            position_order = ["上游", "中游", "下游", "其他"]
            position_names = {
                "上游": "⬆️ 上游（芯片/器件）",
                "中游": "➡️ 中游（设备/系统）",
                "下游": "⬇️ 下游（终端/运营）",
                "其他": "📦 其他"
            }

            for position in position_order:
                items_in_position = grouped_items.get(position, [])
                if not items_in_position:
                    continue

                md += f"### {position_names.get(position, position)}\n\n"

                # 按重要性排序
                items_in_position = sorted(
                    items_in_position,
                    key=lambda x: (x.importance, x.created_at),
                    reverse=True
                )

                for i, item in enumerate(items_in_position, 1):
                    # 显示产业链信息
                    chain_info = ""
                    if item.supply_chain:
                        chain_info = f"[{item.supply_chain}]"

                    md += f"**{i}. {item.title}** {chain_info} (重要度: {'⭐' * item.importance})\n"
                    md += f"   - 一句话洞察: {item.one_line_insight or item.summary_zh[:150]}\n"
                    md += f"   - 分类: {item.category.value if item.category else '未分类'} | 来源: {item.source_name}\n"
                    md += f"   - 链接: [{item.source_url}]({item.source_url})\n\n"

                md += "\n"
        else:
            md += "无\n\n"

        md += "---\n\n*本报告由CT产业情报Agent自动生成*\n"
        md += f"*生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n"

        return md

    def generate_supply_chain_html(
        self,
        items: List[IntelItem],
        issue_no: int,
        date_range: str,
        stats: Dict[str, Any]
    ) -> str:
        """按产业链结构生成HTML报告"""

        # 将Markdown转换为HTML
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>通信设备产业情报周报 - 第{issue_no}期</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Microsoft YaHei', sans-serif; line-height: 1.8; max-width: 1000px; margin: 0 auto; padding: 20px; color: #333; }}
        h1 {{ color: #1a73e8; border-bottom: 3px solid #1a73e8; padding-bottom: 10px; }}
        h2 {{ color: #2c5aa0; margin-top: 30px; border-left: 5px solid #2c5aa0; padding-left: 15px; }}
        h3 {{ color: #555; margin-top: 20px; }}
        h4 {{ color: #666; margin-top: 15px; font-weight: 600; }}
        .date-range {{ color: #666; font-size: 14px; margin: 10px 0; }}
        .highlight {{ background: #e8f4ff; padding: 15px; border-radius: 5px; margin: 15px 0; border-left: 4px solid #1a73e8; }}
        .item {{ margin: 12px 0; padding: 10px; background: #f8f9fa; border-radius: 5px; border-left: 3px solid #ddd; }}
        .item-title {{ font-weight: bold; color: #1a73e8; }}
        .item-meta {{ color: #666; font-size: 13px; margin-top: 5px; }}
        .stars {{ color: #ff6b6b; font-weight: bold; }}
        .subsector {{ margin: 15px 0; padding: 10px 0; border-left: 2px solid #eee; padding-left: 15px; }}
        table {{ border-collapse: collapse; width: 100%; margin: 15px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 10px; text-align: left; }}
        th {{ background: #f2f2f2; color: #333; font-weight: 600; }}
        a {{ color: #1a73e8; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
        .footer {{ margin-top: 40px; padding-top: 20px; border-top: 1px solid #ddd; color: #999; font-size: 12px; text-align: center; }}
        .section {{ page-break-inside: avoid; }}
        .icon {{ font-size: 20px; margin-right: 5px; }}
    </style>
</head>
<body>
    <h1>通信设备产业情报周报 | 第{issue_no}期</h1>
    <p class="date-range">{date_range}</p>

    {self._summary_html(items, stats)}

    <h2>【本周核心决策洞察】</h2>
"""

        # 核心决策洞察：所有 importance>=5 的条目
        decision_items = [
            item for item in items
            if item.importance >= 5
        ]
        decision_items = sorted(
            decision_items,
            key=lambda x: x.importance,
            reverse=True
        )  # 无数量限制

        if decision_items:
            html += '<div class="highlight">'
            for i, item in enumerate(decision_items, 1):
                html += f'<div class="item">'
                html += f'<div class="item-title">{i}. {item.title}</div>'
                html += f'<div>{item.one_line_insight or item.summary_zh[:100]}</div>'
                html += f'<div class="item-meta">来源: {item.source_name}</div>'
                html += '</div>'
            html += '</div>'
        else:
            html += '<p>本周无重大事件</p>'

        # 按产业链组织
        sorted_chains = sorted(
            self.supply_chain_config.items(),
            key=lambda x: x[1].get('order', 999)
        )

        for chain_key, chain_config in sorted_chains:
            chain_name = chain_config.get('display_name', chain_key)
            chain_items = [
                item for item in items
                if item.supply_chain == chain_name
            ]

            if not chain_items:
                continue

            html += f'<div class="section">'
            html += f'<h2>{chain_config.get("order", "")}. {chain_name}</h2>'
            html += f'<p style="color: #666; font-size: 14px;">{chain_config.get("description", "")}</p>'

            # 按二级分类
            subsector_types = [
                "政策变化",
                "关键企业动态",
                "研发动态",
                "市场动态",
                "投融资"
            ]

            for subsector_type in subsector_types:
                subsector_items = [
                    item for item in chain_items
                    if item.subsector_type == subsector_type
                ]

                if not subsector_items:
                    continue

                icons = {
                    "政策变化": "📋",
                    "关键企业动态": "🏢",
                    "研发动态": "🔬",
                    "市场动态": "📊",
                    "投融资": "💰"
                }
                icon = icons.get(subsector_type, "•")

                html += f'<h3><span class="icon">{icon}</span>{subsector_type}</h3>'

                for item in subsector_items:
                    stars = "⭐" * item.importance
                    html += f'<div class="item">'
                    html += f'<div class="item-title">{item.title} <span class="stars">{stars}</span></div>'
                    html += f'<div>{item.one_line_insight or item.summary_zh[:150]}</div>'
                    if item.companies_mentioned:
                        companies = ", ".join(item.companies_mentioned)
                        html += f'<div class="item-meta">涉及企业: {companies}</div>'
                    html += f'<div class="item-meta">来源: {item.source_name}</div>'
                    html += '</div>'

            html += '</div>'

        # 数据统计
        html += '<h2>数据统计</h2>'
        html += '<table>'
        html += '<tr><th>指标</th><th>数值</th></tr>'
        html += f'<tr><td>本周采集情报</td><td>{len(items)}</td></tr>'
        html += f'<tr><td>决策价值条目</td><td>{len(decision_items)}</td></tr>'
        html += f'<tr><td>涉及产业链</td><td>{len(set(i.supply_chain for i in items if i.supply_chain))}</td></tr>'
        html += '</table>'

        # 全部情报条目（重要性>=3，按上中下游分组）
        html += '<h2>【全部情报条目】（重要性≥3分，按产业链位置分组）</h2>'

        all_items_3plus = [item for item in items if item.importance >= 3]
        all_items_3plus = sorted(all_items_3plus, key=lambda x: (x.importance, x.created_at), reverse=True)

        if all_items_3plus:
            # 按上中下游分组
            grouped_items = self._group_items_by_upstream_midstream_downstream(all_items_3plus)

            total_count = len(all_items_3plus)
            html += f'<p>共 {total_count} 条情报</p>'

            # 定义顺序和样式
            position_order = ["上游", "中游", "下游", "其他"]
            position_names = {
                "上游": "⬆️ 上游（芯片/器件）",
                "中游": "➡️ 中游（设备/系统）",
                "下游": "⬇️ 下游（终端/运营）",
                "其他": "📦 其他"
            }
            position_colors = {
                "上游": "#4CAF50",   # 绿色
                "中游": "#2196F3",   # 蓝色
                "下游": "#FF9800",   # 橙色
                "其他": "#9E9E9E"    # 灰色
            }

            for position in position_order:
                items_in_position = grouped_items.get(position, [])
                if not items_in_position:
                    continue

                color = position_colors.get(position, "#666")
                html += f'<div style="margin: 20px 0; padding: 15px; border-left: 4px solid {color}; background: #f9f9f9;">'
                html += f'<h3 style="margin: 0 0 15px 0; color: {color};">{position_names.get(position, position)} ({len(items_in_position)}条)</h3>'

                # 按重要性排序
                items_in_position = sorted(
                    items_in_position,
                    key=lambda x: (x.importance, x.created_at),
                    reverse=True
                )

                html += '<table>'
                html += '<tr><th>#</th><th>标题</th><th>产业链</th><th>重要度</th><th>分类</th><th>来源</th><th>链接</th></tr>'
                for i, item in enumerate(items_in_position, 1):
                    chain = item.supply_chain or "-"
                    html += f'<tr>'
                    html += f'<td>{i}</td>'
                    html += f'<td style="max-width: 300px; overflow: hidden; text-overflow: ellipsis;">{item.title}</td>'
                    html += f'<td style="font-size: 12px; color: #666;">{chain}</td>'
                    html += f'<td>{"⭐" * item.importance}</td>'
                    html += f'<td>{item.category.value if item.category else "未分类"}</td>'
                    html += f'<td>{item.source_name}</td>'
                    html += f'<td><a href="{item.source_url}" target="_blank">查看原文</a></td>'
                    html += f'</tr>'
                html += '</table>'
                html += '</div>'
        else:
            html += '<p>无</p>'

        html += f'''
    <div class="footer">
        <p>本报告由CT产业情报Agent自动生成</p>
        <p>生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
</body>
</html>'''

        return html
