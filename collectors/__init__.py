"""
采集器模块 - 多源数据采集
"""
from .base import BaseCollector, RawIntelData
from .rss_collector import RSSCollector
from .web_collector import WebCollector
from .search_collector import SearchCollector
from .patent_collector import PatentCollector

__all__ = [
    'BaseCollector',
    'RawIntelData',
    'RSSCollector',
    'WebCollector',
    'SearchCollector',
    'PatentCollector',
]
