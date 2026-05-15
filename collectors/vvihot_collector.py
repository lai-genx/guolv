"""
识微商情/VviHot平台采集器。

该采集器通过已授权的平台账号读取现有监测主题下的文章列表，并统一转换为
RawIntelData，交给项目既有的去重、LLM分析、入库和周报流程处理。
"""
import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Set
from urllib.parse import parse_qs, urlparse

from bs4 import BeautifulSoup
from loguru import logger

from .base import BaseCollector, CollectorResult, RawIntelData, contains_keywords
from config import settings


MANAGED_TOPIC_DEFINITIONS = [
    {
        "name": "CT-无线接入与标准",
        "terms": ["5G", "6G", "5G-A", "5G Advanced", "Open RAN", "O-RAN", "vRAN", "RAN", "基站", "小基站", "射频", "天线", "3GPP", "ITU-R"],
        "keyword": (
            '(5G || 6G || "5G-A" || "5G Advanced" || "Open RAN" || "O-RAN" || vRAN || RAN || '
            '基站 || 小基站 || 射频 || 天线 || 3GPP || "ITU-R") && '
            "(发布 || 合作 || 中标 || 商用 || 部署 || 测试 || 研发 || 标准 || 专利 || 融资 || 收购)"
        ),
    },
    {
        "name": "CT-光通信",
        "terms": ["光通信", "光模块", "光芯片", "硅光", "CPO", "LPO", "OTN", "WDM", "DWDM", "相干光", "800G", "1.6T"],
        "keyword": (
            "(光通信 || 光模块 || 光芯片 || 硅光 || CPO || LPO || OTN || WDM || DWDM || "
            "相干光 || 800G || 1.6T) && "
            "(发布 || 量产 || 中标 || 合作 || 订单 || 扩产 || 研发 || 专利 || 融资 || 收购)"
        ),
    },
    {
        "name": "CT-核心网与承载",
        "terms": ["核心网", "5G Core", "UPF", "AMF", "SMF", "MEC", "网络切片", "云原生网络", "边缘计算", "传输网", "承载网", "IP承载", "PTN", "SPN", "路由器", "交换机", "DCI"],
        "keyword": (
            '(核心网 || "5G Core" || UPF || AMF || SMF || MEC || 网络切片 || 云原生网络 || '
            "边缘计算 || 传输网 || 承载网 || IP承载 || PTN || SPN || 路由器 || 交换机 || DCI) && "
            "(发布 || 部署 || 商用 || 合作 || 测试 || 升级 || 运营商 || 中标 || 扩容)"
        ),
    },
    {
        "name": "CT-通信芯片半导体",
        "terms": ["基带芯片", "射频芯片", "光芯片", "DSP", "FPGA", "SoC", "PA", "LNA", "滤波器", "通信芯片", "国产芯片"],
        "keyword": (
            "(基带芯片 || 射频芯片 || 光芯片 || DSP || FPGA || SoC || PA || LNA || 滤波器 || "
            "通信芯片 || 国产芯片) && "
            "(发布 || 量产 || 流片 || 订单 || 合作 || 融资 || 收购 || 专利 || 认证)"
        ),
    },
    {
        "name": "CT-物联网终端",
        "terms": ["物联网", "IoT", "模组", "5G模组", "CPE", "车联网", "V2X", "NTN", "卫星通信", "RedCap", "工业互联网"],
        "keyword": (
            "(物联网 || IoT || 模组 || 5G模组 || CPE || 车联网 || V2X || NTN || 卫星通信 || "
            "RedCap || 工业互联网) && "
            "(发布 || 商用 || 合作 || 认证 || 中标 || 出货 || 量产 || 部署)"
        ),
    },
]


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
        self.manage_topics = settings.collector.vvihot_manage_topics
        self.delete_unmanaged_topics = settings.collector.vvihot_delete_unmanaged_topics
        self.managed_topic_prefix = settings.collector.vvihot_managed_topic_prefix
        self.managed_topic_definitions = [
            topic
            for topic in MANAGED_TOPIC_DEFINITIONS
            if topic["name"].startswith(self.managed_topic_prefix)
        ]
        if self.manage_topics and not self.topic_names:
            self.topic_names = {topic["name"] for topic in self.managed_topic_definitions}

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
                await self._wait_until_authenticated(page)

                # 先主动读取主题列表；如开启托管模式，则把平台主题整理成通信领域主题池。
                topics_payload = await self._fetch_topics(page)
                if self.manage_topics:
                    topics_payload = await self._ensure_managed_topics(page, topics_payload)
                    await page.reload(wait_until="networkidle", timeout=60000)
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

    async def _wait_until_authenticated(self, page) -> None:
        """等待登录态真正可用于平台接口。"""
        for _ in range(20):
            payload = await self._fetch_topics(page)
            if payload and payload.get("success"):
                return
            await page.wait_for_timeout(1000)
        raise RuntimeError("VviHot登录后仍无法读取主题接口")

    async def _fetch_topics(self, page) -> Optional[Dict[str, Any]]:
        """直接读取平台主题列表，避免只依赖前端初始化事件"""
        try:
            return await page.evaluate(
                """async () => {
                    const r = await fetch('/swsq/topic/pagingByType?topicType=KEYWORDS', {
                        credentials: 'include'
                    });
                    const text = await r.text();
                    try {
                        return JSON.parse(text);
                    } catch (e) {
                        return {success: false, msg: text.slice(0, 200)};
                    }
                }"""
            )
        except Exception as e:
            logger.debug(f"读取VviHot主题列表失败: {e}")
            return None

    async def _ensure_managed_topics(self, page, topics_payload: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """确保平台上保留的是项目托管的通信领域主题。"""
        topics_payload = topics_payload or await self._fetch_topics(page)
        topics = self._extract_topics(topics_payload)

        if self.delete_unmanaged_topics:
            for topic in topics:
                if not self._is_deletable_topic(topic):
                    continue
                if self._is_managed_topic(topic):
                    continue
                if await self._remove_topic(page, topic):
                    logger.info(f"VviHot已删除非托管主题: {self._topic_label(topic)}")

            topics_payload = await self._fetch_topics(page)
            topics = self._extract_topics(topics_payload)

        for definition in self.managed_topic_definitions:
            if any(self._topic_matches_definition(topic, definition) for topic in topics):
                continue

            added = await self._add_topic(page, definition)
            if added:
                logger.info(f"VviHot已创建托管主题: {definition['name']}")
                continue

            # 账号主题数量有限时，优先清理剩余非托管主题后重试一次。
            if self.delete_unmanaged_topics:
                refreshed = self._extract_topics(await self._fetch_topics(page))
                removable = next(
                    (
                        topic
                        for topic in refreshed
                        if self._is_deletable_topic(topic) and not self._is_managed_topic(topic)
                    ),
                    None,
                )
                if removable and await self._remove_topic(page, removable):
                    if await self._add_topic(page, definition):
                        logger.info(f"VviHot清理额度后已创建托管主题: {definition['name']}")

        return await self._fetch_topics(page)

    async def _add_topic(self, page, definition: Dict[str, str]) -> bool:
        """通过识微商情接口创建关键词主题。"""
        try:
            result = await page.evaluate(
                """async ({name, keyword}) => {
                    const body = new URLSearchParams();
                    body.set('topic[keyword]', keyword);
                    body.set('topic[name]', name);
                    body.set('topic[topicType]', 'KEYWORDS');
                    body.set('topic[scope]', 'JN');
                    body.set('topic[mediaType]', 'ALL');
                    const r = await fetch('/swsq/topic/add', {
                        method: 'POST',
                        credentials: 'include',
                        headers: {'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'},
                        body: body.toString()
                    });
                    return await r.json();
                }""",
                definition,
            )
            if result and result.get("success"):
                return True
            logger.warning(f"VviHot创建主题失败: {definition['name']} - {result}")
            return False
        except Exception as e:
            logger.warning(f"VviHot创建主题异常: {definition['name']} - {e}")
            return False

    async def _remove_topic(self, page, topic: Dict[str, Any]) -> bool:
        """通过识微商情接口删除关键词主题。"""
        topic_id = topic.get("topicId")
        if not topic_id:
            return False

        try:
            result = await page.evaluate(
                """async (topicId) => {
                    const body = new URLSearchParams();
                    body.set('topicId', topicId);
                    const r = await fetch('/swsq/topic/remove', {
                        method: 'POST',
                        credentials: 'include',
                        headers: {'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'},
                        body: body.toString()
                    });
                    return await r.json();
                }""",
                topic_id,
            )
            return bool(result and result.get("success"))
        except Exception as e:
            logger.warning(f"VviHot删除主题异常: {topic.get('name') or topic_id} - {e}")
            return False

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
        for topic in self._extract_topics(payload):
            topic_id = topic.get("topicId")
            name = self._topic_label(topic)
            if topic_id and name:
                lookup[topic_id] = name
        return lookup

    def _extract_topics(self, payload: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not payload or not payload.get("success"):
            return []
        topics = payload.get("data") or []
        return topics if isinstance(topics, list) else []

    def _is_visible_keyword_topic(self, topic: Dict[str, Any]) -> bool:
        return topic.get("topicType") == "KEYWORDS" and topic.get("status") == "SHOW"

    def _is_deletable_topic(self, topic: Dict[str, Any]) -> bool:
        topic_id = topic.get("topicId", "")
        if topic_id in {"REPORT_DATA", "HOT_EVENT"}:
            return False
        return self._is_visible_keyword_topic(topic)

    def _is_managed_topic(self, topic: Dict[str, Any]) -> bool:
        return any(self._topic_matches_definition(topic, definition) for definition in self.managed_topic_definitions)

    def _topic_matches_definition(self, topic: Dict[str, Any], definition: Dict[str, str]) -> bool:
        name = topic.get("name") or topic.get("topicDisplay", {}).get("displayName") or ""
        if name == definition["name"]:
            return True
        return self._normalize_topic_keyword(topic.get("keywords", "")) == self._normalize_topic_keyword(definition["keyword"])

    def _topic_label(self, topic: Dict[str, Any]) -> str:
        name = topic.get("name") or topic.get("topicDisplay", {}).get("displayName") or ""
        if name:
            return name

        keyword = topic.get("keywords") or ""
        normalized = self._normalize_topic_keyword(keyword)
        for definition in self.managed_topic_definitions:
            if normalized == self._normalize_topic_keyword(definition["keyword"]):
                return definition["name"]
        return keyword

    def _normalize_topic_keyword(self, keyword: str) -> str:
        return "".join(str(keyword or "").split())

    def _passes_managed_topic_filter(self, topic_name: str, text: str) -> bool:
        definition = next(
            (definition for definition in self.managed_topic_definitions if definition["name"] == topic_name),
            None,
        )
        if not definition:
            return True

        lower_text = text.lower()
        return any(self._term_in_text(term, lower_text) for term in definition.get("terms", []))

    def _term_in_text(self, term: str, lower_text: str) -> bool:
        lower_term = term.lower()
        if re.fullmatch(r"[a-z0-9][a-z0-9.+-]{1,8}", lower_term):
            return re.search(rf"(?<![a-z0-9]){re.escape(lower_term)}(?![a-z0-9])", lower_text) is not None
        return lower_term in lower_text

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
        if self.topic_names and topic_name not in self.topic_names:
            return None

        searchable_text = f"{title} {content_text}"
        if self.manage_topics and topic_name and not self._passes_managed_topic_filter(topic_name, searchable_text):
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
