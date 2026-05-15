"""
Public trial report service.

This module builds a lightweight preview report from the already generated
weekly intelligence database. It is designed for website trial pages where
visitors choose a recent week and one or more technology directions, then see
a limited preview plus a contact call-to-action.
"""
from __future__ import annotations

import html
import os
import sqlite3
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional


PROJECT_ROOT = Path(__file__).resolve().parent
DB_PATH = PROJECT_ROOT / "data" / "intel.db"

DEFAULT_CONTACT = {
    "name": os.getenv("TRIAL__CONTACT_NAME", "薄云咨询产业情报团队"),
    "phone": os.getenv("TRIAL__CONTACT_PHONE", "请在 .env 中填写 TRIAL__CONTACT_PHONE"),
    "wechat": os.getenv("TRIAL__CONTACT_WECHAT", "请在 .env 中填写 TRIAL__CONTACT_WECHAT"),
    "email": os.getenv("TRIAL__CONTACT_EMAIL", "请在 .env 中填写 TRIAL__CONTACT_EMAIL"),
}


@dataclass
class TrialWeek:
    issue_no: int
    date_start: str
    date_end: str
    total_items: int

    @property
    def label(self) -> str:
        return f"第{self.issue_no}期 | {self.date_start[:10]} 至 {self.date_end[:10]}"


def _connect(db_path: Path = DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn


def _safe_json_list(value: Optional[str]) -> List[str]:
    if not value:
        return []
    try:
        import json

        parsed = json.loads(value)
        if isinstance(parsed, list):
            return [str(item) for item in parsed if item]
    except Exception:
        return []
    return []


def _direction_for_row(row: sqlite3.Row) -> str:
    supply_chain = (row["supply_chain"] or "").strip()
    tech_domain = (row["tech_domain"] or "").strip()
    if supply_chain and supply_chain != "其他":
        return supply_chain
    if tech_domain and tech_domain != "其他":
        return tech_domain
    return "综合技术动态"


def _item_date(row: sqlite3.Row) -> str:
    raw = row["pub_date"] or row["created_at"] or ""
    return raw[:10]


def get_recent_weeks(limit: int = 3, db_path: Path = DB_PATH) -> List[TrialWeek]:
    """Return the latest weekly reports available for public trial selection."""
    if not db_path.exists():
        return []

    with _connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT issue_no, date_start, date_end, total_items
            FROM weekly_reports
            ORDER BY issue_no DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

    return [
        TrialWeek(
            issue_no=int(row["issue_no"]),
            date_start=row["date_start"],
            date_end=row["date_end"],
            total_items=int(row["total_items"] or 0),
        )
        for row in rows
    ]


def get_week(issue_no: int, db_path: Path = DB_PATH) -> Optional[TrialWeek]:
    if not db_path.exists():
        return None

    with _connect(db_path) as conn:
        row = conn.execute(
            """
            SELECT issue_no, date_start, date_end, total_items
            FROM weekly_reports
            WHERE issue_no = ?
            """,
            (issue_no,),
        ).fetchone()

    if not row:
        return None
    return TrialWeek(
        issue_no=int(row["issue_no"]),
        date_start=row["date_start"],
        date_end=row["date_end"],
        total_items=int(row["total_items"] or 0),
    )


def _rows_for_week(week: TrialWeek, db_path: Path = DB_PATH) -> List[sqlite3.Row]:
    with _connect(db_path) as conn:
        return conn.execute(
            """
            SELECT *
            FROM intel_items
            WHERE source_type != 'vvihot'
              AND is_news = 1
              AND (
                    (pub_date >= ? AND pub_date <= ?)
                 OR (pub_date IS NULL AND created_at >= ? AND created_at <= ?)
              )
            ORDER BY importance DESC, decision_value DESC, COALESCE(pub_date, created_at) DESC
            """,
            (week.date_start, week.date_end, week.date_start, week.date_end),
        ).fetchall()


def get_available_directions(issue_no: Optional[int] = None, db_path: Path = DB_PATH) -> List[str]:
    """Return selectable technology directions for one week or the latest weeks."""
    weeks = [get_week(issue_no, db_path)] if issue_no else get_recent_weeks(3, db_path)
    directions: Dict[str, int] = {}

    for week in [w for w in weeks if w]:
        for row in _rows_for_week(week, db_path):
            direction = _direction_for_row(row)
            directions[direction] = directions.get(direction, 0) + 1

    return [
        name
        for name, _count in sorted(
            directions.items(),
            key=lambda item: (item[0] == "综合技术动态", -item[1], item[0]),
        )
    ]


def _select_items(
    rows: Iterable[sqlite3.Row],
    directions: List[str],
    max_total: int,
    max_per_direction: int,
) -> Dict[str, List[sqlite3.Row]]:
    selected: Dict[str, List[sqlite3.Row]] = {direction: [] for direction in directions}
    fallback: Dict[str, List[sqlite3.Row]] = {}

    for row in rows:
        direction = _direction_for_row(row)
        fallback.setdefault(direction, []).append(row)
        if direction in selected and len(selected[direction]) < max_per_direction:
            selected[direction].append(row)

    flattened_count = sum(len(items) for items in selected.values())
    if flattened_count == 0:
        for direction, items in fallback.items():
            selected[direction] = items[:max_per_direction]
            flattened_count += len(selected[direction])
            if flattened_count >= max_total:
                break

    trimmed: Dict[str, List[sqlite3.Row]] = {}
    remaining = max_total
    for direction, items in selected.items():
        if remaining <= 0:
            break
        keep = items[:remaining]
        if keep:
            trimmed[direction] = keep
            remaining -= len(keep)
    return trimmed


def _build_summary(grouped_items: Dict[str, List[sqlite3.Row]]) -> str:
    total = sum(len(items) for items in grouped_items.values())
    directions = "、".join(grouped_items.keys())
    important = sum(
        1
        for items in grouped_items.values()
        for item in items
        if int(item["importance"] or 0) >= 4
    )
    return (
        f"本试用报告基于已归档的产业情报库生成，覆盖 {directions} 等方向，"
        f"当前预览展示 {total} 条代表性情报，其中重要度 4 分及以上 {important} 条。"
        "完整版本可进一步提供全量来源、趋势研判、竞争动作、专利线索和定制监测建议。"
    )


def build_trial_report(
    issue_no: int,
    directions: List[str],
    max_total: int = 8,
    max_per_direction: int = 3,
    db_path: Path = DB_PATH,
    contact: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    """Build a limited trial report from stored weekly intelligence data."""
    week = get_week(issue_no, db_path)
    if not week:
        return {
            "ok": False,
            "message": "未找到对应周报，请先完成采集并生成周报。",
            "markdown": "",
            "html": "",
            "items_count": 0,
        }

    all_directions = get_available_directions(issue_no, db_path)
    chosen = [d for d in directions if d in all_directions]
    if not chosen:
        chosen = all_directions[:3]

    rows = _rows_for_week(week, db_path)
    grouped = _select_items(rows, chosen, max_total=max_total, max_per_direction=max_per_direction)
    contact_info = contact or DEFAULT_CONTACT

    md_lines = [
        f"# 产业情报试用报告",
        "",
        f"**报告周期**：{week.date_start[:10]} 至 {week.date_end[:10]}",
        f"**选择方向**：{'、'.join(grouped.keys()) if grouped else '暂无匹配方向'}",
        "",
        "## 本期试用摘要",
        "",
        _build_summary(grouped) if grouped else "当前选择条件下暂无可展示的试用情报。",
        "",
        "## 重点情报预览",
        "",
    ]

    html_parts = [
        "<article class='trial-report'>",
        "<h1>产业情报试用报告</h1>",
        f"<p><strong>报告周期：</strong>{html.escape(week.date_start[:10])} 至 {html.escape(week.date_end[:10])}</p>",
        f"<p><strong>选择方向：</strong>{html.escape('、'.join(grouped.keys()) if grouped else '暂无匹配方向')}</p>",
        "<h2>本期试用摘要</h2>",
        f"<p>{html.escape(_build_summary(grouped) if grouped else '当前选择条件下暂无可展示的试用情报。')}</p>",
        "<h2>重点情报预览</h2>",
    ]

    for direction, items in grouped.items():
        md_lines.extend([f"### {direction}", ""])
        html_parts.append(f"<h3>{html.escape(direction)}</h3>")
        for index, row in enumerate(items, 1):
            companies = _safe_json_list(row["companies"])
            summary = row["one_line_insight"] or row["summary_zh"] or row["content"] or ""
            summary = summary.strip().replace("\n", " ")[:220]
            source = row["source_name"] or row["source_type"] or "公开来源"
            date_text = _item_date(row)

            md_lines.extend(
                [
                    f"{index}. **{row['title']}**",
                    f"   - 摘要：{summary}",
                    f"   - 来源：{source} | 日期：{date_text} | 重要度：{row['importance']}",
                ]
            )
            if companies:
                md_lines.append(f"   - 涉及企业：{'、'.join(companies[:5])}")
            md_lines.append("")

            html_parts.append("<section class='trial-item'>")
            html_parts.append(f"<h4>{html.escape(str(index) + '. ' + row['title'])}</h4>")
            html_parts.append(f"<p>{html.escape(summary)}</p>")
            html_parts.append(
                "<p class='trial-meta'>"
                f"来源：{html.escape(source)} | 日期：{html.escape(date_text)} | 重要度：{html.escape(str(row['importance']))}"
                "</p>"
            )
            if companies:
                html_parts.append(f"<p class='trial-meta'>涉及企业：{html.escape('、'.join(companies[:5]))}</p>")
            html_parts.append("</section>")

    md_lines.extend(
        [
            "---",
            "",
            "## 查看完整报告与定制监测",
            "",
            "当前页面仅展示试用版内容。完整版本可包含全量情报、原文链接、深度分析、专利线索、竞品动作、企业微信/邮箱推送和定制技术方向。",
            "",
            f"- 联系人：{contact_info.get('name', '')}",
            f"- 电话：{contact_info.get('phone', '')}",
            f"- 微信：{contact_info.get('wechat', '')}",
            f"- 邮箱：{contact_info.get('email', '')}",
        ]
    )

    html_parts.extend(
        [
            "<hr>",
            "<h2>查看完整报告与定制监测</h2>",
            "<p>当前页面仅展示试用版内容。完整版本可包含全量情报、原文链接、深度分析、专利线索、竞品动作、企业微信/邮箱推送和定制技术方向。</p>",
            "<ul>",
            f"<li>联系人：{html.escape(contact_info.get('name', ''))}</li>",
            f"<li>电话：{html.escape(contact_info.get('phone', ''))}</li>",
            f"<li>微信：{html.escape(contact_info.get('wechat', ''))}</li>",
            f"<li>邮箱：{html.escape(contact_info.get('email', ''))}</li>",
            "</ul>",
            "</article>",
        ]
    )

    return {
        "ok": True,
        "message": "试用报告生成成功",
        "week": week,
        "directions": list(grouped.keys()),
        "markdown": "\n".join(md_lines),
        "html": "\n".join(html_parts),
        "items_count": sum(len(items) for items in grouped.values()),
    }
