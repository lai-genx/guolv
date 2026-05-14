"""
搜索采集器 - 使用搜索引擎API采集情报
"""
from datetime import datetime, timedelta
from typing import List, Optional, Dict
import urllib.parse
import random
import re

from loguru import logger

from .base import BaseCollector, CollectorResult, RawIntelData, contains_keywords, MONITORED_KEYWORDS
from config import settings


class SearchCollector(BaseCollector):
    """搜索采集器 - 通过搜索API获取情报"""
    
    def __init__(self):
        super().__init__("search")
        # 这里使用Bing搜索作为示例
        self.bing_api_key = None  # 需要在配置中设置
        # 随机User-Agent列表
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
        ]
    
    async def collect(self, **kwargs) -> CollectorResult:
        """通过搜索采集情报"""
        all_items = []
        
        # 搜索关键词组合
        keywords = self._build_search_keywords()
        
        max_results_per_query = kwargs.get('max_results_per_query', 10)
        max_queries = kwargs.get('max_queries', 5)
        
        # 限制查询数量
        queries = keywords[:max_queries]
        
        for query in queries:
            try:
                logger.info(f"搜索关键词: {query}")
                items = await self._search(query, max_results_per_query)
                all_items.extend(items)
                logger.info(f"搜索 '{query}' 获取 {len(items)} 条结果")
            except Exception as e:
                logger.error(f"搜索失败 '{query}': {e}")
        
        # 去重
        seen_urls = set()
        unique_items = []
        for item in all_items:
            if item.url not in seen_urls:
                seen_urls.add(item.url)
                unique_items.append(item)
        
        return CollectorResult(
            items=unique_items,
            success=len(unique_items) > 0,
            message=f"搜索完成，获取 {len(unique_items)} 条唯一结果",
            total_found=len(all_items)
        )
    
    def _build_search_keywords(self) -> List[str]:
        """构建搜索关键词"""
        keywords = []

        # 核心关键词组合（中文）
        base_keywords_zh = [
            "通信设备 5G 6G 新闻",
            "华为 最新动态 新闻",
            "中兴通讯 最新动态 新闻",
            "爱立信 诺基亚 最新动态",
            "光通信 光纤 波分复用 技术",
            "核心网 网络切片 边缘计算",
            "Open RAN 虚拟化 基站",
            "通信行业 投资 并购 融资",
            "通信专利 技术突破 标准",
            "运营商 5G 基站 建设",
            "光模块 光器件 技术",
        ]

        # 核心关键词组合（英文）
        base_keywords_en = [
            "5G 6G telecommunications news",
            "Huawei technology news",
            "ZTE Ericsson Nokia latest",
            "optical communication fiber",
            "core network network slicing edge computing",
            "Open RAN virtualization base station",
            "telecom industry investment acquisition",
            "telecom patent breakthrough standard",
            "carrier 5G base station",
            "optical module optical device",
        ]

        keywords.extend(base_keywords_zh)
        keywords.extend(base_keywords_en)

        return keywords
    
    async def _search(self, query: str, max_results: int = 10) -> List[RawIntelData]:
        """执行搜索"""
        items = []
        
        # 如果没有API密钥，使用模拟数据或网页搜索
        if not self.bing_api_key:
            items = await self._web_search(query, max_results)
        else:
            items = await self._bing_api_search(query, max_results)
        
        return items
    
    async def _web_search(self, query: str, max_results: int) -> List[RawIntelData]:
        """通过Bing网页搜索获取结果"""
        items = []

        try:
            # 使用Bing搜索结果页
            encoded_query = urllib.parse.quote(query)
            search_url = f"https://www.bing.com/search?q={encoded_query}&count={max_results}"

            # 随机选择User-Agent
            headers = {
                "User-Agent": random.choice(self.user_agents),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            }
            response = await self.client.get(search_url, headers=headers)
            html = response.text
            if not html:
                return items

            soup = self.parse_html(html)

            # 尝试从HTML中提取结果
            items = await self._extract_bing_results(soup, max_results)

            # 如果提取失败，尝试使用Jina Reader API作为fallback
            if not items:
                logger.info(f"HTML提取失败，尝试使用Jina Reader API...")
                items = await self._jina_search(query, max_results)

        except Exception as e:
            logger.error(f"网页搜索失败: {e}")

        return items

    async def _extract_bing_results(self, soup, max_results: int) -> List[RawIntelData]:
        """从Bing HTML中提取结果"""
        items = []

        # 增强的选择器列表 - 涵盖多个Bing版本的HTML结构
        result_selectors = [
            '.b_algo',                           # 标准Bing结果容器 (最常见)
            'div.b_algo',                        # 更明确的容器选择器
            '.b_results > li',                   # 列表形式 (旧版)
            'li.b_algo',                         # 列表项形式
            '[data-module-id*="organic"]',       # 有机搜索结果
            '.result-item',                      # 通用备用
            'article',                           # HTML5语义标签
            'div[data-bm]',                      # Bing module标签
            '.ckSGb',                            # Google搜索兼容性
            'main > div',                        # 主容器
        ]

        # 尝试所有选择器，收集所有可能的结果
        all_candidate_elements = []

        for selector in result_selectors:
            try:
                elements = soup.select(selector)[:max_results]
                if elements:
                    logger.debug(f"选择器 '{selector}' 找到 {len(elements)} 个候选元素")
                    all_candidate_elements.extend(elements)
            except Exception as e:
                logger.debug(f"选择器 '{selector}' 执行失败: {e}")
                continue

        # 去重元素 (使用HTML内容作为唯一标识)
        seen_content = set()
        unique_elements = []
        for elem in all_candidate_elements:
            content_hash = hash(elem.decode() if hasattr(elem, 'decode') else str(elem)[:200])
            if content_hash not in seen_content:
                seen_content.add(content_hash)
                unique_elements.append(elem)

        # 从去重后的元素中提取信息
        for elem in unique_elements[:max_results]:
            try:
                title, url, summary = self._extract_item_details(elem)

                if title and url and self._is_valid_result(title, url):
                    items.append(RawIntelData(
                        title=title,
                        url=url,
                        source="Bing搜索",
                        source_type="search",
                        pub_date=datetime.now(),
                        content=summary,
                        summary=summary[:500] if summary else ""
                    ))

                    if len(items) >= max_results:
                        break

            except Exception as e:
                logger.debug(f"提取结果详情失败: {e}")
                continue

        return items

    def _extract_item_details(self, elem) -> tuple:
        """从单个结果元素中提取标题、URL和摘要"""
        title = None
        url = None
        summary = ""

        # 多层级标题提取策略
        # 策略1: h2 > a (最标准)
        h2_elem = elem.find('h2')
        if h2_elem:
            a_elem = h2_elem.find('a')
            if a_elem:
                title = a_elem.get_text(strip=True)
                url = a_elem.get('href', '')

        # 策略2: h3 > a (某些版本)
        if not url:
            h3_elem = elem.find('h3')
            if h3_elem:
                a_elem = h3_elem.find('a')
                if a_elem:
                    title = a_elem.get_text(strip=True)
                    url = a_elem.get('href', '')

        # 策略3: 查找data-id属性的链接
        if not url:
            for a_elem in elem.find_all('a', {'data-id': True}):
                potential_title = a_elem.get_text(strip=True)
                potential_url = a_elem.get('href', '')
                if potential_title and len(potential_title) > 5:
                    title = potential_title
                    url = potential_url
                    break

        # 策略4: 智能选择最长的有效标题链接
        if not url:
            best_a_elem = None
            best_title_len = 0

            for a_elem in elem.find_all('a', href=True):
                potential_title = a_elem.get_text(strip=True)
                potential_url = a_elem.get('href', '')

                # 优先选择：标题长度合理、不是Bing内部链接、不是过短标题
                if (potential_title and
                    5 < len(potential_title) < 200 and
                    'bing.com' not in potential_url and
                    'search?' not in potential_url):

                    # 选择标题最长的
                    if len(potential_title) > best_title_len:
                        best_title_len = len(potential_title)
                        best_a_elem = a_elem
                        title = potential_title
                        url = potential_url

        # 提取摘要 - 多策略
        # 优先查找p标签
        summary_candidates = []
        for p_elem in elem.find_all('p'):
            p_text = p_elem.get_text(strip=True)
            if p_text and len(p_text) > 20:  # 只保留有意义的摘要
                summary_candidates.append(p_text)

        # 备用：查找div.b_snippet或其他摘要容器
        if not summary_candidates:
            for div_elem in elem.find_all(['div', 'span'], class_=True):
                div_text = div_elem.get_text(strip=True)
                if div_text and 20 < len(div_text) < 500:
                    # 避免选择导航、菜单等
                    if any(word not in div_text.lower() for word in ['导航', '菜单', '登录', '注册', '广告']):
                        summary_candidates.append(div_text)

        if summary_candidates:
            summary = sorted(summary_candidates, key=len, reverse=True)[0][:500]

        return title, url, summary

    def _is_valid_result(self, title: str, url: str) -> bool:
        """验证提取的结果是否有效"""
        if not title or not url:
            return False

        # URL验证
        if 'bing.com' in url or 'search?' in url:
            return False

        # 标题长度验证 (对中文友好)
        # 中文标题最少2个字，英文标题最少5个字符
        title_stripped = title.strip()
        title_len = len(title_stripped)

        # 检测是否为中文标题
        has_chinese = any('\u4e00' <= c <= '\u9fff' for c in title_stripped)

        if has_chinese:
            # 中文标题: 最少2个字符，最多200个字符
            if title_len < 2 or title_len > 200:
                return False
        else:
            # 英文标题: 最少5个字符，最多200个字符
            if title_len < 5 or title_len > 200:
                return False

        # 跳过纯数字或特殊字符标题
        if not any(c.isalpha() or '\u4e00' <= c <= '\u9fff' for c in title_stripped):
            return False

        return True

    async def _jina_search(self, query: str, max_results: int) -> List[RawIntelData]:
        """使用Jina Reader API进行搜索"""
        items = []

        try:
            jina_api_key = settings.collector.jina_api_key

            if not jina_api_key:
                logger.warning("Jina API密钥未配置，跳过Jina fallback")
                return items

            # 使用Bing搜索URL
            encoded_query = urllib.parse.quote(query)
            search_url = f"https://www.bing.com/search?q={encoded_query}"

            # 调用Jina Reader API
            jina_url = f"https://r.jina.ai/{search_url}"
            headers = {
                "Authorization": f"Bearer {jina_api_key}",
                "User-Agent": random.choice(self.user_agents),
            }

            response = await self.client.get(jina_url, headers=headers, timeout=30)
            content = response.text

            # 解析Jina返回的Markdown格式结果
            # Jina会返回网页的Markdown表示
            lines = content.split('\n')

            for i, line in enumerate(lines):
                if i >= max_results * 2:  # 限制处理行数
                    break

                # 查找URL pattern (通常是 [title](url) 格式)
                url_pattern = r'\[(.+?)\]\((.+?)\)'
                matches = re.findall(url_pattern, line)

                for match in matches:
                    if len(items) >= max_results:
                        break

                    title, url = match
                    if self._is_valid_result(title, url):
                        # 从后续行提取摘要
                        summary = ""
                        for j in range(i + 1, min(i + 3, len(lines))):
                            if lines[j].strip():
                                summary = lines[j][:200]
                                break

                        items.append(RawIntelData(
                            title=title,
                            url=url,
                            source="Jina Reader",
                            source_type="search",
                            pub_date=datetime.now(),
                            content=summary,
                            summary=summary
                        ))

            if items:
                logger.info(f"Jina Reader 获取 {len(items)} 条结果")

        except Exception as e:
            logger.warning(f"Jina搜索失败: {e}")

        return items
    
    async def _bing_api_search(self, query: str, max_results: int) -> List[RawIntelData]:
        """使用Bing Search API搜索"""
        items = []
        
        try:
            search_url = "https://api.bing.microsoft.com/v7.0/news/search"
            headers = {"Ocp-Apim-Subscription-Key": self.bing_api_key}
            params = {
                "q": query,
                "count": max_results,
                "mkt": "zh-CN",
                "freshness": "Week"  # 最近一周
            }
            
            response = await self.client.get(search_url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            
            for news in data.get("value", []):
                try:
                    # 解析日期
                    pub_date = None
                    date_str = news.get("datePublished")
                    if date_str:
                        try:
                            pub_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                        except:
                            pass
                    
                    item = RawIntelData(
                        title=news.get("name", ""),
                        url=news.get("url", ""),
                        source=news.get("provider", [{}])[0].get("name", "Bing新闻"),
                        source_type="search",
                        pub_date=pub_date,
                        content=news.get("description", ""),
                        summary=news.get("description", "")[:500]
                    )
                    items.append(item)
                
                except Exception as e:
                    logger.debug(f"解析新闻项失败: {e}")
                    continue
        
        except Exception as e:
            logger.error(f"Bing API搜索失败: {e}")
        
        return items
