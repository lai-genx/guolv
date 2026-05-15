"""
CT产业情报Agent - Web界面
启动方式: streamlit run web_app.py
"""
import importlib
import subprocess
import sys

# 依赖检测与自动安装
REQUIRED_PACKAGES = {
    "httpx": "httpx",
    "bs4": "beautifulsoup4",
    "loguru": "loguru",
    "pydantic_settings": "pydantic-settings",
    "apscheduler": "apscheduler",
    "chromadb": "chromadb",
    "sentence_transformers": "sentence-transformers",
    "plotly": "plotly",
    "pandas": "pandas",
    "yaml": "PyYAML",
    "lxml": "lxml",
}

missing = []
for mod, pkg in REQUIRED_PACKAGES.items():
    try:
        importlib.import_module(mod)
    except ImportError:
        missing.append(pkg)

if missing:
    import streamlit as st
    st.warning(f"检测到缺少依赖: {', '.join(missing)}")
    if st.button("一键安装缺失依赖"):
        with st.spinner("正在安装..."):
            subprocess.check_call([sys.executable, "-m", "pip", "install", *missing])
        st.success("安装完成，请刷新页面")
    st.stop()

import streamlit as st
import sqlite3
import json
import os
import asyncio
import threading
import queue
from datetime import datetime, timedelta
from pathlib import Path
from contextlib import contextmanager

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from config import settings

# ============================================================
# 配置
# ============================================================
PROJECT_ROOT = Path(__file__).parent
DB_PATH = PROJECT_ROOT / "data" / "intel.db"
REPORTS_DIR = PROJECT_ROOT / "data" / "reports"
ENV_PATH = PROJECT_ROOT / ".env"

st.set_page_config(
    page_title="CT产业情报Agent",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# 数据库工具
# ============================================================
@contextmanager
def get_db():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def query_df(sql, params=None):
    with get_db() as conn:
        return pd.read_sql_query(sql, conn, params=params)


def query_one(sql, params=None):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(sql, params or [])
        row = cur.fetchone()
        return dict(row) if row else None


def query_all(sql, params=None):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(sql, params or [])
        return [dict(r) for r in cur.fetchall()]

# ============================================================
# 侧边栏导航
# ============================================================
page = st.sidebar.radio(
    "导航",
    ["📊 仪表盘", "📋 报告列表", "🔍 情报库", "🚀 采集中心", "⚙️ 设置"],
    label_visibility="collapsed"
)

# ============================================================
# 页面1: 仪表盘
# ============================================================
if page == "📊 仪表盘":
    st.title("📊 CT产业情报仪表盘")

    # 概览指标
    try:
        total_items = query_one("SELECT COUNT(*) as c FROM intel_items")["c"]
        total_reports = query_one("SELECT COUNT(*) as c FROM weekly_reports")["c"]
        high_importance = query_one("SELECT COUNT(*) as c FROM intel_items WHERE importance >= 4")["c"]
        decision_value = query_one("SELECT COUNT(*) as c FROM intel_items WHERE decision_value = 1")["c"]
    except Exception:
        total_items = total_reports = high_importance = decision_value = 0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("情报总数", f"{total_items} 条")
    col2.metric("周报期数", f"{total_reports} 期")
    col3.metric("高重要度(≥4)", f"{high_importance} 条")
    col4.metric("决策价值", f"{decision_value} 条")

    st.divider()

    # 最新周报摘要
    st.subheader("最新周报")
    try:
        latest = query_one("SELECT * FROM weekly_reports ORDER BY issue_no DESC LIMIT 1")
        if latest:
            date_start = latest["date_start"][:10] if latest["date_start"] else ""
            date_end = latest["date_end"][:10] if latest["date_end"] else ""
            st.markdown(f"**第{latest['issue_no']}期** | {date_start} ~ {date_end} | 共 {latest['total_items']} 条情报")
            if latest["report_md"]:
                # 只显示前1500字符作为摘要
                preview = latest["report_md"][:1500]
                st.markdown(preview)
                if len(latest["report_md"]) > 1500:
                    st.info("👆 完整报告请到「报告列表」查看")
        else:
            st.warning("暂无周报数据")
    except Exception as e:
        st.error(f"读取周报失败: {e}")

    st.divider()

    # 趋势图表
    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("各期情报数量趋势")
        try:
            reports_df = query_df("SELECT issue_no, total_items, date_start FROM weekly_reports ORDER BY issue_no")
            if not reports_df.empty:
                fig = px.bar(reports_df, x="issue_no", y="total_items",
                           labels={"issue_no": "期号", "total_items": "情报条数"},
                           color="total_items", color_continuous_scale="Blues")
                fig.update_layout(showlegend=False, height=300)
                st.plotly_chart(fig, use_container_width=True)
        except Exception:
            st.info("暂无数据")

    with col_right:
        st.subheader("情报分类分布")
        try:
            cat_df = query_df("SELECT category, COUNT(*) as cnt FROM intel_items GROUP BY category ORDER BY cnt DESC")
            if not cat_df.empty:
                fig = px.pie(cat_df, values="cnt", names="category", hole=0.4)
                fig.update_layout(height=300)
                st.plotly_chart(fig, use_container_width=True)
        except Exception:
            st.info("暂无数据")

    # 重要度分布
    st.subheader("重要度分布")
    try:
        imp_df = query_df("SELECT importance, COUNT(*) as cnt FROM intel_items GROUP BY importance ORDER BY importance")
        if not imp_df.empty:
            fig = px.bar(imp_df, x="importance", y="cnt",
                       labels={"importance": "重要度", "cnt": "条数"},
                       color="cnt", color_continuous_scale="OrRd")
            fig.update_layout(showlegend=False, height=280)
            st.plotly_chart(fig, use_container_width=True)
    except Exception:
        st.info("暂无数据")

# ============================================================
# 页面2: 报告列表
# ============================================================
elif page == "📋 报告列表":
    st.title("📋 周报列表")

    try:
        reports = query_all("SELECT * FROM weekly_reports ORDER BY issue_no DESC")
    except Exception:
        reports = []

    if not reports:
        st.warning("暂无周报数据")
    else:
        for r in reports:
            date_start = r["date_start"][:10] if r["date_start"] else ""
            date_end = r["date_end"][:10] if r["date_end"] else ""
            with st.expander(f"第{r['issue_no']}期 | {date_start} ~ {date_end} | {r['total_items']}条情报"):
                # 标签
                tags = []
                if r.get("sent_email"):
                    tags.append("✉️ 已邮件发送")
                if r.get("sent_wechat"):
                    tags.append("💬 已企微发送")
                if tags:
                    st.markdown("  ".join(tags))

                # 分布信息
                if r.get("importance_distribution"):
                    st.markdown(f"**重要度分布**: {r['importance_distribution']}")
                if r.get("category_distribution"):
                    st.markdown(f"**分类分布**: {r['category_distribution']}")

                # Tab切换 md/html
                tab_md, tab_html = st.tabs(["Markdown", "HTML"])
                with tab_md:
                    if r.get("report_md"):
                        st.markdown(r["report_md"])
                    else:
                        st.info("无Markdown内容")
                with tab_html:
                    if r.get("report_html"):
                        st.components.v1.html(r["report_html"], height=600, scrolling=True)
                    else:
                        st.info("无HTML内容")

# ============================================================
# 页面3: 情报库
# ============================================================
elif page == "🔍 情报库":
    st.title("🔍 情报库")

    # 筛选栏
    col_f1, col_f2, col_f3, col_f4 = st.columns([2, 2, 2, 1])

    with col_f1:
        categories = query_all("SELECT DISTINCT category FROM intel_items WHERE category IS NOT NULL ORDER BY category")
        cat_options = ["全部"] + [c["category"] for c in categories]
        selected_cat = st.selectbox("分类", cat_options)

    with col_f2:
        tech_domains = query_all("SELECT DISTINCT tech_domain FROM intel_items WHERE tech_domain IS NOT NULL ORDER BY tech_domain")
        td_options = ["全部"] + [t["tech_domain"] for t in tech_domains]
        selected_td = st.selectbox("技术领域", td_options)

    with col_f3:
        imp_options = ["全部", "5-最重要", "4-重要", "3-中等", "2-一般", "1-低"]
        selected_imp = st.selectbox("重要度", imp_options)

    with col_f4:
        only_decision = st.checkbox("仅决策价值")

    # 构建查询
    where_clauses = []
    params = []

    if selected_cat != "全部":
        where_clauses.append("category = ?")
        params.append(selected_cat)
    if selected_td != "全部":
        where_clauses.append("tech_domain = ?")
        params.append(selected_td)
    if selected_imp != "全部":
        imp_val = int(selected_imp[0])
        where_clauses.append("importance = ?")
        params.append(imp_val)
    if only_decision:
        where_clauses.append("decision_value = 1")

    where_sql = (" WHERE " + " AND ".join(where_clauses)) if where_clauses else ""

    # 总数
    try:
        total = query_one(f"SELECT COUNT(*) as c FROM intel_items{where_sql}", params)["c"]
    except Exception:
        total = 0

    st.caption(f"共 {total} 条")

    # 分页
    page_size = 20
    current_page = st.number_input("页码", min_value=1, max_value=max(1, (total + page_size - 1) // page_size), value=1)
    offset = (current_page - 1) * page_size

    try:
        items = query_all(
            f"SELECT id, title, source_url, source_name, category, tech_domain, importance, decision_value, "
            f"summary_zh, one_line_insight, companies, created_at "
            f"FROM intel_items{where_sql} ORDER BY created_at DESC LIMIT ? OFFSET ?",
            params + [page_size, offset]
        )
    except Exception:
        items = []

    for item in items:
        importance_emoji = "🔴" if item["importance"] >= 4 else ("🟡" if item["importance"] == 3 else "⚪")
        decision_badge = " ⭐决策价值" if item["decision_value"] else ""
        title = item["title"] or "(无标题)"
        with st.expander(f"{importance_emoji} [{item['importance']}] {title}{decision_badge}"):
            col_a, col_b = st.columns([3, 1])
            with col_a:
                if item.get("summary_zh"):
                    st.markdown(f"**摘要**: {item['summary_zh']}")
                if item.get("one_line_insight"):
                    st.markdown(f"**点评**: {item['one_line_insight']}")
                if item.get("source_url"):
                    st.markdown(f"**原文链接**: [{item['source_url'][:60]}{'...' if len(item['source_url'])>60 else ''}]({item['source_url']})")
            with col_b:
                st.markdown(f"分类: {item.get('category', '-')}")
                st.markdown(f"领域: {item.get('tech_domain', '-')}")
                st.markdown(f"来源: {item.get('source_name', '-')}")
                if item.get("companies"):
                    try:
                        comps = json.loads(item["companies"])
                        st.markdown(f"公司: {', '.join(comps[:5])}")
                    except Exception:
                        pass
                st.caption(item.get("created_at", "")[:16] if item.get("created_at") else "")

# ============================================================
# 页面4: 采集中心
# ============================================================
elif page == "🚀 采集中心":
    st.title("🚀 采集中心")

    st.markdown("""
    点击按钮启动采集任务。采集过程会实时显示进度信息。

    > 采集包括：RSS源采集 → 网站爬取 → AI分析分类 → 生成周报
    """)

    # 采集状态管理
    if "collect_running" not in st.session_state:
        st.session_state.collect_running = False
    if "collect_logs" not in st.session_state:
        st.session_state.collect_logs = []
    if "collect_result" not in st.session_state:
        st.session_state.collect_result = None

    col_btn1, col_btn2 = st.columns([1, 5])
    with col_btn1:
        if st.button("▶️ 开始采集", disabled=st.session_state.collect_running, type="primary"):
            st.session_state.collect_running = True
            st.session_state.collect_logs = []
            st.session_state.collect_result = None
            st.rerun()

    with col_btn2:
        if st.session_state.collect_running:
            st.info("采集中...")

    # 如果正在采集，执行采集逻辑
    if st.session_state.collect_running and not st.session_state.collect_result:
        log_placeholder = st.empty()
        progress_bar = st.progress(0, text="准备启动...")

        logs = []

        def add_log(msg):
            logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

        try:
            # 需要设置事件循环
            try:
                loop = asyncio.get_event_loop()
                if loop.is_closed():
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

            # Step 1: 初始化Agent
            add_log("🔧 初始化CT产业情报Agent...")
            progress_bar.progress(5, text="初始化Agent...")
            log_placeholder.code("\n".join(logs))

            # 动态导入项目模块
            import sys
            if str(PROJECT_ROOT) not in sys.path:
                sys.path.insert(0, str(PROJECT_ROOT))

            from main import TelecomIntelAgent
            agent = TelecomIntelAgent()

            add_log(f"✅ Agent初始化完成 - {len(agent.collectors)} 个采集器就绪")
            progress_bar.progress(10, text="Agent初始化完成")
            log_placeholder.code("\n".join(logs))

            # Step 2: 采集数据
            add_log("=" * 40)
            add_log("📡 开始数据采集...")
            progress_bar.progress(15, text="数据采集中...")
            log_placeholder.code("\n".join(logs))

            all_raw_items = []
            total_collectors = len(agent.collectors)

            for idx, collector in enumerate(agent.collectors):
                add_log(f"  🔍 启动采集器: {collector.source_type}")
                progress_pct = 15 + int((idx / total_collectors) * 40)
                progress_bar.progress(progress_pct, text=f"采集器 {collector.source_type} 运行中...")
                log_placeholder.code("\n".join(logs))

                try:
                    collector_timeout = 180
                    if collector.source_type == "web":
                        max_sites = settings.collector.web_max_sites
                        site_count = len(getattr(collector, "sites", []))
                        if max_sites and max_sites > 0:
                            site_count = min(site_count, max_sites)
                        collector_timeout = max(
                            180,
                            site_count * (settings.collector.web_per_site_timeout + 5) + 120
                        )
                        add_log(
                            f"     web将扫描 {site_count} 个官网，单站最长 {settings.collector.web_per_site_timeout} 秒，预计可能需要较长时间"
                        )
                        log_placeholder.code("\n".join(logs))
                    elif collector.source_type == "patent":
                        try:
                            query_count = len(collector._build_patent_queries())
                        except Exception:
                            query_count = settings.collector.patent_max_queries or 18
                        if settings.collector.patent_max_queries and settings.collector.patent_max_queries > 0:
                            query_count = min(query_count, settings.collector.patent_max_queries)
                        collector_timeout = max(
                            180,
                            query_count * (settings.collector.patent_per_query_timeout + 3) + 120
                        )
                        add_log(
                            f"     patent将执行 {query_count} 个查询，单查询最长 {settings.collector.patent_per_query_timeout} 秒"
                        )
                        log_placeholder.code("\n".join(logs))

                    result = loop.run_until_complete(
                        asyncio.wait_for(collector.collect(), timeout=collector_timeout)
                    )

                    if result.success:
                        all_raw_items.extend(result.items)
                        add_log(f"  ✅ {collector.source_type}: {result.message}")
                        add_log(f"     获取 {len(result.items)} 条原始数据")

                        # 显示部分采集到的标题
                        for i, item in enumerate(result.items[:5]):
                            add_log(f"     - {item.title[:60]}")
                        if len(result.items) > 5:
                            add_log(f"     ... 还有 {len(result.items) - 5} 条")
                    else:
                        add_log(f"  ❌ {collector.source_type}: {result.message}")
                except Exception as e:
                    add_log(f"  ❌ {collector.source_type} 异常: {e}")
                finally:
                    try:
                        loop.run_until_complete(collector.close())
                    except Exception:
                        pass

                log_placeholder.code("\n".join(logs))

            # 去重
            seen_urls = set()
            unique_items = []
            for item in all_raw_items:
                if item.url not in seen_urls:
                    seen_urls.add(item.url)
                    unique_items.append(item)

            add_log(f"📊 采集完成: 共 {len(all_raw_items)} 条, 去重后 {len(unique_items)} 条唯一数据")
            progress_bar.progress(55, text=f"采集完成，{len(unique_items)} 条数据")
            log_placeholder.code("\n".join(logs))

            # Step 3: AI分析
            add_log("=" * 40)
            add_log("🧠 开始AI分析...")
            progress_bar.progress(58, text="AI分析中...")
            log_placeholder.code("\n".join(logs))

            analyzed_items = []
            for i, raw_data in enumerate(unique_items, 1):
                if i % 3 == 0 or i == len(unique_items):
                    add_log(f"  [{i}/{len(unique_items)}] 分析: {raw_data.title[:50]}...")
                    progress_pct = 58 + int((i / len(unique_items)) * 30)
                    progress_bar.progress(progress_pct, text=f"AI分析 {i}/{len(unique_items)}...")
                    log_placeholder.code("\n".join(logs))

                try:
                    rag_context = ""
                    if agent.rag.is_initialized:
                        rag_context = agent.rag.get_context_for_analysis(
                            raw_data.title + " " + raw_data.summary
                        )
                    item = loop.run_until_complete(agent.analyzer.analyze_item(raw_data, rag_context))
                    if item:
                        analyzed_items.append(item)
                except Exception as e:
                    add_log(f"  ❌ 分析失败: {e}")

            add_log(f"✅ AI分析完成: 成功 {len(analyzed_items)} 条")
            log_placeholder.code("\n".join(logs))

            if not analyzed_items:
                add_log("❌ AI分析成功 0 条，已停止生成周报")
                add_log("   请先在 .env 里配置至少一个 LLM API Key；否则系统只能采集原文，不能完成分类、价值判断和入库")
                progress_bar.progress(100, text="AI分析失败，已停止")
                log_placeholder.code("\n".join(logs))
                st.session_state.collect_result = {
                    "error": "AI分析成功 0 条，未生成新周报。请检查 LLM API Key 配置。"
                }
                st.stop()

            progress_bar.progress(90, text="生成周报...")

            # Step 4: 生成周报
            add_log("=" * 40)
            add_log("📝 生成周报...")
            log_placeholder.code("\n".join(logs))

            report_result = loop.run_until_complete(agent.generate_report())

            if report_result:
                add_log(f"✅ 周报生成成功: 第{report_result['issue_no']}期, {report_result['total_items']}条情报")
            else:
                add_log("⚠️ 周报生成失败")

            progress_bar.progress(100, text="完成!")
            log_placeholder.code("\n".join(logs))

            add_log("=" * 40)
            add_log(f"🎉 全部完成! 分析 {len(analyzed_items)} 条情报, 周报第{report_result['issue_no'] if report_result else '?'}期")

            st.session_state.collect_result = {
                "analyzed": len(analyzed_items),
                "report_issue": report_result["issue_no"] if report_result else None,
                "total_raw": len(all_raw_items),
                "unique_raw": len(unique_items),
            }

        except Exception as e:
            add_log(f"❌ 采集过程出错: {e}")
            import traceback
            add_log(traceback.format_exc()[:500])
            st.session_state.collect_result = {"error": str(e)}

        finally:
            st.session_state.collect_running = False
            st.session_state.collect_logs = logs
            st.rerun()

    # 显示采集日志和结果
    if st.session_state.collect_logs:
        st.subheader("采集日志")
        st.code("\n".join(st.session_state.collect_logs), language="log")

    if st.session_state.collect_result:
        result = st.session_state.collect_result
        if "error" in result:
            st.error(f"采集失败: {result['error']}")
        else:
            st.success(
                f"采集完成! 原始数据 {result['total_raw']} 条 → "
                f"去重 {result['unique_raw']} 条 → "
                f"AI分析 {result['analyzed']} 条 → "
                f"周报第{result['report_issue']}期"
            )

# ============================================================
# 页面5: 设置
# ============================================================
elif page == "⚙️ 设置":
    st.title("⚙️ 设置")

    # --- 邮件配置 ---
    st.subheader("📧 邮件发送配置")
    st.markdown("配置后，周报可自动发送到您的邮箱。")

    # 读取当前.env
    env_vars = {}
    if ENV_PATH.exists():
        with open(ENV_PATH, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    env_vars[k.strip()] = v.strip()

    with st.form("email_form"):
        smtp_server = st.text_input("SMTP服务器", value=env_vars.get("DISTRIBUTION__SMTP_SERVER", ""), placeholder="smtp.example.com")
        smtp_port = st.number_input("SMTP端口", value=int(env_vars.get("DISTRIBUTION__SMTP_PORT", "587")), min_value=1, max_value=65535)
        smtp_user = st.text_input("SMTP用户名(邮箱)", value=env_vars.get("DISTRIBUTION__SMTP_USER", ""), placeholder="your_email@example.com")
        smtp_password = st.text_input("SMTP密码/授权码", value=env_vars.get("DISTRIBUTION__SMTP_PASSWORD", ""), type="password")
        smtp_tls = st.checkbox("使用TLS", value=env_vars.get("DISTRIBUTION__SMTP_USE_TLS", "true").lower() == "true")

        st.markdown("---")
        st.markdown("**收件人邮箱**（多个用英文逗号分隔）")
        recipients = st.text_input("收件人", value=env_vars.get("DISTRIBUTION__EMAIL_RECIPIENTS", ""), placeholder="a@example.com,b@example.com")

        enable_email = st.checkbox("启用邮件发送", value=env_vars.get("DISTRIBUTION__ENABLE_EMAIL", "false").lower() == "true")

        submitted = st.form_submit_button("💾 保存邮件配置")

        if submitted:
            # 更新env_vars
            env_vars["DISTRIBUTION__SMTP_SERVER"] = smtp_server
            env_vars["DISTRIBUTION__SMTP_PORT"] = str(smtp_port)
            env_vars["DISTRIBUTION__SMTP_USER"] = smtp_user
            env_vars["DISTRIBUTION__SMTP_PASSWORD"] = smtp_password
            env_vars["DISTRIBUTION__SMTP_USE_TLS"] = str(smtp_tls).lower()
            env_vars["DISTRIBUTION__EMAIL_RECIPIENTS"] = recipients
            env_vars["DISTRIBUTION__EMAIL_SENDER"] = smtp_user
            env_vars["DISTRIBUTION__ENABLE_EMAIL"] = str(enable_email).lower()

            # 写回.env
            # 先读取原始文件保留注释和顺序
            lines = []
            if ENV_PATH.exists():
                with open(ENV_PATH, "r", encoding="utf-8") as f:
                    for line in f:
                        stripped = line.strip()
                        if stripped and not stripped.startswith("#") and "=" in stripped:
                            k = stripped.split("=", 1)[0].strip()
                            if k in env_vars:
                                lines.append(f"{k}={env_vars[k]}\n")
                                del env_vars[k]
                            else:
                                lines.append(line)
                        else:
                            lines.append(line)

            # 追加新增的key
            for k, v in env_vars.items():
                lines.append(f"{k}={v}\n")

            with open(ENV_PATH, "w", encoding="utf-8") as f:
                f.writelines(lines)

            st.success("邮件配置已保存!")

    # --- 企微配置 ---
    st.divider()
    st.subheader("💬 企业微信配置")

    with st.form("wechat_form"):
        webhook_url = st.text_input("Webhook URL", value=env_vars.get("DISTRIBUTION__WECHAT_WEBHOOK_URL", ""), type="password")
        enable_wechat = st.checkbox("启用企微发送", value=env_vars.get("DISTRIBUTION__ENABLE_WECHAT", "false").lower() == "true")

        submitted_w = st.form_submit_button("💾 保存企微配置")

        if submitted_w:
            env_vars_new = {}
            if ENV_PATH.exists():
                with open(ENV_PATH, "r", encoding="utf-8") as f:
                    for line in f:
                        stripped = line.strip()
                        if stripped and not stripped.startswith("#") and "=" in stripped:
                            k = stripped.split("=", 1)[0].strip()
                            env_vars_new[k] = stripped.split("=", 1)[1].strip()

            env_vars_new["DISTRIBUTION__WECHAT_WEBHOOK_URL"] = webhook_url
            env_vars_new["DISTRIBUTION__ENABLE_WECHAT"] = str(enable_wechat).lower()

            with open(ENV_PATH, "w", encoding="utf-8") as f:
                for k, v in env_vars_new.items():
                    f.write(f"{k}={v}\n")

            st.success("企微配置已保存!")

    # --- 系统信息 ---
    st.divider()
    st.subheader("ℹ️ 系统信息")

    info_col1, info_col2 = st.columns(2)
    with info_col1:
        st.markdown(f"**项目路径**: `{PROJECT_ROOT}`")
        st.markdown(f"**数据库**: `{DB_PATH}` ({DB_PATH.stat().st_size / 1024:.0f} KB)" if DB_PATH.exists() else "**数据库**: 不存在")

    with info_col2:
        # 报告数量
        try:
            report_count = query_one("SELECT COUNT(*) as c FROM weekly_reports")["c"]
            item_count = query_one("SELECT COUNT(*) as c FROM intel_items")["c"]
            st.markdown(f"**周报期数**: {report_count}")
            st.markdown(f"**情报条数**: {item_count}")
        except Exception:
            st.markdown("**数据库**: 无法读取")

    # API Key 状态（只显示是否配置，不显示值）
    st.divider()
    st.subheader("🔑 API配置状态")
    api_keys = {
        "DeepSeek": env_vars.get("LLM__DEEPSEEK_API_KEY", ""),
        "通义千问": env_vars.get("LLM__QWEN_API_KEY", ""),
        "Kimi": env_vars.get("LLM__KIMI_API_KEY", ""),
        "Claude": env_vars.get("LLM__CLAUDE_API_KEY", ""),
        "Jina Reader": env_vars.get("COLLECTOR__JINA_API_KEY", ""),
    }
    for name, val in api_keys.items():
        if val and val != f"your_{name.lower().replace(' ', '_')}_api_key_here":
            st.markdown(f"  ✅ {name}: 已配置")
        else:
            st.markdown(f"  ⬜ {name}: 未配置")

    st.caption("API Key 和代理配置请直接编辑 `.env` 文件")
