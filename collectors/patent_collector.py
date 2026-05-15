"""
专利线索采集器。

当前实现以公开搜索结果为主，面向 Google Patents、EPO Espacenet 等公开页面
采集通信设备相关专利线索。若后续接入 EPO OPS API，可在本采集器内扩展
认证请求逻辑，并保持输出 RawIntelData 不变。
"""
from datetime import datetime
from typing import List
import asyncio
import csv
import io
import json
import re
import urllib.parse

from loguru import logger

from .base import BaseCollector, CollectorResult, RawIntelData, contains_keywords
from config import settings


class PatentCollector(BaseCollector):
    """公开专利线索采集器"""

    def __init__(self):
        super().__init__("patent")
        self.serper_calls = 0

    async def collect(self, **kwargs) -> CollectorResult:
        all_items: List[RawIntelData] = []
        max_queries = kwargs.get("max_queries", settings.collector.patent_max_queries)
        max_results_per_query = kwargs.get("max_results_per_query", settings.collector.patent_max_results_per_query)
        per_query_timeout = kwargs.get("per_query_timeout", settings.collector.patent_per_query_timeout)

        all_queries = self._build_patent_queries()
        queries = all_queries[:max_queries] if max_queries and max_queries > 0 else all_queries

        for query in queries:
            try:
                logger.info(f"采集专利线索: {query}")
                items = await asyncio.wait_for(
                    self._search_patents(query, max_results_per_query),
                    timeout=per_query_timeout
                )
                all_items.extend(items)
                logger.info(f"专利查询 '{query}' 获取 {len(items)} 条线索")
            except asyncio.TimeoutError:
                logger.warning(f"专利查询超时，已跳过: {query}")
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
        logger.info(f"PatentCollector本轮Serper调用次数: {self.serper_calls}")

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
        if settings.collector.serper_api_key:
            serper_items = await self._search_serper_patents(query, max_results)
            if serper_items:
                return serper_items

        if settings.collector.jina_api_key:
            jina_items = await self._search_jina_patents(query, max_results)
            if jina_items:
                return jina_items
            return []

        google_items = await self._search_google_patents(query, max_results)
        if google_items:
            return google_items

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

    async def _search_serper_patents(self, query: str, max_results: int) -> List[RawIntelData]:
        """使用 Serper 搜索公开专利页面。"""
        url = "https://google.serper.dev/search"
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
            logger.warning(f"Serper专利搜索失败 '{query}': {e}")
            return []

        items: List[RawIntelData] = []
        seen_urls = set()
        for row in data.get("organic") or []:
            if len(items) >= max_results:
                break
            title = (row.get("title") or "").strip()
            url_value = (row.get("link") or "").strip()
            if not title or not url_value:
                continue
            if "patents.google.com" not in url_value and "espacenet" not in url_value:
                continue
            if url_value in seen_urls:
                continue

            seen_urls.add(url_value)
            summary = (row.get("snippet") or "").strip()
            items.append(RawIntelData(
                title=title,
                url=url_value,
                source=row.get("source") or "Serper专利搜索",
                source_type="patent",
                pub_date=self._parse_patent_date(row.get("date") or ""),
                content=summary,
                summary=summary[:500],
            ))

        return items

    async def _search_jina_patents(self, query: str, max_results: int) -> List[RawIntelData]:
        """使用 Jina Search 作为公开专利搜索备用源。"""
        jina_api_key = settings.collector.jina_api_key
        if not jina_api_key:
            return []

        encoded_query = urllib.parse.quote(query)
        url = f"https://s.jina.ai/?q={encoded_query}"
        headers = {
            "Authorization": f"Bearer {jina_api_key}",
            "Accept": "text/plain; charset=utf-8",
            "Accept-Encoding": "identity",
        }

        try:
            response = await self.client.get(url, headers=headers, timeout=12)
            response.raise_for_status()
        except Exception as e:
            logger.debug(f"Jina专利搜索失败 '{query}': {e}")
            return []

        return self._parse_jina_search_results(response.text or "", max_results)

    def _parse_jina_search_results(self, text: str, max_results: int) -> List[RawIntelData]:
        blocks = re.split(r"\n(?=\[\d+\]\s+Title:)", text)
        items: List[RawIntelData] = []
        seen_urls = set()

        for block in blocks:
            if len(items) >= max_results:
                break

            title_match = re.search(r"\[\d+\]\s+Title:\s*(.+)", block)
            url_match = re.search(r"\[\d+\]\s+URL Source:\s*(https?://\S+)", block)
            desc_match = re.search(r"\[\d+\]\s+Description:\s*(.+?)(?:\n\[\d+\]\s+Date:|\n##|\Z)", block, re.S)
            date_match = re.search(r"\[\d+\]\s+Date:\s*(.+)", block)

            if not title_match or not url_match:
                continue

            url = url_match.group(1).strip()
            if "patents.google.com" not in url and "espacenet" not in url:
                continue
            if url in seen_urls:
                continue

            title = title_match.group(1).strip()
            summary = self._extract_text(desc_match.group(1) if desc_match else "")
            pub_date = self._parse_patent_date(date_match.group(1).strip() if date_match else "")
            seen_urls.add(url)

            items.append(RawIntelData(
                title=title,
                url=url,
                source="Jina专利搜索",
                source_type="patent",
                pub_date=pub_date,
                content=summary,
                summary=summary[:500]
            ))

        return items

    async def _search_google_patents(self, query: str, max_results: int) -> List[RawIntelData]:
        """优先使用 Google Patents XHR 接口，避免搜索页反爬导致 0 结果。"""
        clean_query = self._clean_patent_query(query)
        if not clean_query:
            return []

        encoded = urllib.parse.quote(f"q={clean_query}", safe="")
        urls = [
            f"https://patents.google.com/xhr/query?url={encoded}&exp=",
            f"https://patents.google.com/xhr/query?url={encoded}&exp=&download=true",
        ]

        for url in urls:
            try:
                response = await self.client.get(url)
                response.raise_for_status()
            except Exception as e:
                logger.debug(f"Google Patents查询失败 '{clean_query}': {e}")
                continue

            text = response.text or ""
            items = self._parse_google_patents_response(text, max_results)
            if items:
                return items

        return []

    def _parse_google_patents_response(self, text: str, max_results: int) -> List[RawIntelData]:
        stripped = text.lstrip()
        if not stripped:
            return []

        if stripped.startswith("{"):
            try:
                return self._parse_google_patents_json(json.loads(stripped), max_results)
            except Exception as e:
                logger.debug(f"解析Google Patents JSON失败: {e}")
                return []

        if "publication" not in text.lower() and "title" not in text.lower():
            return []

        items: List[RawIntelData] = []
        reader = csv.DictReader(io.StringIO(text))
        for row in reader:
            if len(items) >= max_results:
                break

            publication = (
                row.get("publication number")
                or row.get("Publication Number")
                or row.get("id")
                or ""
            ).strip()
            title = (row.get("title") or row.get("Title") or publication).strip()
            assignee = (row.get("assignee") or row.get("Assignee") or "").strip()
            summary = " | ".join(part for part in [assignee, row.get("snippet", ""), row.get("abstract", "")] if part)

            if not publication or not title:
                continue

            items.append(RawIntelData(
                title=title,
                url=f"https://patents.google.com/patent/{publication}",
                source="Google Patents",
                source_type="patent",
                pub_date=datetime.now(),
                content=summary,
                summary=summary[:500]
            ))

        return items

    def _parse_google_patents_json(self, data: dict, max_results: int) -> List[RawIntelData]:
        results = data.get("results", data)
        clusters = results.get("cluster") or results.get("clusters") or []

        rows = []
        for cluster in clusters:
            if isinstance(cluster, dict):
                cluster_results = cluster.get("result") or cluster.get("results") or []
                rows.extend(item for item in cluster_results if isinstance(item, dict))

        if not rows and isinstance(results.get("result"), list):
            rows = [item for item in results["result"] if isinstance(item, dict)]

        items: List[RawIntelData] = []
        for row in rows:
            if len(items) >= max_results:
                break

            publication = self._extract_publication_number(row)
            title = self._extract_text(row.get("title") or row.get("patentTitle") or publication)
            snippet = self._extract_text(row.get("snippet") or row.get("abstract") or "")
            assignee = self._extract_text(row.get("assignee") or row.get("owner") or "")
            summary = " | ".join(part for part in [assignee, snippet] if part)

            if not publication or not title:
                continue

            items.append(RawIntelData(
                title=title,
                url=f"https://patents.google.com/patent/{publication}",
                source="Google Patents",
                source_type="patent",
                pub_date=datetime.now(),
                content=summary,
                summary=summary[:500]
            ))

        return items

    def _extract_publication_number(self, row: dict) -> str:
        patent = row.get("patent")
        if isinstance(patent, dict):
            for key in ("publication_number", "publicationNumber", "id", "publication"):
                value = self._extract_text(patent.get(key, ""))
                if value:
                    return value

        for key in ("publication_number", "publicationNumber", "publication", "id", "patent_id"):
            value = self._extract_text(row.get(key, ""))
            if value:
                return value
        return ""

    def _extract_text(self, value) -> str:
        if value is None:
            return ""
        if isinstance(value, dict):
            value = value.get("text") or value.get("html") or value.get("value") or ""
        if isinstance(value, list):
            value = " ".join(self._extract_text(item) for item in value)
        return re.sub(r"<[^>]+>", " ", str(value)).strip()

    def _parse_patent_date(self, value: str):
        if not value:
            return datetime.now()
        for fmt in ("%b %d, %Y", "%Y-%m-%d", "%Y/%m/%d"):
            try:
                return datetime.strptime(value, fmt)
            except ValueError:
                continue
        return datetime.now()

    def _clean_patent_query(self, query: str) -> str:
        clean = re.sub(r"site:\S+", " ", query)
        clean = clean.replace(" OR ", " ")
        return re.sub(r"\s+", " ", clean).strip()
