"""
专利线索采集器。

当前实现以公开搜索结果为主，面向 Google Patents、EPO Espacenet 等公开页面
采集通信设备相关专利线索。若后续接入 EPO OPS API，可在本采集器内扩展
认证请求逻辑，并保持输出 RawIntelData 不变。
"""
from datetime import datetime
from typing import List
import urllib.parse

from loguru import logger

from .base import BaseCollector, CollectorResult, RawIntelData, contains_keywords
from config import settings


class PatentCollector(BaseCollector):
    """公开专利线索采集器"""

    def __init__(self):
        super().__init__("patent")

    async def collect(self, **kwargs) -> CollectorResult:
        all_items: List[RawIntelData] = []
        max_queries = kwargs.get("max_queries", 8)
        max_results_per_query = kwargs.get("max_results_per_query", 5)

        queries = self._build_patent_queries()[:max_queries]

        for query in queries:
            try:
                logger.info(f"采集专利线索: {query}")
                items = await self._search_patents(query, max_results_per_query)
                all_items.extend(items)
                logger.info(f"专利查询 '{query}' 获取 {len(items)} 条线索")
            except Exception as e:
                logger.warning(f"专利查询失败 '{query}': {e}")

        seen_urls = set()
        unique_items = []
        for item in all_items:
            if item.url not in seen_urls:
                seen_urls.add(item.url)
                unique_items.append(item)

        filtered_items = [
            item for item in unique_items
            if contains_keywords(item.title + " " + item.summary)
        ]

        return CollectorResult(
            items=filtered_items,
            success=len(filtered_items) > 0,
            message=f"专利线索采集完成，过滤后 {len(filtered_items)}/{len(unique_items)} 条",
            total_found=len(unique_items)
        )

    def _build_patent_queries(self) -> List[str]:
        base_queries = [
            "site:patents.google.com 5G base station patent",
            "site:patents.google.com optical module patent",
            "site:patents.google.com Open RAN patent",
            "site:patents.google.com 6G wireless communication patent",
            "site:worldwide.espacenet.com 5G communication equipment",
            "site:worldwide.espacenet.com optical communication module",
        ]

        company_queries = []
        for company in (settings.collector.target_companies or [])[:12]:
            company_queries.append(f'site:patents.google.com "{company}" 5G OR optical communication')

        return base_queries + company_queries

    async def _search_patents(self, query: str, max_results: int) -> List[RawIntelData]:
        encoded_query = urllib.parse.quote(query)
        search_url = f"https://www.bing.com/search?q={encoded_query}&count={max_results}"

        html = await self.fetch_html(search_url)
        if not html:
            return []

        soup = self.parse_html(html)
        candidates = soup.select(".b_algo, li.b_algo, article, h2, h3")[: max_results * 3]
        items: List[RawIntelData] = []

        for elem in candidates:
            if len(items) >= max_results:
                break

            link_elem = elem.select_one("h2 a[href], h3 a[href], a[href]")
            if not link_elem:
                continue

            title = link_elem.get_text(strip=True)
            url = link_elem.get("href", "")

            if not title or not url.startswith("http"):
                continue
            if "patents.google.com" not in url and "espacenet" not in url:
                continue

            summary = ""
            snippet = elem.select_one("p, .b_caption, .b_snippet")
            if snippet:
                summary = snippet.get_text(" ", strip=True)

            items.append(RawIntelData(
                title=title,
                url=url,
                source="专利公开检索",
                source_type="patent",
                pub_date=datetime.now(),
                content=summary,
                summary=summary[:500]
            ))

        return items
