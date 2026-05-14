"""
识微商情/VviHot平台采集器。

该采集器通过已授权的平台账号读取现有监测主题下的文章列表，并统一转换为
RawIntelData，交给项目既有的去重、LLM分析、入库和周报流程处理。
"""
from datetime import datetime
from typing import Any, Dict, List, Optional, Set
from urllib.parse import parse_qs, urlparse

from bs4 import BeautifulSoup
from loguru import logger

from .base import BaseCollector, CollectorResult, RawIntelData, contains_keywords
from config import settings


class VviHotCollector(BaseCollector):
    """识微商情/VviHot平台采集器"""

    def __init__(self):
        super().__init__("vvihot")
        self.platform_url = settings.collector.vvihot_url.rstrip("/") + "/"
        self.username = settings.collector.vvihot_username
        self.password = settings.collector.vvihot_password
        self.headless = settings.collector.vvihot_headless
        self.wait_seconds = settings.collector.vvihot_wait_seconds
        self.max_items = settings.collector.vvihot_max_items
        self.topic_names = self._parse_topic_names(settings.collector.vvihot_topic_names)

    async def collect(self, **kwargs) -> CollectorResult:
        """从识微商情平台采集已配置监测主题下的文章"""
        if not self.username or not self.password:
            return CollectorResult(
                items=[],
                success=False,
                message="VviHot未配置账号或密码，请设置 COLLECTOR__VVIHOT_USERNAME/PASSWORD",
                total_found=0,
            )

        max_items = kwargs.get("max_items", self.max_items)

        try:
            from playwright.async_api import async_playwright
        except ImportError:
            return CollectorResult(
                items=[],
                success=False,
                message="未安装playwright，请先执行 pip install playwright 并安装浏览器",
                total_found=0,
            )

        captured_docs: List[Dict[str, Any]] = []
        topic_lookup: Dict[str, str] = {}

        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=self.headless)
                context = await browser.new_context(
                    viewport={"width": 1600, "height": 1000},
                    user_agent=(
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/120.0.0.0 Safari/537.36"
                    ),
                )
                page = await context.new_page()

                async def on_response(response):
                    url = response.url
                    if "/swsq/topic/pagingByType" in url:
                        topics = await self._safe_json_response(response)
                        if topics:
                            topic_lookup.update(self._extract_topic_lookup(topics))
                        return

                    if "/swsq/topic/pagingSummary" not in url:
                        return

                    payload = await self._safe_json_response(response)
                    if not payload or not payload.get("success"):
                        return

                    docs = payload.get("data") or []
                    if isinstance(docs, list):
                        topic_id = self._topic_id_from_url(url)
                        topic_name = topic_lookup.get(topic_id, "")
                        for doc in docs:
                            if topic_id:
                                doc["_vvihot_topic_id"] = topic_id
                            if topic_name:
                                doc["_vvihot_topic_name"] = topic_name
                        captured_docs.extend(docs)

                page.on("response", on_response)

                await page.goto(self.platform_url, wait_until="networkidle", timeout=60000)
                await self._login_if_needed(page)

                # 先主动读取主题列表，随后触发一次页面监测刷新。
                topics_payload = await self._fetch_topics(page)
                if topics_payload:
                    topic_lookup.update(self._extract_topic_lookup(topics_payload))

                await self._trigger_topic_refresh(page, topic_lookup)

                # 平台主题数据异步加载，等待前端触发 pagingSummary 接口。
                await page.wait_for_timeout(max(1, self.wait_seconds) * 1000)

                await context.close()
                await browser.close()

        except Exception as e:
            logger.error(f"VviHot采集失败: {e}")
            hint = "请确认已执行 python -m playwright install chromium，且账号可正常登录"
            return CollectorResult(items=[], success=False, message=f"VviHot采集失败: {e}。{hint}", total_found=0)

        items = self._convert_documents(captured_docs, topic_lookup, max_items)

        return CollectorResult(
            items=items,
            success=len(items) > 0,
            message=f"VviHot采集完成，获取 {len(items)}/{len(captured_docs)} 条有效内容",
            total_found=len(captured_docs),
        )

    async def _login_if_needed(self, page) -> None:
        """如页面跳转到登录页，则填写账号密码并登录"""
        body_text = ""
        try:
            body_text = await page.locator("body").inner_text(timeout=10000)
        except Exception:
            pass

        input_count = await page.locator("input").count()
        if "/auth" not in page.url and "login" not in page.url.lower() and input_count < 2:
            return

        logger.info("VviHot需要登录，正在使用配置账号登录")
        inputs = page.locator("input")
        await inputs.nth(0).fill(self.username)
        await inputs.nth(1).fill(self.password)

        button = page.locator("button").first
        if await button.count():
            await button.click()
        elif "登录" in body_text:
            await page.get_by_text("登录", exact=False).first.click()
        else:
            await page.keyboard.press("Enter")

        await page.wait_for_load_state("networkidle", timeout=60000)

    async def _fetch_topics(self, page) -> Optional[Dict[str, Any]]:
        """直接读取平台主题列表，避免只依赖前端初始化事件"""
        try:
            return await page.evaluate(
                """async () => {
                    const r = await fetch('/swsq/topic/pagingByType?topicType=KEYWORDS', {
                        credentials: 'include'
                    });
                    return await r.json();
                }"""
            )
        except Exception as e:
            logger.debug(f"读取VviHot主题列表失败: {e}")
            return None

    async def _trigger_topic_refresh(self, page, topic_lookup: Dict[str, str]) -> None:
        """
        触发平台前端刷新主题文章。

        识微商情的桌面看板会在用户点击“监测”后异步加载各主题的 pagingSummary
        接口；无头浏览器首次进入时该接口有时不会自动触发，因此这里模拟一次轻量
        的监测操作。若主题已存在或数量超限，平台会返回错误，但仍会刷新看板数据。
        """
        try:
            keyword = next((name for name in topic_lookup.values() if name), "5G")
            await page.mouse.click(240, 25)
            await page.keyboard.press("Control+A")
            await page.keyboard.type(keyword)
            await page.mouse.click(720, 25)
            await page.wait_for_timeout(2000)
        except Exception as e:
            logger.debug(f"触发VviHot主题刷新失败: {e}")

    async def _safe_json_response(self, response) -> Optional[Dict[str, Any]]:
        try:
            return await response.json()
        except Exception:
            return None

    def _extract_topic_lookup(self, payload: Dict[str, Any]) -> Dict[str, str]:
        lookup = {}
        for topic in payload.get("data") or []:
            topic_id = topic.get("topicId")
            name = topic.get("name") or topic.get("topicDisplay", {}).get("displayName")
            if topic_id and name:
                lookup[topic_id] = name
        return lookup

    def _convert_documents(
        self,
        docs: List[Dict[str, Any]],
        topic_lookup: Dict[str, str],
        max_items: int,
    ) -> List[RawIntelData]:
        seen: Set[str] = set()
        items: List[RawIntelData] = []

        for doc in docs:
            if len(items) >= max_items:
                break

            item = self._document_to_item(doc, topic_lookup)
            if not item:
                continue

            dedupe_key = item.url or item.title
            if dedupe_key in seen:
                continue
            seen.add(dedupe_key)

            # 平台会返回泛舆情内容，这里保留一层项目关键词过滤，减少无关噪声。
            if not contains_keywords(f"{item.title} {item.summary} {item.content}"):
                continue

            items.append(item)

        return items

    def _document_to_item(self, doc: Dict[str, Any], topic_lookup: Dict[str, str]) -> Optional[RawIntelData]:
        title = (doc.get("title") or "").strip()
        content_html = doc.get("content") or ""
        content_text = self._html_to_text(content_html)

        if not title:
            title = content_text[:80].strip()

        url = (doc.get("url") or "").strip()
        if not title or not url:
            return None

        topic_id = self._extract_topic_id(doc)
        topic_name = doc.get("_vvihot_topic_name") or (topic_lookup.get(topic_id, "") if topic_id else "")
        if self.topic_names and topic_name and topic_name not in self.topic_names:
            return None

        source = doc.get("websiteName") or doc.get("domain") or "识微商情"
        pub_date = self._parse_platform_time(doc.get("createdAt") or doc.get("createTime"))

        summary_parts = [
            f"平台来源: {source}",
            f"媒体类型: {doc.get('mediaType', '')}",
        ]
        if topic_name:
            summary_parts.append(f"监测主题: {topic_name}")
        if content_text:
            summary_parts.append(content_text[:300])

        return RawIntelData(
            title=title,
            url=url,
            source=source,
            source_type="vvihot",
            pub_date=pub_date,
            content=content_text,
            summary="\n".join(part for part in summary_parts if part),
        )

    def _extract_topic_id(self, doc: Dict[str, Any]) -> str:
        for key in ("_vvihot_topic_id", "topicId", "fromTopicId"):
            value = doc.get(key)
            if isinstance(value, str) and value:
                return value
        return ""

    def _topic_id_from_url(self, url: str) -> str:
        try:
            query = parse_qs(urlparse(url).query)
            values = query.get("topicId") or []
            return values[0] if values else ""
        except Exception:
            return ""

    def _html_to_text(self, html: str) -> str:
        if not html:
            return ""
        soup = BeautifulSoup(html, "lxml")
        for tag in soup(["script", "style", "img"]):
            tag.decompose()
        return soup.get_text("\n", strip=True)

    def _parse_platform_time(self, value: Any) -> Optional[datetime]:
        if value in (None, ""):
            return None

        try:
            timestamp = int(value)
        except (TypeError, ValueError):
            return None

        # 平台有时返回毫秒，有时返回秒。
        if timestamp > 10_000_000_000:
            timestamp = timestamp // 1000

        try:
            return datetime.fromtimestamp(timestamp)
        except (OverflowError, OSError, ValueError):
            return None

    def _parse_topic_names(self, raw: str) -> Set[str]:
        if not raw:
            return set()
        return {name.strip() for name in raw.split(",") if name.strip()}
