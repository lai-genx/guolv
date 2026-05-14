"""
周计划Agent - 基于历史记忆，LLM生成本周情报优先级
"""
import json
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from loguru import logger

from llm import llm_router


@dataclass
class WeeklyPlan:
    """周计划数据模型"""
    focus_companies: List[str]      # 本周重点监控公司（最多5家）
    focus_topics: List[str]         # 本周重点技术方向
    priority_queries: List[str]     # 优先搜索查询（覆盖默认前5条）
    rationale: str                  # LLM解释为何这样规划
    created_at: str = None          # 计划创建时间

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()


class WeeklyPlanningAgent:
    """周计划Agent - 生成本周监控重点"""

    PLANS_DIR = Path("data/plans")

    def __init__(self, llm=None):
        """
        初始化规划Agent

        Args:
            llm: LLMRouter 实例
        """
        self.llm = llm or llm_router
        self.PLANS_DIR.mkdir(parents=True, exist_ok=True)

    async def generate_plan(self, memory_context: str = "") -> WeeklyPlan:
        """
        基于历史记忆，LLM生成本周情报优先级

        Args:
            memory_context: 历史记忆上下文（来自EpisodicMemory.get_recent_context()）

        Returns:
            WeeklyPlan 对象
        """
        try:
            # 构建系统Prompt
            system_prompt = """你是通信产业情报分析师。根据过去几周的情报摘要，规划本周的监控重点。
你的目标是：
1. 识别持续需要关注的关键公司
2. 预测可能的技术趋势方向
3. 建议优先搜索的关键词

输出必须是JSON格式，包含 focus_companies, focus_topics, priority_queries, rationale。"""

            # 构建用户Prompt
            if memory_context:
                user_prompt = f"""请基于以下历史情报，规划本周（{datetime.now().strftime('%Y-%m-%d')}）的监控重点：

{memory_context}

请输出JSON格式的规划：
{{
    "focus_companies": ["公司1", "公司2", "公司3", "公司4", "公司5"],
    "focus_topics": ["5G演进", "光通信", "核心网", "..."],
    "priority_queries": ["query1", "query2", "query3", "..."],
    "rationale": "基于上周的趋势，本周应重点关注...（50-100字）"
}}"""
            else:
                user_prompt = f"""本周（{datetime.now().strftime('%Y-%m-%d')}）暂无历史记忆。
请基于通信产业当前热点，提议监控重点：

{{
    "focus_companies": ["华为", "中兴", "爱立信", "诺基亚", "思科"],
    "focus_topics": ["5G", "6G", "光通信", "核心网", "人工智能"],
    "priority_queries": ["5G毫米波", "光芯片", "云原生", "..."],
    "rationale": "首周规划采用行业标准重点..."
}}"""

            # 调用LLM
            response = await self.llm.analyze(system_prompt, user_prompt)

            # 解析JSON
            plan = self._parse_plan_response(response)

            # 保存计划
            week_no = datetime.now().isocalendar()[1]
            year = datetime.now().year
            plan_file = self.PLANS_DIR / f"plan_{year}-{week_no:02d}.json"

            with open(plan_file, 'w', encoding='utf-8') as f:
                json.dump(asdict(plan), f, ensure_ascii=False, indent=2)

            logger.info(f"周计划已生成: {plan_file}")
            logger.info(f"重点公司: {', '.join(plan.focus_companies[:3])}")
            logger.info(f"重点话题: {', '.join(plan.focus_topics[:3])}")

            return plan

        except Exception as e:
            logger.error(f"生成周计划失败: {e}")
            # 返回默认计划
            return self._create_default_plan()

    def _parse_plan_response(self, response: str) -> WeeklyPlan:
        """解析LLM响应为WeeklyPlan"""
        try:
            import re
            # 提取JSON块
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                plan_data = json.loads(json_match.group())
            else:
                plan_data = {}

            # 验证必需字段
            focus_companies = plan_data.get('focus_companies', [])[:5]
            focus_topics = plan_data.get('focus_topics', [])[:5]
            priority_queries = plan_data.get('priority_queries', [])[:10]
            rationale = plan_data.get('rationale', '')

            # 确保都是字符串列表
            if isinstance(focus_companies, str):
                focus_companies = [focus_companies]
            if isinstance(focus_topics, str):
                focus_topics = [focus_topics]
            if isinstance(priority_queries, str):
                priority_queries = [priority_queries]

            return WeeklyPlan(
                focus_companies=focus_companies,
                focus_topics=focus_topics,
                priority_queries=priority_queries,
                rationale=rationale
            )

        except Exception as e:
            logger.warning(f"解析规划响应失败: {e}")
            return self._create_default_plan()

    def _create_default_plan(self) -> WeeklyPlan:
        """创建默认规划"""
        return WeeklyPlan(
            focus_companies=["华为", "中兴", "爱立信", "诺基亚", "思科"],
            focus_topics=["5G", "6G", "光通信", "核心网", "人工智能"],
            priority_queries=[
                "5G毫米波", "光芯片", "云原生", "RAN sharing",
                "Open RAN", "4G LTE", "3GPP", "E-band"
            ],
            rationale="采用行业标准重点监控"
        )

    def get_latest_plan(self) -> Optional[WeeklyPlan]:
        """获取最新的周计划"""
        try:
            plan_files = sorted(self.PLANS_DIR.glob("plan_*.json"), reverse=True)
            if plan_files:
                with open(plan_files[0], 'r', encoding='utf-8') as f:
                    plan_data = json.load(f)
                    return WeeklyPlan(**plan_data)
            return None
        except Exception as e:
            logger.error(f"读取周计划失败: {e}")
            return None
