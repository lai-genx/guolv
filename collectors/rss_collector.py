"""
RSS采集器 - 从RSS源采集情报
"""
from datetime import datetime
from typing import List, Optional, Dict
import xml.etree.ElementTree as ET

from loguru import logger

from .base import BaseCollector, CollectorResult, RawIntelData, contains_keywords
from config import settings


class RSSCollector(BaseCollector):
    """RSS采集器"""
    
    # 默认RSS源列表
    DEFAULT_FEEDS = [
        # 国内媒体（优先，无需代理）
        "https://www.c114.com.cn/rss/",                              # C114通信网
        "https://www.cww.net.cn/rss.xml",                            # 通信世界
        "https://www.51cto.com/rss/index.html",                      # 51CTO
        "https://www.texiao.com/rss/",                               # 通信产业报
        "https://www.cnii.com.cn/rss",                               # 中国信息产业网

        # 国际媒体（可访问）
        "https://spectrum.ieee.org/rss/",                            # IEEE Spectrum
        "https://www.rcrwireless.com/feed",                          # RCR Wireless
        "https://www.sdxcentral.com/feed/",                          # SDxCentral（SDN/NFV）
        "https://www.lightreading.com/rss.xml",                      # Light Reading
        "https://www.telecomtv.com/rss",                             # TelecomTV
        "https://www.fierce-network.com/rss.xml",                    # Fierce Network

        # 国际企业官方RSS
        "https://www.ericsson.com/en/newsroom/news/rss",            # Ericsson
        "https://www.nokia.com/about-us/newsroom/press-releases/press-releases-rss/",  # Nokia
        "https://newsroom.cisco.com/c/channels/rss.spa",            # Cisco
    ]
    
    def __init__(self):
        super().__init__("rss")
        # 优先使用config中的设置，如果为空则使用默认列表
        config_feeds = settings.collector.rss_feeds if hasattr(settings.collector, 'rss_feeds') and settings.collector.rss_feeds else []
        self.feeds = config_feeds if config_feeds else self.DEFAULT_FEEDS
        self.feed_failures = {}  # 记录每个RSS源的失败次数
    
    async def collect(self, **kwargs) -> CollectorResult:
        """从RSS源采集情报"""
        all_items = []
        success_count = 0
        skipped_count = 0

        max_items_per_feed = kwargs.get('max_items_per_feed', 20)
        max_failures = 3  # 失败超过3次则跳过

        for feed_url in self.feeds:
            # 跳过失败次数过多的源
            if self.feed_failures.get(feed_url, 0) >= max_failures:
                logger.warning(f"跳过频繁失败的RSS源: {feed_url} (失败{self.feed_failures[feed_url]}次)")
                skipped_count += 1
                continue

            try:
                logger.info(f"采集RSS源: {feed_url}")
                items = await self._parse_feed(feed_url, max_items_per_feed)
                all_items.extend(items)
                success_count += 1
                # 成功则重置失败计数
                self.feed_failures[feed_url] = 0
                logger.info(f"从 {feed_url} 获取 {len(items)} 条数据")
            except Exception as e:
                # 记录失败次数
                self.feed_failures[feed_url] = self.feed_failures.get(feed_url, 0) + 1
                logger.error(f"采集RSS源失败 {feed_url}: {e} (失败{self.feed_failures[feed_url]}次)")

        # 关键词过滤
        filtered_items = [item for item in all_items if contains_keywords(item.title + item.summary)]

        return CollectorResult(
            items=filtered_items,
            success=success_count > 0,
            message=f"成功采集 {success_count}/{len(self.feeds)-skipped_count} 个RSS源，跳过 {skipped_count} 个失败源，过滤后 {len(filtered_items)}/{len(all_items)} 条",
            total_found=len(all_items)
        )
    
    async def _parse_feed(self, feed_url: str, max_items: int = 20) -> List[RawIntelData]:
        """解析单个RSS源"""
        items = []
        
        html = await self.fetch_html(feed_url)
        if not html:
            return items
        
        try:
            root = ET.fromstring(html)
            
            # 处理RSS 2.0格式
            if root.tag == 'rss' or root.tag.endswith('rss'):
                channel = root.find('.//channel')
                if channel is not None:
                    source_name = self._get_text(channel, 'title', 'Unknown')
                    for item_elem in channel.findall('item')[:max_items]:
                        item = self._parse_rss_item(item_elem, source_name, feed_url)
                        if item:
                            items.append(item)
            
            # 处理Atom格式
            elif root.tag.endswith('feed'):
                source_name = self._get_text(root, 'title', 'Unknown')
                for entry in root.findall('.//entry')[:max_items]:
                    item = self._parse_atom_entry(entry, source_name, feed_url)
                    if item:
                        items.append(item)
        
        except ET.ParseError as e:
            logger.error(f"解析RSS失败 {feed_url}: {e}")
            # 尝试用正则表达式提取
            items = self._fallback_parse(html, feed_url)
        
        return items
    
    def _parse_rss_item(self, item_elem: ET.Element, source_name: str, feed_url: str) -> Optional[RawIntelData]:
        """解析RSS条目"""
        title = self._get_text(item_elem, 'title')
        link = self._get_text(item_elem, 'link')
        
        if not title or not link:
            return None
        
        description = self._get_text(item_elem, 'description')
        pub_date = self._parse_date(self._get_text(item_elem, 'pubDate'))
        
        # 清理HTML标签
        summary = self._strip_html(description)
        
        return RawIntelData(
            title=title.strip(),
            url=link.strip(),
            source=source_name,
            source_type="rss",
            pub_date=pub_date,
            content=summary,
            summary=summary[:500]
        )
    
    def _parse_atom_entry(self, entry_elem: ET.Element, source_name: str, feed_url: str) -> Optional[RawIntelData]:
        """解析Atom条目"""
        title = self._get_text(entry_elem, 'title')
        
        # 获取链接
        link_elem = entry_elem.find('link')
        link = link_elem.get('href', '') if link_elem is not None else ''
        
        if not title or not link:
            return None
        
        content = self._get_text(entry_elem, 'content')
        if not content:
            content = self._get_text(entry_elem, 'summary')
        
        pub_date = self._parse_date(self._get_text(entry_elem, 'published'))
        
        summary = self._strip_html(content)
        
        return RawIntelData(
            title=title.strip(),
            url=link.strip(),
            source=source_name,
            source_type="rss",
            pub_date=pub_date,
            content=summary,
            summary=summary[:500]
        )
    
    def _fallback_parse(self, html: str, feed_url: str) -> List[RawIntelData]:
        """备用解析方法 - 使用正则"""
        import re
        items = []
        
        # 尝试匹配简单的item/link模式
        title_pattern = re.compile(r'<title>([^<]+)</title>', re.I)
        link_pattern = re.compile(r'<link>([^<]+)</link>', re.I)
        
        titles = title_pattern.findall(html)
        links = link_pattern.findall(html)
        
        for i, (title, link) in enumerate(zip(titles[1:], links)):  # 跳过channel title
            if title and link:
                items.append(RawIntelData(
                    title=title.strip(),
                    url=link.strip(),
                    source=feed_url,
                    source_type="rss",
                    pub_date=None,
                    content="",
                    summary=""
                ))
        
        return items[:20]
    
    def _get_text(self, element: ET.Element, tag: str, default: str = '') -> str:
        """获取XML元素文本"""
        # 处理命名空间
        if element is None:
            return default
        
        child = element.find(tag)
        if child is not None and child.text:
            return child.text
        
        # 尝试带命名空间的查找
        for child in element:
            if child.tag.endswith(tag):
                return child.text or default
        
        return default
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """解析RSS日期格式"""
        if not date_str:
            return None
        
        date_formats = [
            "%a, %d %b %Y %H:%M:%S %z",
            "%a, %d %b %Y %H:%M:%S %Z",
            "%Y-%m-%dT%H:%M:%SZ",
            "%Y-%m-%dT%H:%M:%S%z",
            "%Y-%m-%d %H:%M:%S",
        ]
        
        for fmt in date_formats:
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except ValueError:
                continue
        
        return None
    
    def _strip_html(self, html: str) -> str:
        """移除HTML标签"""
        import re
        if not html:
            return ""
        
        # 移除HTML标签
        text = re.sub(r'<[^>]+>', '', html)
        # 解码HTML实体
        text = text.replace('&lt;', '<').replace('&gt;', '>')
        text = text.replace('&amp;', '&').replace('&quot;', '"')
        text = text.replace('&#39;', "'").replace('&nbsp;', ' ')
        
        return text.strip()
