"""
采集器基类模块
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Dict, Any
from urllib.parse import urlparse

import httpx
from httpx import ConnectTimeout, ReadTimeout, PoolTimeout, ProxyError
from bs4 import BeautifulSoup
from loguru import logger

from config import settings
from models import RawIntelData


@dataclass
class CollectorResult:
    """采集结果"""
    items: List[RawIntelData]
    success: bool
    message: str
    total_found: int


class BaseCollector(ABC):
    """采集器基类"""
    
    def __init__(self, source_type: str):
        self.source_type = source_type
        self.timeout = settings.collector.request_timeout
        self.max_retries = settings.collector.max_retries
        self.proxy = settings.collector.http_proxy
        
        # 创建HTTP客户端
        self.client = self._create_client()
    
    def _create_client(self) -> httpx.AsyncClient:
        """创建HTTP客户端"""
        proxy = self.proxy if self.proxy else None

        # 更真实的浏览器标识和请求头，防止反爬虫
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Cache-Control": "max-age=0",
            "Referer": "https://www.google.com/",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Upgrade-Insecure-Requests": "1",
            "Connection": "keep-alive",
        }

        # 配置超时和重试
        timeout_config = httpx.Timeout(
            connect=10.0,    # 连接超时 10秒
            read=30.0,       # 读取超时 30秒
            write=10.0,      # 写入超时 10秒
            pool=10.0        # 连接池超时 10秒
        )

        return httpx.AsyncClient(
            timeout=timeout_config,
            proxy=proxy,
            follow_redirects=True,
            headers=headers,
            limits=httpx.Limits(max_connections=10, max_keepalive_connections=5)
        )
    
    @abstractmethod
    async def collect(self, **kwargs) -> CollectorResult:
        """执行采集，子类必须实现"""
        pass
    
    async def fetch_html(self, url: str) -> Optional[str]:
        """获取网页HTML内容"""
        try:
            response = await self.client.get(url)
            response.raise_for_status()
            return response.text
        except ConnectTimeout:
            logger.warning(f"连接超时 {url}，尝试使用代理...")
            # 尝试通过代理获取
            return await self._fetch_with_proxy_fallback(url)
        except ReadTimeout:
            logger.warning(f"读取超时 {url}")
            return None
        except PoolTimeout:
            logger.warning(f"连接池超时 {url}")
            return None
        except ProxyError as e:
            logger.warning(f"代理错误 {url}: {e}")
            return None
        except httpx.HTTPStatusError as e:
            logger.warning(f"HTTP状态错误 {url}: {e.response.status_code}")
            return None
        except Exception as e:
            logger.error(f"获取页面失败 {url}: {e}")
            return None

    async def _fetch_with_proxy_fallback(self, url: str) -> Optional[str]:
        """通过代理 fallback 获取页面"""
        proxies = [
            self.proxy,
            "http://127.0.0.1:7890",      # Clash 默认
            "http://127.0.0.1:1080",      # V2Ray 默认
            "http://127.0.0.1:8080",      # 通用代理
        ]

        for proxy in set(proxies):  # 去重
            if not proxy:
                continue
            try:
                logger.debug(f"尝试代理 {proxy} 获取 {url}")
                async with httpx.AsyncClient(timeout=httpx.Timeout(10.0, read=30.0)) as client:
                    response = await client.get(url, proxy=proxy)
                    response.raise_for_status()
                    logger.info(f"通过代理 {proxy} 成功获取 {url}")
                    return response.text
            except Exception as e:
                logger.debug(f"代理 {proxy} 失败: {e}")
                continue

        logger.warning(f"所有代理尝试失败，无法获取 {url}")
        return None
    
    async def fetch_json(self, url: str, params: Optional[Dict] = None) -> Optional[Dict]:
        """获取JSON数据"""
        try:
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"获取JSON失败 {url}: {e}")
            return None
    
    def parse_html(self, html: str) -> BeautifulSoup:
        """解析HTML"""
        return BeautifulSoup(html, 'lxml')
    
    def extract_text(self, soup: BeautifulSoup, selector: str) -> str:
        """从HTML中提取文本"""
        try:
            element = soup.select_one(selector)
            return element.get_text(strip=True) if element else ""
        except Exception:
            return ""
    
    def extract_full_text(self, soup: BeautifulSoup) -> str:
        """提取文章正文内容"""
        # 移除脚本和样式
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
        
        # 获取文本
        text = soup.get_text(separator='\n', strip=True)
        
        # 清理空行
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        return '\n'.join(lines)
    
    def extract_links(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, str]]:
        """提取页面中的所有链接"""
        links = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            text = a.get_text(strip=True)
            
            # 处理相对URL
            if href.startswith('/'):
                parsed = urlparse(base_url)
                href = f"{parsed.scheme}://{parsed.netloc}{href}"
            elif not href.startswith('http'):
                continue
            
            if text and href:
                links.append({'text': text, 'url': href})
        
        return links
    
    def clean_text(self, text: str) -> str:
        """清理文本内容"""
        if not text:
            return ""
        
        # 移除多余空白
        lines = [line.strip() for line in text.split('\n')]
        lines = [line for line in lines if line]
        
        return '\n'.join(lines)
    
    def is_valid_url(self, url: str) -> bool:
        """验证URL是否有效"""
        try:
            parsed = urlparse(url)
            return parsed.scheme in ('http', 'https') and parsed.netloc
        except Exception:
            return False
    
    async def close(self):
        """关闭HTTP客户端"""
        await self.client.aclose()
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()


# 关键词过滤配置
MONITORED_KEYWORDS = {
    "en": [
        # 技术词 - 核心技术方向
        "5G", "6G", "wireless communication", "cellular network",
        "optical communication", "fiber optic", "DWDM", "OTN",
        "core network", "SDN", "NFV", "cloud-native",
        "Massive MIMO", "beamforming", "mmWave",
        "network slicing", "edge computing", "Open RAN",
        "routing", "switching", "data center interconnect",
        # 新增技术词 - 新兴方向
        "vRAN", "RIC", "O-RAN Alliance", "Network Disaggregation",
        "Intent-based networking", "AI network", "Quantum communication",
        "satellite communication", "Non-Terrestrial Network", "NTN",
        "private 5G", "industrial IoT", "vehicle-to-everything", "V2X",
        "network computing", "algorithm-aware networking", "programmable network",
        # 公司名称 - 主要企业
        "Huawei", "ZTE", "Ericsson", "Nokia", "Cisco", "FiberHome",
        "Hengtong", "Yofc", "Fujitsu", "NEC", "Corning", "Prysmian",
        # 新增企业名称 - 上游供应商和新兴企业
        "Qualcomm", "Broadcom", "MediaTek", "Samsung", "Intel",
        "Lumentum", "Coherent", "Innolight", "Infinera", "Ciena",
        "Mavenir", "UXE", "Casa Systems", "Altiostar",
        "Radcom", "Amdocs", "Netcracker", "Red Hat",
        # 企业产品线词汇
        "Harmonyos", "Cloud RAN", "Service Mesh", "NFVI",
        "DU", "CU", "MEC", "RAN", "nanoRAN", "Spectrum Sharing",
        # 行业宽泛词
        "telecom", "communications equipment", "base station",
        "optical module", "transmission", "network infrastructure",
        "telecommunications", "carrier network", "operator",
        "communications provider", "network operator", "service provider",
        "network equipment", "wireless operator", "broadband provider"
    ],
    "zh": [
        # 技术词 - 核心技术方向
        "5G", "6G", "无线通信", "移动通信", "蜂窝网络",
        "光通信", "光纤通信", "波分复用", "光传输网",
        "核心网", "软件定义网络", "网络功能虚拟化", "云原生",
        "大规模MIMO", "波束赋形", "毫米波通信",
        "网络切片", "边缘计算", "开放无线接入网", "Open RAN",
        "路由器", "交换机", "数据中心互联", "算力网络",
        # 新增技术词 - 新兴方向
        "vRAN", "RIC", "O-RAN", "网络解耦", "解耦架构",
        "意图驱动网络", "AI网络", "量子通信", "智能网络",
        "卫星通信", "非地面网络", "NTN", "私有5G",
        "工业互联网", "车联网", "V2X", "物联网", "边缘计算",
        "网络计算", "可编程网络", "智能化网络", "自智网络",
        "云原生网络", "微服务", "容器化", "云计算",
        # 公司名称 - 主要企业（已有）
        "华为", "中兴", "爱立信", "诺基亚", "思科",
        "烽火通信", "亨通光电", "中天科技", "长飞光纤", "富士通",
        # 新增企业名称 - 产业链完整覆盖
        "高通", "博通", "联发科", "三星", "英特尔",
        "光迅科技", "中际旭创", "新易盛", "华工正源", "海信宽带",
        "鹏鼎控股", "东山精密", "深南电路", "沪电股份", "景旺电子",
        "泰科电子", "安费诺", "莫仕", "申泰", "中航光电",
        "康普通讯", "凯士林", "通宇通讯", "京信通信", "摩比发展",
        "盛路通信", "武汉凡谷", "大富科技", "新华三", "锐捷网络",
        "移远通信", "广和通", "日海智能", "美格智能", "有方科技",
        # 华为产品线和部门
        "灵犀芯片", "昇腾", "鸿蒙", "云服务", "云计算",
        "云存储", "HiCloud", "华为云", "昆仑芯片", "麒麟芯片",
        "Mate系列", "P系列", "Foldable", "折叠屏", "5G芯片",
        # 中兴产品线
        "ZXEC8080", "ULTRACELL", "SkyLink", "ZXC系列", "通信芯片",
        # 爱立信产品线
        "Cloud RAN", "Service Mesh", "NFVI", "RAN Compute",
        "5G核心网", "6G", "无线云", "AI引擎",
        # 应用场景词
        "5G专网", "5G应用", "运营商", "国内运营商", "电信运营商",
        "移动运营商", "智慧城市", "智能交通", "工业4.0",
        "远程医疗", "远程教育", "直播", "超高清视频", "4K", "8K",
        "AR", "VR", "虚拟现实", "增强现实", "虚拟化",
        # 下游应用
        "数据中心", "政企网络", "企业网", "专网", "行业应用",
        "垂直行业", "实际应用", "场景应用", "基地建设",
        # 市场和财务词汇
        "融资", "融资轮", "投融资", "并购", "收购", "兼并",
        "IPO", "上市", "上市公司", "非上市", "初创企业",
        "创业公司", "独角兽", "估值", "融资金额", "投资方",
        "战略融资", "天使融资", "种子轮", "A轮", "B轮",
        # 行业宽泛词
        "通信设备", "基站", "光模块", "光纤", "电信",
        "运营商", "通信行业", "网络设备", "传输设备",
        "通信技术", "通信企业", "通信服务", "电信服务",
        "通信运营", "网络建设", "基础设施", "新基建"
    ]
}


def contains_keywords(text: str) -> bool:
    """检查文本是否包含监控关键词"""
    if not text:
        return False
    
    text_lower = text.lower()
    
    for keyword in MONITORED_KEYWORDS["en"]:
        if keyword.lower() in text_lower:
            return True
    
    for keyword in MONITORED_KEYWORDS["zh"]:
        if keyword in text:
            return True
    
    return False
