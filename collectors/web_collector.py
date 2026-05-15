"""
网页采集器 - 从竞争对手官网采集新闻
增强版: 支持多URL fallback + Jina Reader API fallback
"""
from datetime import datetime
from typing import List, Optional, Dict
from urllib.parse import urljoin
import asyncio
import re

import httpx
from httpx import ConnectTimeout
from bs4 import BeautifulSoup
from loguru import logger
from playwright.async_api import async_playwright

from .base import BaseCollector, CollectorResult, RawIntelData, contains_keywords
from .web_sites_config import DEFAULT_SITES
from config import settings


class WebCollector(BaseCollector):
    """网页采集器 - 采集竞争对手官网新闻"""

    def __init__(self):
        super().__init__("web")
        self.sites = DEFAULT_SITES

    async def collect(self, **kwargs) -> CollectorResult:
        """从网页采集情报"""
        all_items = []
        success_count = 0

        max_per_site = kwargs.get('max_per_site', 5)
        max_sites = kwargs.get('max_sites', settings.collector.web_max_sites)
        per_site_timeout = kwargs.get('per_site_timeout', settings.collector.web_per_site_timeout)
        sites = self.sites[:max_sites] if max_sites and max_sites > 0 else self.sites

        for site in sites:
            try:
                logger.info(f"采集网站: {site['name']}")
                items = await asyncio.wait_for(
                    self._collect_site(site, max_per_site),
                    timeout=max(5, per_site_timeout),
                )
                all_items.extend(items)
                if items:  # 仅当有数据时才算成功
                    success_count += 1
                logger.info(f"从 {site['name']} 获取 {len(items)} 条数据")
            except asyncio.TimeoutError:
                logger.warning(f"采集网站超时 {site['name']}，已跳过")
            except Exception as e:
                logger.error(f"采集网站失败 {site['name']}: {e}")

        # 关键词过滤
        filtered_items = [item for item in all_items if contains_keywords(item.title + item.summary)]

        return CollectorResult(
            items=filtered_items,
            success=success_count > 0,
            message=f"成功采集 {success_count}/{len(sites)} 个网站，过滤后 {len(filtered_items)}/{len(all_items)} 条",
            total_found=len(all_items)
        )

    async def _collect_site(self, site_config: Dict, max_items: int) -> List[RawIntelData]:
        """采集单个网站，支持多URL fallback和Jina Reader"""
        items = []

        # 检查是否强制使用Jina Reader
        if site_config.get('use_jina_only', False):
            logger.debug(f"使用Jina Reader (强制): {site_config['name']}")
            html = await self._fetch_via_jina(site_config['url'])
            if not html:
                logger.debug(f"Jina Reader不可用，改用 Playwright 渲染: {site_config['name']}")
                html = await self._fetch_via_playwright(site_config['url'])
        else:
            # 第一步: 尝试主URL
            html = await self.fetch_html(site_config['url'])

            # 第二步: 如果失败，尝试备选URL (如果有)
            if not html and 'alternative_urls' in site_config:
                logger.debug(f"主URL失败，尝试备选URL: {site_config['name']}")
                for alt_url in site_config['alternative_urls']:
                    html = await self.fetch_html(alt_url)
                    if html:
                        logger.debug(f"备选URL成功: {alt_url}")
                        break

            # 第三步: 如果仍然失败，尝试Jina Reader
            if not html:
                logger.debug(f"所有URL失败，尝试Jina Reader: {site_config['name']}")
                html = await self._fetch_via_jina(site_config['url'])

            # 第四步: 如果 Jina 失败，尝试 Playwright 渲染
            if not html:
                logger.debug(f"Jina Reader 失败，尝试 Playwright 渲染: {site_config['name']}")
                html = await self._fetch_via_playwright(site_config['url'])

        if not html:
            logger.warning(f"无法采集网站 {site_config['name']}: 所有方法都失败")
            return items

        # 判断是 HTML 还是 Markdown (Jina Reader 返回 Markdown)
        if html.startswith("Title:") or "Markdown Content:" in html or html.startswith("#"):
            # Jina Reader 返回的 Markdown 格式
            logger.debug(f"检测到 Markdown 格式内容: {site_config['name']}")
            items = self._parse_markdown_content(html, site_config, max_items)
        else:
            # 标准 HTML 格式
            soup = self.parse_html(html)
            # 查找新闻列表
            news_elements = soup.select(site_config['list_selector'])[:max_items]

            for elem in news_elements:
                try:
                    item = self._parse_news_element(elem, site_config)
                    if item:
                        items.append(item)
                except Exception as e:
                    logger.debug(f"解析新闻元素失败: {e}")
                    continue

            if not items:
                items = self._parse_generic_links(soup, site_config, max_items)

        return items

    def _parse_markdown_content(self, markdown_text: str, site_config: Dict, max_items: int) -> List[RawIntelData]:
        """解析 Jina Reader 返回的 Markdown 格式内容"""
        items = []

        # 提取 Markdown Content 部分
        if "Markdown Content:" in markdown_text:
            content = markdown_text.split("Markdown Content:")[-1]
        else:
            content = markdown_text

        # 提取标题区域的元数据（Date、Published等）
        meta_date = self._extract_date_from_meta(markdown_text)

        base_url = site_config.get('base_url', '')

        # Markdown 中的链接模式: [标题](URL)，兼容相对链接
        link_pattern = re.compile(r'\[([^\]]+)\]\(([^\)]+)\)')
        matches = link_pattern.findall(content)
        seen_urls = set()

        for title, raw_url in matches:
            if len(items) >= max_items:
                break

            url = urljoin(base_url or site_config.get('url', ''), raw_url.strip())

            # 过滤非新闻链接（导航、footer等）
            if url in seen_urls:
                continue
            if not self._is_candidate_news_link(title, url):
                continue
            seen_urls.add(url)

            # 提取摘要（取标题后的简短描述）
            summary = ""
            pub_date = meta_date  # 使用元数据中的日期

            title_pos = content.find(f'[{title}]({raw_url})')
            if title_pos > 0:
                # 取链接前后的文本作为上下文
                start = max(0, title_pos - 300)
                end = min(len(content), title_pos + len(url) + 10)
                context = content[start:end]

                # 尝试从上下文中提取日期
                if not pub_date:
                    pub_date = self._extract_date_from_context(context)

                # 提取链接前后的第一行作为摘要
                lines = context.split('\n')
                for line in lines:
                    if line.strip() and not line.strip().startswith('#') and not line.strip().startswith('*'):
                        summary = line.strip()[:200]
                        break

            item = RawIntelData(
                title=title.strip(),
                url=url.strip(),
                source=site_config['name'],
                source_type="web",
                pub_date=pub_date,
                content=summary,
                summary=summary[:500] if summary else title.strip()
            )
            items.append(item)

        return items

    def _parse_generic_links(self, soup: BeautifulSoup, site_config: Dict, max_items: int) -> List[RawIntelData]:
        items = []
        seen_urls = set()
        base_url = site_config.get("base_url") or site_config.get("url", "")

        for link in soup.find_all("a", href=True):
            if len(items) >= max_items:
                break

            title = link.get_text(" ", strip=True)
            url = urljoin(base_url, link.get("href", ""))
            if not title or url in seen_urls:
                continue
            if not self._is_candidate_news_link(title, url):
                continue

            seen_urls.add(url)
            context = link.find_parent(["article", "li", "div", "section"])
            summary = ""
            pub_date = None
            if context:
                summary = context.get_text(" ", strip=True)[:300]
                pub_date = self._extract_date_from_context(summary)

            items.append(RawIntelData(
                title=title[:180],
                url=url,
                source=site_config['name'],
                source_type="web",
                pub_date=pub_date,
                content=summary,
                summary=summary[:500] if summary else title[:180]
            ))

        return items

    def _is_candidate_news_link(self, title: str, url: str) -> bool:
        title_lower = (title or "").strip().lower()
        url_lower = (url or "").lower()

        if not title_lower or len(title_lower) < 4:
            return False
        if title_lower.startswith("!["):
            return False
        generic_titles = {
            "cisco.com worldwide", "products and services", "explore cisco",
            "innovation", "technology insights and reports", "other reports",
            "our solutions", "support", "contact us", "about us",
            "press releases", "ericsson blog", "events", "shaping history",
            "people and places", "products", "newsroom"
        }
        if title_lower in generic_titles:
            return False
        if any(skip in url_lower for skip in ['javascript:', '#', 'tel:', 'mailto:', 'privacy', 'cookie', 'login']):
            return False
        if any(skip in title_lower for skip in ['skip to', 'copyright', 'privacy', 'terms', 'subscribe', '登录']):
            return False
        if any(token in url_lower for token in [
            'filter-results', '/events', '/rss', '/blogs', '/executives',
            '/contacts', '/press-room', '/podcasts', '/reports', '/people.html'
        ]):
            return False
        if url_lower.endswith(('press-releases.html', '/news/', '/news', '/blog', '/blogs')):
            return False

        if re.search(r'/(news|press|article|a)/.*(20\d{2}|y20\d{2})', url_lower):
            return True
        if re.search(r'/20\d{2}/\d{1,2}/', url_lower):
            return True

        news_tokens = [
            'news', 'press', 'release', 'media', 'article', 'blog', 'insight',
            'story', 'event', 'announcement', '新闻', '资讯', '公告', '动态',
            '发布', '媒体'
        ]
        if any(token in url_lower or token in title_lower for token in news_tokens):
            return True

        return False

    def _extract_date_from_meta(self, text: str) -> Optional[datetime]:
        """从 Markdown 元数据区域提取日期"""
        # 提取 Title: 之前的部分（通常包含元数据）
        if "Markdown Content:" in text:
            meta_section = text.split("Markdown Content:")[0]
        elif "Title:" in text:
            meta_section = text.split("Title:")[0]
        else:
            meta_section = text[:500]

        # 常见的日期模式
        date_patterns = [
            (r'Date:\s*(\d{4}[-/]\d{2}[-/]\d{2})', None),
            (r'Published:\s*(\d{4}[-/]\d{2}[-/]\d{2})', None),
            (r'published:\s*(\d{4}[-/]\d{2}[-/]\d{2})', None),
            (r'(\d{4}年\d{1,2}月\d{1,2}日)', None),
            (r'(\d{4}-\d{2}-\d{2})', None),
            (r'(\d{4}/\d{2}/\d{2})', None),
            # Jina Reader 返回的 RFC 1123 格式: Published Time: Thu, 23 Apr 2026 06:55:26 GMT
            (r'Published\s+Time:\s*(\w+),\s*(\d{1,2})\s*(\w+)\s*(\d{4})\s*(\d{2}:\d{2}:\d{2})', 'rfc1123'),
        ]

        for pattern, fmt in date_patterns:
            match = re.search(pattern, meta_section)
            if match:
                if fmt == 'rfc1123':
                    # RFC 1123 格式: Thu, 23 Apr 2026 06:55:26 GMT
                    try:
                        from email.utils import parsedate_to_datetime
                        date_str = f"{match.group(1)}, {match.group(2)} {match.group(3)} {match.group(4)} {match.group(5)}"
                        return parsedate_to_datetime(date_str)
                    except Exception:
                        continue
                else:
                    date_str = match.group(1)
                    parsed = self._parse_date(date_str)
                    if parsed:
                        return parsed

        return None

    def _extract_date_from_context(self, context: str) -> Optional[datetime]:
        """从链接上下文提取日期"""
        # 在链接前后查找日期模式
        date_patterns = [
            r'(\d{4}[-/]\d{2}[-/]\d{2})',
            r'(\d{4}年\d{1,2}月\d{1,2}日)',
            r'(\d{4}-\d{2}-\d{2})',
        ]

        for pattern in date_patterns:
            match = re.search(pattern, context)
            if match:
                date_str = match.group(1)
                parsed = self._parse_date(date_str)
                if parsed:
                    return parsed

        return None

    def _parse_news_element(self, elem, site_config: Dict) -> Optional[RawIntelData]:
        """解析单个新闻元素"""
        # 提取标题
        title_elem = elem.select_one(site_config['title_selector'])
        if not title_elem:
            return None

        title = title_elem.get_text(strip=True)

        # 提取链接
        link_elem = elem.select_one(site_config['link_selector'])
        if not link_elem or not link_elem.get('href'):
            return None

        href = link_elem['href']
        url = urljoin(site_config['base_url'], href)

        # 提取日期
        date_elem = elem.select_one(site_config.get('date_selector', ''))
        pub_date = None
        if date_elem:
            pub_date = self._parse_date(date_elem.get_text(strip=True))

        # 提取摘要
        summary = ""
        content_elem = elem.select_one('.summary, .desc, p')
        if content_elem:
            summary = content_elem.get_text(strip=True)

        return RawIntelData(
            title=title,
            url=url,
            source=site_config['name'],
            source_type="web",
            pub_date=pub_date,
            content=summary,
            summary=summary[:500]
        )

    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """解析日期字符串"""
        if not date_str:
            return None

        date_formats = [
            "%Y-%m-%d",
            "%Y/%m/%d",
            "%Y年%m月%d日",
            "%m-%d",
            "%m/%d",
        ]

        # 清理日期字符串
        date_str = date_str.strip()

        for fmt in date_formats:
            try:
                date = datetime.strptime(date_str, fmt)
                # 如果只有月日，补充当前年份
                if date.year == 1900:
                    date = date.replace(year=datetime.now().year)
                return date
            except ValueError:
                continue

        return None

    async def fetch_article_content(self, url: str) -> str:
        """获取文章完整内容，使用Jina Reader作为fallback"""
        html = await self.fetch_html(url)
        if not html:
            # 尝试使用Jina Reader API
            return await self._fetch_via_jina(url)

        soup = self.parse_html(html)

        # 尝试多种正文选择器
        content_selectors = [
            'article',
            '.content',
            '.main-content',
            '.news-content',
            '.article-content',
            '#content',
            '.detail',
            '.post-content',
            '.entry-content',
            '.article-body'
        ]

        for selector in content_selectors:
            content_elem = soup.select_one(selector)
            if content_elem:
                return self.extract_full_text(content_elem)

        # 如果都没找到，返回整个body的文本
        body = soup.find('body')
        if body:
            return self.extract_full_text(body)

        # 最后尝试Jina Reader
        return await self._fetch_via_jina(url)

    async def _fetch_via_jina(self, url: str) -> str:
        """通过Jina Reader API获取文章内容"""
        jina_api_key = settings.collector.jina_api_key
        if not jina_api_key:
            logger.debug(f"未配置Jina API密钥，无法获取 {url} 的完整内容")
            return ""

        try:
            jina_url = f"https://r.jina.ai/{url}"
            headers = {
                "Authorization": f"Bearer {jina_api_key}",
                "Accept": "text/plain; charset=utf-8",
                "Accept-Encoding": "identity"
            }
            response = await self.client.get(jina_url, headers=headers, timeout=max(10, settings.collector.web_per_site_timeout))
            if response.status_code == 200:
                logger.debug(f"Jina Reader获取成功: {url}")
                text = response.text
                if "Warning: Target URL returned error 404" in text:
                    logger.debug(f"Jina Reader目标页面404: {url}")
                    return ""
                return text
        except ConnectTimeout:
            logger.warning(f"Jina Reader连接超时 {url}，尝试直接访问...")
            return await self._fetch_via_jina_direct(url)
        except Exception as e:
            logger.debug(f"Jina Reader获取失败 {url}: {e}")

        return ""

    async def _fetch_via_jina_direct(self, url: str) -> str:
        """直接通过 Jina AI API 获取（不带代理）"""
        jina_api_key = settings.collector.jina_api_key
        if not jina_api_key:
            return ""

        # 尝试多个 Jina API 端点
        jina_urls = [
            f"https://r.jina.ai/{url}",
            f"https://jina.ai/reader/{url}/",
        ]

        for jina_url in jina_urls:
            try:
                # 不使用代理直接请求
                async with httpx.AsyncClient(timeout=httpx.Timeout(15.0, read=30.0), proxy=None) as client:
                    headers = {
                        "Authorization": f"Bearer {jina_api_key}",
                        "Accept": "text/plain; charset=utf-8",
                        "Accept-Encoding": "identity"
                    }
                    response = await client.get(jina_url, headers=headers)
                    if response.status_code == 200:
                        logger.debug(f"Jina直接获取成功: {url}")
                        text = response.text
                        if "Warning: Target URL returned error 404" in text:
                            return ""
                        return text
            except Exception as e:
                logger.debug(f"Jina直接获取失败 {jina_url}: {e}")
                continue

        return ""

    async def _fetch_via_playwright(self, url: str) -> str:
        """通过 Playwright 无头浏览器获取动态渲染后的页面内容"""
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()

                # 设置视口
                await page.set_viewport_size({"width": 1920, "height": 1080})

                # 导航到页面并等待 DOM 加载完成
                await page.goto(url, wait_until="domcontentloaded", timeout=max(5000, settings.collector.web_per_site_timeout * 1000))

                # 等待新闻列表容器加载（通用选择器）
                try:
                    await page.wait_for_selector(
                        "article, .news-item, .news-list, .article-list, .press-release, [class*='news'], [role='article']",
                        timeout=3000
                    )
                except Exception:
                    pass  # 没找到特定容器也继续

                # 滚动页面以触发懒加载
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await page.wait_for_timeout(800)

                # 获取渲染后的 HTML
                html = await page.content()

                await browser.close()

                logger.debug(f"Playwright 渲染成功: {url}")
                return html

        except Exception as e:
            logger.debug(f"Playwright 获取失败 {url}: {e}")

        return ""

