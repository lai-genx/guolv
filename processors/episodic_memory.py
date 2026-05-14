"""
历史记忆模块 - 存储和检索周报摘要
"""
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from loguru import logger

from models import WeeklyReport


class EpisodicMemory:
    """历史记忆管理器 - 存储和检索周报摘要"""

    MEMORY_DIR = Path("knowledge_base/episodic_memory")

    def __init__(self):
        """初始化记忆目录"""
        self.MEMORY_DIR.mkdir(parents=True, exist_ok=True)

    async def save_weekly_summary(self, report: WeeklyReport, llm) -> str:
        """
        LLM将本周报告压缩为记忆摘要，保存到 week_YYYY-WW.md

        Args:
            report: WeeklyReport 对象
            llm: LLMRouter 实例

        Returns:
            保存的文件路径
        """
        try:
            # 生成周编号 (YYYY-WW 格式)
            end_date = report.date_end
            week_no = end_date.isocalendar()[1]
            year = end_date.year
            week_id = f"{year}-{week_no:02d}"

            # 准备LLM提示
            system_prompt = """你是通信产业专家。将以下一周的产业情报报告提炼为关键摘要。
要求:
1. 提炼5条关键主题（每条限50字）
2. 识别3个关键趋势信号
3. 标注前5个重点公司活动
保持简洁，便于后续周报对标和趋势分析。"""

            user_prompt = f"""请分析以下周报（第{report.issue_no}期，{report.date_start.strftime('%Y-%m-%d')}至{report.date_end.strftime('%Y-%m-%d')}）：

{report.report_md[:2000]}

请生成记忆摘要（JSON格式）：
{{
    "key_themes": ["主题1", "主题2", ...],
    "trend_signals": ["趋势1", "���势2", "趋势3"],
    "top_companies": ["公司1", "公司2", ...],
    "summary": "本周摘要（100-200字）"
}}"""

            # 调用LLM
            response = await llm.analyze(system_prompt, user_prompt)

            # 尝试解析JSON
            try:
                # 提取JSON块
                import re
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    memory_data = json.loads(json_match.group())
                else:
                    memory_data = self._create_default_memory(report)
            except:
                memory_data = self._create_default_memory(report)

            # 构建记忆文件内容
            memory_content = f"""# 第{report.issue_no}期周报记忆 ({week_id})

**时间**: {report.date_start.strftime('%Y-%m-%d')} ~ {report.date_end.strftime('%Y-%m-%d')}

## 核心主题
"""
            for i, theme in enumerate(memory_data.get('key_themes', [])[:5], 1):
                memory_content += f"{i}. {theme}\n"

            memory_content += "\n## 趋势信号\n"
            for i, signal in enumerate(memory_data.get('trend_signals', [])[:3], 1):
                memory_content += f"- {signal}\n"

            memory_content += "\n## 活跃企业\n"
            for company in memory_data.get('top_companies', [])[:5]:
                memory_content += f"- {company}\n"

            memory_content += f"\n## 周报摘要\n{memory_data.get('summary', '')}\n"
            memory_content += f"\n---\n*自动生成于 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n"

            # 保存到文件
            memory_file = self.MEMORY_DIR / f"week_{week_id}.md"
            with open(memory_file, 'w', encoding='utf-8') as f:
                f.write(memory_content)

            logger.info(f"记忆摘要已保存: {memory_file}")
            return str(memory_file)

        except Exception as e:
            logger.error(f"保存记忆摘要失败: {e}")
            return ""

    def _create_default_memory(self, report: WeeklyReport) -> dict:
        """当LLM解析失败时，创建默认的记忆数据"""
        return {
            "key_themes": list(report.category_distribution.keys())[:5],
            "trend_signals": list(report.importance_distribution.keys())[:3],
            "top_companies": [],
            "summary": f"本期采集{report.total_items}条情报"
        }

    def get_recent_context(self, n_weeks: int = 3) -> str:
        """
        读取最近 n 周记忆，格式化为LLM上下文字符串

        Args:
            n_weeks: 读取的周数

        Returns:
            格式化的记忆上下文字符串
        """
        try:
            # 列出所有周报文件
            memory_files = sorted(self.MEMORY_DIR.glob("week_*.md"), reverse=True)[:n_weeks]

            if not memory_files:
                logger.warning("没有找到历史记忆文件")
                return ""

            context = "## 最近周报回顾\n\n"

            for memory_file in reversed(memory_files):
                with open(memory_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    context += f"{content}\n\n"

            return context

        except Exception as e:
            logger.error(f"读取历史记忆失败: {e}")
            return ""

    def get_memory_file(self, week_id: str) -> Optional[str]:
        """
        获取特定周的记忆内容

        Args:
            week_id: 周编号 (YYYY-WW 格式)

        Returns:
            记忆内容或 None
        """
        try:
            memory_file = self.MEMORY_DIR / f"week_{week_id}.md"
            if memory_file.exists():
                with open(memory_file, 'r', encoding='utf-8') as f:
                    return f.read()
            return None
        except Exception as e:
            logger.error(f"读取记忆文件失败: {e}")
            return None

    def list_memory_files(self) -> list:
        """列出所有记忆文件"""
        return sorted(self.MEMORY_DIR.glob("week_*.md"), reverse=True)
