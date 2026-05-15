"""
Website trial report app.

Run:
    streamlit run trial_demo_app.py --server.port 8502

This page does not trigger live crawling or LLM analysis. It reads from the
existing weekly intelligence database and returns a limited public preview.
"""
from __future__ import annotations

import streamlit as st

from trial_report_service import (
    DEFAULT_CONTACT,
    build_trial_report,
    get_available_directions,
    get_recent_weeks,
)


st.set_page_config(
    page_title="产业情报试用报告",
    page_icon="AI",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
    .main .block-container { max-width: 1080px; padding-top: 32px; }
    .trial-header { border-bottom: 1px solid #d9e2ec; padding-bottom: 18px; margin-bottom: 22px; }
    .trial-header h1 { color: #102a43; margin-bottom: 8px; }
    .trial-header p { color: #52616b; margin: 0; font-size: 16px; }
    .trial-report h1 { color: #102a43; }
    .trial-report h2 { margin-top: 28px; color: #1f4e79; }
    .trial-report h3 { margin-top: 22px; color: #334e68; }
    .trial-item { border-left: 4px solid #2f80ed; background: #f7fbff; padding: 12px 14px; margin: 10px 0; }
    .trial-item h4 { margin: 0 0 8px 0; color: #102a43; }
    .trial-meta { color: #627d98; font-size: 13px; margin: 4px 0; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="trial-header">
      <h1>产业情报试用报告</h1>
      <p>选择最近三期周报和技术方向，系统将基于已归档的产业情报库生成试用版预览。</p>
    </div>
    """,
    unsafe_allow_html=True,
)

weeks = get_recent_weeks(3)
if not weeks:
    st.warning("暂无可展示的周报数据。请先在主系统完成采集、AI分析和周报生成。")
    st.stop()

week_labels = {week.label: week.issue_no for week in weeks}
col_week, col_limit = st.columns([3, 1])

with col_week:
    selected_week_label = st.selectbox("报告周期", list(week_labels.keys()))
selected_issue_no = week_labels[selected_week_label]

directions = get_available_directions(selected_issue_no)
default_directions = directions[:3]

with col_limit:
    max_total = st.selectbox("预览条数", [6, 8, 10, 12], index=1)

selected_directions = st.multiselect(
    "技术方向",
    directions,
    default=default_directions,
    help="试用版会按所选方向展示部分代表性内容，完整报告可支持定制方向和关键词。",
)

if st.button("生成试用报告", type="primary", use_container_width=True):
    st.session_state["trial_report"] = build_trial_report(
        selected_issue_no,
        selected_directions,
        max_total=max_total,
        max_per_direction=3,
    )

if "trial_report" not in st.session_state:
    st.info("请选择报告周期和技术方向，然后点击生成试用报告。")
    st.stop()

result = st.session_state["trial_report"]
if not result["ok"]:
    st.error(result["message"])
    st.stop()

st.success(f"已生成试用版预览，共展示 {result['items_count']} 条代表性情报。")
st.components.v1.html(result["html"], height=900, scrolling=True)

with st.expander("联系方式配置说明"):
    st.markdown(
        f"""
        当前联系方式来自环境变量，未配置时会显示默认提示。

        - `TRIAL__CONTACT_NAME`：{DEFAULT_CONTACT["name"]}
        - `TRIAL__CONTACT_PHONE`：{DEFAULT_CONTACT["phone"]}
        - `TRIAL__CONTACT_WECHAT`：{DEFAULT_CONTACT["wechat"]}
        - `TRIAL__CONTACT_EMAIL`：{DEFAULT_CONTACT["email"]}
        """
    )
