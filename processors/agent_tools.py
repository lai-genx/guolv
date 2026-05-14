"""
Agent工具集 - LLM可调用的工具定义
"""
import json
from typing import List, Optional, Dict, Any

import httpx
from loguru import logger

from database import db
from processors.rag import VectorRAG
from config import settings


# 工具定义 JSON Schema（用于LLM function calling）
TOOL_SCHEMAS = [
    {
        "name": "fetch_full_content",
        "description": "获取URL的完整文章内容。当标题/摘要信息不足以判断重要性时使用。",
        "parameters": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "要获取的文章URL"
                }
            },
            "required": ["url"]
        }
    },
    {
        "name": "search_recent_news",
        "description": "查询数据库中该公司最近30天的已收录情报，判断是否重复或相关。",
        "parameters": {
            "type": "object",
            "properties": {
                "company": {
                    "type": "string",
                    "description": "公司名称"
                },
                "days": {
                    "type": "integer",
                    "description": "查询天数，默认30",
                    "default": 30
                }
            },
            "required": ["company"]
        }
    },
    {
        "name": "lookup_knowledge",
        "description": "查询专业知识库，获取相关技术背景信息以增强分析深度。",
        "parameters": {
            "type": "object",
            "properties": {
                "topic": {
                    "type": "string",
                    "description": "要查询的技术主题"
                }
            },
            "required": ["topic"]
        }
    }
]


class AgentTools:
    """LLM可调用的工具集合"""

    def __init__(self, rag: Optional[VectorRAG] = None):
        """
        初始化工具集

        Args:
            rag: VectorRAG 实例（用于知识库查询）
        """
        self.rag = rag
        self.http_client = None

    async def initialize(self):
        """初始化HTTP客户端"""
        self.http_client = httpx.AsyncClient(timeout=30)

    async def close(self):
        """关闭HTTP客户端"""
        if self.http_client:
            await self.http_client.aclose()

    async def fetch_full_content(self, url: str) -> str:
        """
        使用Jina Reader API获取文章全文

        Args:
            url: 文章URL

        Returns:
            文章内容（最多500字）
        """
        try:
            if not settings.collector.jina_api_key:
                logger.warning("Jina API密钥未配置，无法获取全文")
                return ""

            # 调用Jina Reader API
            jina_url = f"https://r.jina.ai/{url}"
            headers = {
                "Authorization": f"Bearer {settings.collector.jina_api_key}"
            }

            if not self.http_client:
                await self.initialize()

            response = await self.http_client.get(jina_url, headers=headers, timeout=30)
            response.raise_for_status()

            content = response.text
            # 限制返回长度
            if len(content) > 500:
                content = content[:500] + "..."

            logger.debug(f"成功获取全文: {url[:80]}")
            return content

        except Exception as e:
            logger.warning(f"获取全文失败: {url[:80]} - {e}")
            return ""

    async def search_recent_news(self, company: str, days: int = 30) -> str:
        """
        查询数据库中该公司最近的情报标题

        Args:
            company: 公司名称
            days: 查询天数

        Returns:
            情报标题列表（格式化字符串）
        """
        try:
            items = db.get_items_by_company(company, days=days)

            if not items:
                return f"未找到 {company} 在过去 {days} 天的情报"

            # 格式化输出
            result = f"【{company}最近{days}天的情报】（共{len(items)}条）:\n"
            for item in items[:5]:  # 最多返回5条
                result += f"- {item.title[:60]} (重要度: {item.importance})\n"

            if len(items) > 5:
                result += f"... 还有 {len(items) - 5} 条"

            return result

        except Exception as e:
            logger.warning(f"数据库查询失败: {e}")
            return ""

    async def lookup_knowledge(self, topic: str) -> str:
        """
        查询RAG知识库获取技术背景

        Args:
            topic: 技术主题

        Returns:
            相关知识背景
        """
        try:
            if not self.rag or not self.rag.is_initialized:
                logger.warning("RAG系统未初始化")
                return ""

            context = self.rag.get_context_for_analysis(topic, top_k=3)
            if context:
                # 限制长度
                if len(context) > 300:
                    context = context[:300] + "..."
                return f"【相关技术背景】\n{context}"
            return ""

        except Exception as e:
            logger.warning(f"知识库查询失败: {e}")
            return ""

    async def call_tool(self, tool_name: str, **kwargs) -> str:
        """
        通用工具调用接口

        Args:
            tool_name: 工具名称
            **kwargs: 工具参数

        Returns:
            工具执行结果
        """
        if tool_name == "fetch_full_content":
            return await self.fetch_full_content(kwargs.get("url", ""))
        elif tool_name == "search_recent_news":
            return await self.search_recent_news(
                kwargs.get("company", ""),
                kwargs.get("days", 30)
            )
        elif tool_name == "lookup_knowledge":
            return await self.lookup_knowledge(kwargs.get("topic", ""))
        else:
            logger.warning(f"未知的工具: {tool_name}")
            return ""


# 创建全局工具实例
agent_tools = None


def get_agent_tools(rag: Optional[VectorRAG] = None) -> AgentTools:
    """获取或创建AgentTools实例"""
    global agent_tools
    if agent_tools is None:
        agent_tools = AgentTools(rag=rag)
    return agent_tools
