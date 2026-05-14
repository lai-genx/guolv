"""
AI分析器模块 - 情报智能分析
"""
import json
import re
from datetime import datetime
from typing import Optional, List, Dict, Any, Tuple
from difflib import SequenceMatcher

from loguru import logger

from llm import llm_router, LLMProvider
from config import settings
from models import IntelItem, RawIntelData, Category, Industry, TechDomain, ActionType, NewsFreshness
from database import db


class IntelAnalyzer:
    """情报分析器 - 使用LLM进行智能分析"""
    
    def __init__(self):
        self.llm = llm_router
        self.similarity_threshold = 0.8  # 标题相似度阈值
    
    async def analyze_item(
        self,
        raw_data: RawIntelData,
        rag_context: str = ""
    ) -> Optional[IntelItem]:
        """
        分析单条情报
        
        Args:
            raw_data: 原始采集数据
            rag_context: RAG检索到的知识上下文
        
        Returns:
            分析后的情报条目
        """
        db.save_raw_intel_data(raw_data, status="pending")

        # 1. URL去重
        if db.check_url_exists(raw_data.url):
            logger.debug(f"URL已存在，跳过: {raw_data.url[:80]}")
            db.update_raw_analysis_status(raw_data.url, status="skipped_duplicate")
            return None
        
        # 2. 标题相似度去重
        if await self._is_duplicate_title(raw_data.title):
            logger.debug(f"标题重复，跳过: {raw_data.title[:50]}")
            db.update_raw_analysis_status(raw_data.url, status="skipped_duplicate_title")
            return None
        
        # 3. 构建分析Prompt
        analysis_prompt = self._build_analysis_prompt(raw_data, rag_context)
        
        # 4. 调用LLM分析
        try:
            system_prompt = self._get_analysis_system_prompt()
            response = await self.llm.analyze(system_prompt, analysis_prompt)
            
            # 5. 解析分析结果
            analysis_result = self._parse_analysis_response(response)
            
            if not analysis_result:
                logger.warning(f"分析结果解析失败: {raw_data.title[:50]}")
                db.update_raw_analysis_status(raw_data.url, status="failed", error="analysis_json_parse_failed")
                return None
            
            # 6. 创建IntelItem（使用安全方法处理枚举验证）
            item = self._safe_create_intel_item(analysis_result, raw_data, rag_context)

            if not item:
                logger.warning(f"创建IntelItem失败: {raw_data.title[:50]}")
                db.update_raw_analysis_status(raw_data.url, status="failed", error="intel_item_create_failed")
                return None
            
            # 7. 启发式修正
            item = self._heuristic_correction(item)
            
            # 8. 保存到数据库
            if db.save_intel_item(item):
                db.update_raw_analysis_status(raw_data.url, status="analyzed")
                logger.info(f"成功分析并保存情报: {item.title[:50]}... [重要性:{item.importance}]")
                return item
            else:
                logger.error(f"保存情报失败: {item.title[:50]}")
                db.update_raw_analysis_status(raw_data.url, status="failed", error="db_save_failed")
                return None
                
        except Exception as e:
            logger.error(f"分析情报失败: {e}")
            db.update_raw_analysis_status(raw_data.url, status="failed", error=str(e)[:500])
            return None
    
    def _validate_enum_value(self, value: str, enum_class, default_value=None) -> str:
        """验证并转换枚举值，如果不有效则使用默认值"""
        if not value:
            # 如果没有值，返回默认值或OTHER
            if default_value:
                return default_value
            return enum_class.OTHER.value if hasattr(enum_class, 'OTHER') else list(enum_class)[0].value

        # 检查值是否有效
        try:
            # 尝试直接创建枚举
            enum_class(value)
            return value
        except (ValueError, KeyError):
            # 如果直接创建失败，尝试找最相近的值
            # 对于Category的特殊处理
            if enum_class == Category:
                value_lower = value.lower()
                if '公司' in value or '动态' in value or 'company' in value_lower or 'news' in value_lower:
                    return Category.COMPANY_NEWS.value
                elif '专利' in value or 'patent' in value_lower:
                    return Category.PATENT.value
                elif '技术' in value or 'technology' in value_lower or 'tech' in value_lower:
                    return Category.TECHNOLOGY.value
                elif '投资' in value or '收购' in value or '并购' in value or 'investment' in value_lower or 'acquisition' in value_lower:
                    return Category.INVESTMENT.value
                elif '下游' in value or '应用' in value or 'downstream' in value_lower or 'application' in value_lower:
                    return Category.DOWNSTREAM.value
                # 默认返回OTHER
                return Category.OTHER.value

            # 对于TechDomain的特殊处理
            if enum_class == TechDomain:
                value_lower = value.lower()
                # 检查包含关系
                if '无线' in value or 'wireless' in value_lower:
                    return TechDomain.WIRELESS.value
                elif '光' in value or 'optical' in value_lower:
                    return TechDomain.OPTICAL.value
                elif '核心网' in value or 'core' in value_lower:
                    return TechDomain.CORE_NETWORK.value
                elif '传输' in value or 'transmission' in value_lower:
                    return TechDomain.TRANSMISSION.value
                elif '接入' in value or 'access' in value_lower:
                    return TechDomain.ACCESS_NETWORK.value
                elif '终端' in value or 'terminal' in value_lower:
                    return TechDomain.TERMINAL.value
                # 默认返回OTHER
                return TechDomain.OTHER.value

            # 其他枚举类型，返回OTHER或第一个值
            if hasattr(enum_class, 'OTHER'):
                return enum_class.OTHER.value
            return list(enum_class)[0].value

    def _safe_create_intel_item(self, analysis_result: dict, raw_data: RawIntelData, rag_context: str) -> Optional[IntelItem]:
        """安全地创建IntelItem，处理枚举验证"""
        try:
            # 验证和转换枚举值
            category_value = self._validate_enum_value(analysis_result.get('category'), Category, '关键公司动态')
            industry_value = self._validate_enum_value(analysis_result.get('industry'), Industry, '其他')
            tech_domain_value = self._validate_enum_value(analysis_result.get('tech_domain'), TechDomain, '其他')
            news_freshness_value = self._validate_enum_value(analysis_result.get('news_freshness'), NewsFreshness, 'current')

            item = IntelItem(
                title=raw_data.title,
                source_url=raw_data.url,
                source_name=raw_data.source,
                source_type=raw_data.source_type,
                pub_date=raw_data.pub_date,
                content=raw_data.content,

                # 分析结果
                category=Category(category_value),
                industry=Industry(industry_value),
                tech_domain=TechDomain(tech_domain_value),
                action_type=analysis_result.get('action_type', '其他'),
                importance=analysis_result.get('importance', 3),
                decision_value=analysis_result.get('decision_value', False),
                is_news=analysis_result.get('is_news', True),
                news_freshness=NewsFreshness(news_freshness_value),

                # 文本内容
                summary_zh=analysis_result.get('summary_zh', raw_data.summary[:200]),
                one_line_insight=analysis_result.get('one_line_insight', ''),

                # 标签和公司
                tags=analysis_result.get('tags', []),
                companies_mentioned=analysis_result.get('companies_mentioned', []),

                # RAG相关
                rag_triggered=bool(rag_context),
                rag_context=rag_context,

                # 产业链维度
                supply_chain=analysis_result.get('supply_chain', '其他'),
                supply_chain_segment=analysis_result.get('supply_chain_segment', ''),
                subsector_type=analysis_result.get('subsector_type', '')
            )
            return item
        except Exception as e:
            logger.error(f"创建IntelItem失败: {e}")
            return None

    async def _is_duplicate_title(self, title: str) -> bool:
        """检查标题是否重复（相似度判断）"""
        # 获取最近的情报标题
        recent_items = db.get_intel_items(days=30, limit=100)
        
        for item in recent_items:
            similarity = self._calculate_similarity(title, item.title)
            if similarity >= self.similarity_threshold:
                return True
        
        return False
    
    def _calculate_similarity(self, s1: str, s2: str) -> float:
        """计算两个字符串的相似度"""
        return SequenceMatcher(None, s1, s2).ratio()
    
    def _build_analysis_prompt(self, raw_data: RawIntelData, rag_context: str = "") -> str:
        """构建分析Prompt"""
        prompt = f"""请分析以下通信设备产业情报：

【标题】
{raw_data.title}

【来源】
{raw_data.source}

【内容摘要】
{raw_data.summary[:1000] if raw_data.summary else '无'}

【正文内容】
{raw_data.content[:2000] if raw_data.content else '无'}
"""

        if rag_context:
            prompt += f"""
【相关技术知识】
{rag_context}
"""

        prompt += """
请按照以下JSON格式输出分析结果：

{
    "category": "关键公司动态|专利情况|新技术|投资收购|下游产业应用",
    "industry": "电信运营商|政企专网|数据中心|工业互联网|车联网|消费电子|其他",
    "tech_domain": "无线通信|光通信|核心网|传输承载|接入网|终端设备|其他",
    "action_type": "研发动作|市场动作|其他",
    "companies_mentioned": ["涉及的公司名1", "公司名2"],
    "importance": 1-5,
    "decision_value": true/false,
    "is_news": true/false,
    "news_freshness": "current|historical|background",
    "summary_zh": "200字以内的中文摘要",
    "one_line_insight": "一句话点评（50字以内）",
    "tags": ["标签1", "标签2"],

    "supply_chain": "芯片与半导体|光通信器件与模块|无线接入设备|光传输与接入|核心网与数据中心|物联网与终端|电信运营与基础设施|其他",
    "supply_chain_segment": "具体环节，如'基带芯片'、'光模块'、'基站设备'等",
    "subsector_type": "政策变化|关键企业动态|研发动态|市场动态|���融资"
}

评分标准：
- 5分：行业重大事件（大型并购、颠覆性技术、重要政策）
- 4分：核心玩家的重要动作（新产品线、技术突破、战略转型）
- 3分：常规但有价值的信息（产品发布、行业报告、重要人事变动）
- 2分：一般性信息（常规财报、例行公告、普通参展参会）
- 1分：边缘信息（消费级产品体验、企业文化活动）

决策价值判断：
- true：竞争对手实质性动作、技术突破、投资并购、政策法规变化
- false：参加展会、例行财报、媒体转载旧新闻、品牌宣传

产业链分类指南：
- 政策变化：国家政策、监管规定、产业政策、国际贸易限制等
- 关键企业动作：新产品发布、战略合作、重大订单、人事变动、业务调整
- 研发动态：新技术突破、新工艺、新标准推进、专利申请
- 市场动态：价格变化、供应链变化、市场份额、出货量、竞争格局
- 投融资：融资轮次、融资金额、并购交易、股权变动、IPO动向

请直接输出JSON，不要包含其他内容。"""

        return prompt
    
    def _get_analysis_system_prompt(self) -> str:
        """获取系统Prompt"""
        return """你是一位专业的通信设备产业情报分析师，精通5G/6G、光通信、核心网、传输承载等领域。

你的任务是分析产业情报，提取关键信息并进行评分分类。

请严格遵循以下规则：
1. 保持客观中立，基于事实分析
2. 准确识别涉及的公司、技术领域和行业
3. 根据内容实质进行评分，不要受标题影响
4. 摘要要简洁明了，突出重点
5. 一句话点评要有洞察力和前瞻性"""
    
    def _parse_analysis_response(self, response: str) -> Optional[Dict[str, Any]]:
        """解析LLM的分析响应"""
        try:
            # 尝试直接解析JSON
            result = json.loads(response.strip())
            return result
        except json.JSONDecodeError:
            pass
        
        # 尝试从文本中提取JSON
        try:
            # 查找JSON代码块
            json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group(1))
                return result
            
            # 查找大括号包裹的内容
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group(0))
                return result
        
        except json.JSONDecodeError:
            pass
        
        logger.error(f"无法解析分析结果: {response[:200]}")
        return None
    
    def _heuristic_correction(self, item: IntelItem) -> IntelItem:
        """启发式修正分析结果"""
        # 修正1：importance=1时，decision_value必须为false
        if item.importance == 1:
            item.decision_value = False
        
        # 修正2：根据来源调整可信度
        if item.source_type == "official_web":
            item.importance = min(5, item.importance + 1)
        elif item.source_type == "wechat":
            # 微信公众号可信度较低
            if item.importance > 1:
                item.importance = max(1, item.importance - 1)
        
        # 修正3：关键词过滤
        if item.title:
            title_lower = item.title.lower()
            # 过滤明显非产业新闻的内容
            filter_keywords = ['传记', '企业史', '品牌故事', '公益活动', '年会', '团建']
            if any(kw in title_lower for kw in filter_keywords):
                item.importance = 1
                item.decision_value = False
                item.is_news = False
                item.news_freshness = NewsFreshness.BACKGROUND
        
        # 修正4：确保公司在监控列表中
        if not item.companies_mentioned:
            # 从标题和内容中提取公司名
            item.companies_mentioned = self._extract_companies(item.title + item.content)
        
        return item
    
    def _extract_companies(self, text: str) -> List[str]:
        """从文本中提取公司名"""
        from config import settings
        
        mentioned = []
        companies = settings.collector.target_companies or []
        
        for company in companies:
            if company in text:
                mentioned.append(company)
        
        return mentioned
    
    async def fetch_full_content(self, url: str) -> str:
        """使用Jina Reader获取文章全文"""
        try:
            jina_api_key = settings.collector.jina_api_key
            headers = {}
            if jina_api_key:
                headers["Authorization"] = f"Bearer {jina_api_key}"
            
            jina_url = f"https://r.jina.ai/http://{url.replace('https://', '').replace('http://', '')}"
            
            import httpx
            async with httpx.AsyncClient() as client:
                response = await client.get(jina_url, headers=headers, timeout=30)
                response.raise_for_status()
                return response.text
        
        except Exception as e:
            logger.error(f"获取全文失败 {url}: {e}")
            return ""
    
    async def analyze_batch(
        self,
        raw_items: List[RawIntelData],
        use_rag: bool = True
    ) -> List[IntelItem]:
        """批量分析情报"""
        from .rag import VectorRAG
        
        results = []
        rag = VectorRAG() if use_rag else None
        
        for raw_data in raw_items:
            try:
                # RAG检索
                rag_context = ""
                if rag:
                    # 只对重要内容进行RAG检索
                    rag_results = rag.search(raw_data.title + raw_data.summary, top_k=3)
                    if rag_results:
                        rag_context = "\n\n".join([r['content'] for r in rag_results])
                
                # 分析
                item = await self.analyze_item(raw_data, rag_context)
                if item:
                    results.append(item)
            
            except Exception as e:
                logger.error(f"批量分析失败: {e}")
                continue
        
        return results

    # ===== Agent升级：ReAct工具调用循环 =====

    async def analyze_item_react(
        self,
        raw_data: RawIntelData,
        rag_context: str = ""
    ) -> Optional[IntelItem]:
        """
        ReAct循环分析 - 支持工具调用（最多3轮迭代）

        仅在以下条件触发：
        - 标题或摘要包含关键公司名 AND 摘要长度 < react_trigger_min_summary_len

        Args:
            raw_data: 原始采集数据
            rag_context: RAG检索到的上下文

        Returns:
            分析后的情报条目
        """
        if not settings.enable_react:
            return await self.analyze_item(raw_data, rag_context)

        # 判断是否需要启用ReAct
        should_use_react = self._should_use_react(raw_data)
        if not should_use_react:
            return await self.analyze_item(raw_data, rag_context)

        logger.info(f"[ReAct] 启用工具调用循环: {raw_data.title[:50]}")

        from processors.agent_tools import get_agent_tools
        tools = get_agent_tools(self.rag)
        await tools.initialize()

        try:
            messages = [
                {
                    "role": "system",
                    "content": self._get_react_system_prompt()
                },
                {
                    "role": "user",
                    "content": self._build_react_prompt(raw_data, rag_context)
                }
            ]

            # ReAct循环（最多3轮）
            for iteration in range(settings.react_max_iterations):
                logger.debug(f"[ReAct] 第{iteration+1}轮迭代")

                response = await self.llm.analyze(
                    messages[0]["content"],  # system
                    messages[-1]["content"] if messages[-1]["role"] == "user" else ""
                )

                # 检查是否为工具调用
                if self._is_tool_call(response):
                    tool_name, tool_args = self._parse_tool_call(response)
                    logger.info(f"[ReAct] 调用工具: {tool_name}")

                    # 执行工具
                    observation = await tools.call_tool(tool_name, **tool_args)

                    # 追加到对话历史
                    messages.append({"role": "assistant", "content": response})
                    messages.append({
                        "role": "user",
                        "content": f"[工具结果]\n{observation}\n\n请基于上述工具结果，继续分析���条情报并输出最终JSON。"
                    })
                else:
                    # 最终答案
                    logger.info(f"[ReAct] 第{iteration+1}轮获得最终答案")
                    analysis_result = self._parse_analysis_response(response)
                    if analysis_result:
                        item = self._safe_create_intel_item(analysis_result, raw_data, rag_context)
                        if item:
                            item = self._heuristic_correction(item)
                            if db.save_intel_item(item):
                                logger.info(f"✅ ReAct分析完成: {item.title[:50]}")
                                return item
                    break

            # 超过迭代次数，返回最后的分析结果
            logger.warning(f"[ReAct] 超出最大迭代次数")
            if response:
                analysis_result = self._parse_analysis_response(response)
                if analysis_result:
                    item = self._safe_create_intel_item(analysis_result, raw_data, rag_context)
                    if item:
                        return self._heuristic_correction(item)

        finally:
            await tools.close()

        return None

    def _should_use_react(self, raw_data: RawIntelData) -> bool:
        """判断是否应该使用ReAct循环"""
        # 条件1：包含关键公司
        companies = settings.collector.target_companies or []
        text = (raw_data.title + " " + raw_data.summary).lower()
        has_company = any(company.lower() in text for company in companies)

        # 条件2：摘要长度 < 阈值
        summary_len = len(raw_data.summary or "")
        summary_too_short = summary_len < settings.react_trigger_min_summary_len

        return has_company and summary_too_short

    def _is_tool_call(self, response: str) -> bool:
        """判断LLM响应是否为工具调用"""
        import re
        # 检查是否包含工具调用标记
        return bool(re.search(r'(Action|工具|调用):', response, re.IGNORECASE))

    def _parse_tool_call(self, response: str) -> tuple:
        """从LLM响应中解析工具调用"""
        import re
        try:
            # 查找 Action: tool_name 形式
            action_match = re.search(r'Action:\s*(\w+)', response)
            if action_match:
                tool_name = action_match.group(1)

                # 查找 Input 或参数
                input_match = re.search(r'Input.*?(\{.*?\})', response, re.DOTALL)
                if input_match:
                    tool_args = json.loads(input_match.group(1))
                    return tool_name, tool_args

            # 备用模式：直接查找JSON
            json_match = re.search(r'\{.*?"tool".*?"name".*?:.*?"(\w+)".*?\}', response, re.DOTALL)
            if json_match:
                return json_match.group(1), {}

        except Exception as e:
            logger.warning(f"解析工具调用失败: {e}")

        return None, {}

    def _get_react_system_prompt(self) -> str:
        """获取ReAct循环的系统Prompt"""
        return """你是一位通信设备产业情报分析师。

你可以使用以下工具来增强分析：
1. fetch_full_content(url) - 获取文章全文
2. search_recent_news(company, days=30) - 查询该公司的最近情报
3. lookup_knowledge(topic) - 查询技术知识库

使用以下格式进行推理：
Thought: 你的思考过程
Action: 工具名称
Input: {"参数": "值"}
Observation: [工具结果会插入这里]
Final: 最终的JSON分析结果

如果信息足够，直接输出JSON。否则，使用工具获取更多信息。"""

    def _build_react_prompt(self, raw_data: RawIntelData, rag_context: str = "") -> str:
        """构建ReAct分析Prompt"""
        prompt = f"""请分析以下通信设备产业情报。如果信息不足，请使用可用工具获取更多背景信息。

【标题】
{raw_data.title}

【来源】
{raw_data.source}

【摘要】
{raw_data.summary[:500] if raw_data.summary else '无'}

【完整内容】
{raw_data.content[:1000] if raw_data.content else '无'}
"""
        if rag_context:
            prompt += f"\n【技术背景】\n{rag_context}"

        prompt += """

请输出JSON格式的分析结果：
{
    "category": "关键公司动态|专利情况|新技术|投资收购|下游产业应用",
    "industry": "电信运营商|政企专网|数据中心|工业互联网|车联网|消费电子|其他",
    "tech_domain": "无线通信|光通信|核心网|传输承载|接入网|终端设备|其他",
    "action_type": "研发动作|市场动作|其他",
    "companies_mentioned": ["公司1", "公司2"],
    "importance": 1-5,
    "decision_value": true/false,
    "is_news": true/false,
    "news_freshness": "current|historical|background",
    "summary_zh": "中文摘要（200字以内）",
    "one_line_insight": "一句话点评（50字以内）",
    "tags": ["标签1", "标签2"]
}"""

        return prompt

    # ===== Agent升级：批量二次审查 =====

    async def run_critic_pass(self, items: List[IntelItem]) -> List[IntelItem]:
        """
        批量二次审查（Critic Pass）

        对分析结果进行质量审查，可修改 importance 和 decision_value

        Args:
            items: 已分析的情报条目列表

        Returns:
            修正后的条目列表
        """
        if not settings.enable_critic or not items:
            return items

        logger.info(f"启动Critic批量审查: {len(items)}条情报")

        corrected = []
        batch_size = settings.critic_batch_size

        # 分批处理
        for i in range(0, len(items), batch_size):
            batch = items[i:i+batch_size]
            logger.info(f"[Critic] 处理第{i//batch_size + 1}批（{len(batch)}条）")

            try:
                corrected_batch = await self._critic_review_batch(batch)
                corrected.extend(corrected_batch)
            except Exception as e:
                logger.error(f"[Critic] 批量审查失败: {e}")
                corrected.extend(batch)  # 使用原始项

        logger.info(f"✅ Critic审查完成")
        return corrected

    async def _critic_review_batch(self, batch: List[IntelItem]) -> List[IntelItem]:
        """对一个批次进行审查"""
        batch_json = [
            {
                "index": i,
                "title": item.title,
                "category": item.category.value if item.category else "",
                "importance": item.importance,
                "decision_value": item.decision_value,
                "summary": item.summary_zh[:100] if item.summary_zh else ""
            }
            for i, item in enumerate(batch)
        ]

        system_prompt = """你是通信产业情报质量审查员。
审查分析结果的分类和评分是否准确。
只能修改 importance 和 decision_value 字段。
返回JSON格式的修正建议。"""

        user_prompt = f"""请审查以下{len(batch)}条情报的分析质量：

{json.dumps(batch_json, ensure_ascii=False, indent=2)}

请返回JSON格式的修正建议，只修改错误的 importance 或 decision_value：
[
    {{"index": 0, "new_importance": 4, "new_decision_value": true, "reason": "..."}},
    ...
]
只包含需要修正的项。如果无需修正，返回空数组 []"""

        try:
            response = await self.llm.analyze(system_prompt, user_prompt)
            corrections = self._parse_critic_response(response)

            # 应用修正
            for correction in corrections:
                idx = correction.get('index')
                if 0 <= idx < len(batch):
                    if 'new_importance' in correction:
                        batch[idx].importance = correction['new_importance']
                    if 'new_decision_value' in correction:
                        batch[idx].decision_value = correction['new_decision_value']
                    logger.info(f"[Critic] 修正条目{idx}: {batch[idx].title[:40]}")

            return batch

        except Exception as e:
            logger.warning(f"[Critic] 审查失败，使用原始结果: {e}")
            return batch

    def _parse_critic_response(self, response: str) -> List[Dict[str, Any]]:
        """解析Critic的审查响应"""
        try:
            # 提取JSON数组
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
        except:
            pass

        return []
