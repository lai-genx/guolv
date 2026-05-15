"""
搜索采集器：优先使用正式搜索 API，回退到网页搜索。
"""
from datetime import datetime
from typing import List
import asyncio
import random
import re
import urllib.parse

from loguru import logger

from .base import BaseCollector, CollectorResult, RawIntelData
from config import settings


class SearchCollector(BaseCollector):
    """通过搜索 API 获取通信设备产业情报。"""

    def __init__(self):
        super().__init__("search")
        self.bing_api_key = None
        self.serper_calls = 0
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        ]

    async def collect(self, **kwargs) -> CollectorResult:
        all_items: List[RawIntelData] = []
        keywords = self._build_search_keywords()

        max_results_per_query = kwargs.get(
            "max_results_per_query",
            settings.collector.search_max_results_per_query,
        )
        max_queries = kwargs.get("max_queries", settings.collector.search_max_queries)
        per_query_timeout = kwargs.get(
            "per_query_timeout",
            settings.collector.search_per_query_timeout,
        )
        queries = keywords[:max_queries] if max_queries and max_queries > 0 else keywords

        for query in queries:
            try:
                logger.info(f"搜索关键词: {query}")
                items = await asyncio.wait_for(
                    self._search(query, max_results_per_query),
                    timeout=per_query_timeout,
                )
                all_items.extend(items)
                logger.info(f"搜索 '{query}' 获取 {len(items)} 条结果")
            except asyncio.TimeoutError:
                logger.warning(f"搜索超时，已跳过: {query}")
            except Exception as e:
                logger.warning(f"搜索失败 '{query}': {e}")

        unique_items = self._deduplicate(all_items)
        provider = "Serper" if settings.collector.serper_api_key else "Fallback"
        logger.info(f"SearchCollector本轮{provider}调用次数: {self.serper_calls}")

        return CollectorResult(
            items=unique_items,
            success=len(unique_items) > 0,
            message=f"搜索完成，获取 {len(unique_items)} 条唯一结果，Serper调用 {self.serper_calls} 次",
            total_found=len(all_items),
        )

    def _build_search_keywords(self) -> List[str]:
        return [
            "通信设备 5G 6G 新闻",
            "Huawei 5G 6G latest news",
            "ZTE 5G latest news",
            "Ericsson Nokia Open RAN latest news",
            "光模块 800G 1.6T 最新消息",
            "800G optical module latest news",
            "5G-Advanced telecom equipment news",
            "Open RAN virtualization base station latest news",
            "telecom industry investment acquisition latest",
            "core network network slicing edge computing telecom news",
            "site:huawei.com/en/news 5G OR 6G",
            "site:zte.com.cn 5G 新闻",
            "site:nokia.com/news Open RAN OR 5G",
            "site:ericsson.com/en/news 5G OR 6G",
            "site:lightreading.com 5G Open RAN optical module",
            "site:rcrwireless.com 5G Open RAN telecom",
            "site:telecoms.com 5G 6G Open RAN",
            "site:sdxcentral.com 5G Open RAN telecom",
            "site:businesswire.com optical module 800G",
            "site:marketscreener.com optical module 800G",
            "site:finance.yahoo.com optical module 800G",
        ]

    async def _search(self, query: str, max_results: int = 10) -> List[RawIntelData]:
        provider = settings.collector.search_provider.lower()
        if settings.collector.serper_api_key and provider in ("auto", "serper"):
            items = await self._serper_search(query, max_results, endpoint="news")
            if len(items) < max(3, max_results // 2):
                existing_urls = {item.url for item in items}
                fallback_items = await self._serper_search(query, max_results, endpoint="search")
                items.extend(item for item in fallback_items if item.url not in existing_urls)
            if items:
                return items[:max_results]

        if self.bing_api_key:
            return await self._bing_api_search(query, max_results)
        return await self._web_search(query, max_results)

    async def _serper_search(self, query: str, max_results: int, endpoint: str) -> List[RawIntelData]:
        url = f"https://google.serper.dev/{endpoint}"
        headers = {
            "X-API-KEY": settings.collector.serper_api_key,
            "Content-Type": "application/json",
        }
        payload = {
            "q": query,
            "num": max_results,
            "gl": "us",
            "hl": "zh-cn",
        }

        try:
            self.serper_calls += 1
            response = await self.client.post(url, headers=headers, json=payload, timeout=25)
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            logger.warning(f"Serper {endpoint} 搜索失败 '{query}': {e}")
            return []

        rows = data.get("news") if endpoint == "news" else data.get("organic")
        rows = rows or []
        items: List[RawIntelData] = []

        for row in rows:
            if len(items) >= max_results:
                break
            title = (row.get("title") or "").strip()
            url_value = (row.get("link") or "").strip()
            summary = (row.get("snippet") or "").strip()
            if not self._is_valid_result(title, url_value):
                continue
            if not self._is_relevant_result(query, title, summary, url_value):
                continue

            source = row.get("source") or ("Serper News" if endpoint == "news" else "Serper Search")
            pub_date = self._parse_serper_date(row.get("date") or "")
            items.append(RawIntelData(
                title=title,
                url=url_value,
                source=source,
                source_type="search",
                pub_date=pub_date,
                content=summary,
                summary=summary[:500],
            ))

        return items

    async def _web_search(self, query: str, max_results: int) -> List[RawIntelData]:
        try:
            encoded_query = urllib.parse.quote(query)
            search_url = f"https://www.bing.com/search?q={encoded_query}&count={max_results}"
            headers = {
                "User-Agent": random.choice(self.user_agents),
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            }
            response = await self.client.get(search_url, headers=headers)
            html = response.text
            if not html:
                return []
            soup = self.parse_html(html)
            return await self._extract_bing_results(soup, max_results)
        except Exception as e:
            logger.warning(f"网页搜索失败: {e}")
            return []

    async def _extract_bing_results(self, soup, max_results: int) -> List[RawIntelData]:
        items: List[RawIntelData] = []
        for elem in soup.select(".b_algo, li.b_algo")[:max_results * 2]:
            link_elem = elem.select_one("h2 a[href], h3 a[href], a[href]")
            if not link_elem:
                continue
            title = link_elem.get_text(strip=True)
            url = link_elem.get("href", "")
            if not self._is_valid_result(title, url):
                continue
            snippet = elem.select_one("p, .b_caption, .b_snippet")
            summary = snippet.get_text(" ", strip=True) if snippet else ""
            items.append(RawIntelData(
                title=title,
                url=url,
                source="Bing搜索",
                source_type="search",
                pub_date=datetime.now(),
                content=summary,
                summary=summary[:500],
            ))
            if len(items) >= max_results:
                break
        return items

    async def _bing_api_search(self, query: str, max_results: int) -> List[RawIntelData]:
        items: List[RawIntelData] = []
        try:
            search_url = "https://api.bing.microsoft.com/v7.0/news/search"
            headers = {"Ocp-Apim-Subscription-Key": self.bing_api_key}
            params = {"q": query, "count": max_results, "mkt": "zh-CN", "freshness": "Week"}
            response = await self.client.get(search_url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            for news in data.get("value", []):
                title = news.get("name", "")
                url = news.get("url", "")
                if not self._is_valid_result(title, url):
                    continue
                items.append(RawIntelData(
                    title=title,
                    url=url,
                    source=news.get("provider", [{}])[0].get("name", "Bing新闻"),
                    source_type="search",
                    pub_date=self._parse_iso_date(news.get("datePublished", "")),
                    content=news.get("description", ""),
                    summary=news.get("description", "")[:500],
                ))
        except Exception as e:
            logger.warning(f"Bing API搜索失败: {e}")
        return items

    def _deduplicate(self, items: List[RawIntelData]) -> List[RawIntelData]:
        seen_urls = set()
        unique_items = []
        for item in items:
            if item.url in seen_urls:
                continue
            seen_urls.add(item.url)
            unique_items.append(item)
        return unique_items

    def _is_valid_result(self, title: str, url: str) -> bool:
        if not title or not url or not url.startswith("http"):
            return False
        blocked = ("google.com/search", "bing.com/search", "duckduckgo.com", "youtube.com/shorts")
        if any(part in url for part in blocked):
            return False
        blocked_domains = (
            "wikipedia.org",
            "youtube.com",
            "youtu.be",
            "facebook.com",
            "x.com/",
            "twitter.com",
            "reddit.com",
            "zhihu.com",
            "bilibili.com",
        )
        if any(domain in url.lower() for domain in blocked_domains):
            return False
        if len(title.strip()) < 3 or len(title.strip()) > 220:
            return False
        return bool(re.search(r"[A-Za-z\u4e00-\u9fff]", title))

    def _is_relevant_result(self, query: str, title: str, summary: str, url: str) -> bool:
        if query.startswith("site:"):
            return True

        text = f"{query} {title} {summary} {url}".lower()
        relevance_terms = [
            "5g", "6g", "5g-a", "open ran", "oran", "ran", "telecom",
            "telecommunications", "optical", "800g", "1.6t", "module",
            "transceiver", "network", "base station", "wireless", "fiber",
            "通信", "电信", "光模块", "光通信", "基站", "中兴", "华为",
            "爱立信", "诺基亚", "运营商", "网络", "专利",
        ]
        return any(term in text for term in relevance_terms)

    def _parse_serper_date(self, value: str):
        if not value:
            return datetime.now()
        for fmt in ("%Y年%m月%d日", "%b %d, %Y", "%Y-%m-%d"):
            try:
                return datetime.strptime(value, fmt)
            except ValueError:
                continue
        return datetime.now()

    def _parse_iso_date(self, value: str):
        if not value:
            return datetime.now()
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return datetime.now()
