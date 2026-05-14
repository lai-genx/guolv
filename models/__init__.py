"""
数据模型模块
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class Category(str, Enum):
    """情报分类"""
    COMPANY_NEWS = "关键公司动态"
    PATENT = "专利情况"
    TECHNOLOGY = "新技术"
    INVESTMENT = "投资收购"
    DOWNSTREAM = "下游产业应用"
    OTHER = "其他"


class Industry(str, Enum):
    """下游行业"""
    TELECOM_OPERATOR = "电信运营商"
    GOVERNMENT_ENTERPRISE = "政企专网"
    DATA_CENTER = "数据中心"
    INDUSTRIAL_INTERNET = "工业互联网"
    VEHICLE_NETWORK = "车联网"
    CONSUMER_ELECTRONICS = "消费电子"
    OTHER = "其他"


class TechDomain(str, Enum):
    """技术领域"""
    WIRELESS = "无线通信"
    OPTICAL = "光通信"
    CORE_NETWORK = "核心网"
    TRANSMISSION = "传输承载"
    ACCESS_NETWORK = "接入网"
    TERMINAL = "终端设备"
    OTHER = "其他"


class ActionType(str, Enum):
    """动作类型"""
    RND = "研发动作"
    MARKET = "市场动作"
    OTHER = "其他"


class NewsFreshness(str, Enum):
    """新闻新鲜度"""
    CURRENT = "current"  # 近期新闻
    HISTORICAL = "historical"  # 历史新闻
    BACKGROUND = "background"  # 背景介绍


class IntelItem(BaseModel):
    """情报条目数据模型"""
    id: Optional[int] = None
    
    # 基本信息
    title: str = Field(..., description="标题")
    source_url: str = Field(..., description="来源URL")
    source_name: str = Field(default="", description="来源名称")
    source_type: str = Field(default="", description="来源类型 (rss/web/search/wechat/patent/academic)")
    pub_date: Optional[datetime] = Field(default=None, description="发布日期")
    content: str = Field(default="", description="正文内容")
    
    # AI分析结果
    category: Optional[Category] = Field(default=None, description="情报分类")
    industry: Optional[Industry] = Field(default=None, description="下游行业")
    tech_domain: Optional[TechDomain] = Field(default=None, description="技术领域")
    action_type: Optional[ActionType] = Field(default=None, description="动作类型")
    
    # 评分
    importance: int = Field(default=3, ge=1, le=5, description="重要性1-5")
    decision_value: bool = Field(default=False, description="是否有决策价值")
    
    # 新闻属性
    is_news: bool = Field(default=True, description="是否为新闻")
    news_freshness: NewsFreshness = Field(default=NewsFreshness.CURRENT, description="新闻新鲜度")
    
    # 摘要和洞察
    summary_zh: str = Field(default="", description="中文摘要")
    one_line_insight: str = Field(default="", description="一句话点评")
    
    # 标签和公司
    tags: List[str] = Field(default_factory=list, description="标签列表")
    companies_mentioned: List[str] = Field(default_factory=list, description="涉及的公司")
    
    # 元数据
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: Optional[datetime] = Field(default=None, description="更新时间")
    
    # RAG相关
    rag_triggered: bool = Field(default=False, description="是否触发了RAG检索")
    rag_context: str = Field(default="", description="RAG检索到的上下文")

    # ===== 产业链维度 =====
    supply_chain: Optional[str] = Field(
        None,
        description="产业链名称，如'芯片与半导体'、'光通信器件与模块'等"
    )
    supply_chain_segment: Optional[str] = Field(
        None,
        description="产业链环节，如'基带芯片'、'光模块'等"
    )
    subsector_type: Optional[str] = Field(
        None,
        description="二级分类，如'政策变化'、'关键企业动态'、'研发动态'、'市场动态'、'投融资'"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "title": "华为发布新一代5G小基站产品",
                "source_url": "https://example.com/news/123",
                "source_name": "通信世界",
                "source_type": "rss",
                "category": "关键公司动态",
                "tech_domain": "无线通信",
                "importance": 4,
                "decision_value": True,
                "one_line_insight": "小基站产品线扩充，强化室内覆盖和企业专网竞争力"
            }
        }


class WeeklyReport(BaseModel):
    """周报表数据模型"""
    id: Optional[int] = None
    issue_no: int = Field(..., description="期号")
    date_start: datetime = Field(..., description="开始日期")
    date_end: datetime = Field(..., description="结束日期")
    
    # 报告内容
    report_md: str = Field(default="", description="Markdown格式报告")
    report_html: str = Field(default="", description="HTML格式报告")
    
    # 发送状态
    sent_email: bool = Field(default=False, description="是否邮件发送")
    sent_wechat: bool = Field(default=False, description="是否微信发送")
    sent_at: Optional[datetime] = Field(default=None, description="发送时间")
    
    # 元数据
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    
    # 统计信息
    total_items: int = Field(default=0, description="情报条目总数")
    importance_distribution: Dict[str, int] = Field(default_factory=dict, description="重要性分布")
    category_distribution: Dict[str, int] = Field(default_factory=dict, description="分类分布")


class AnalysisResult(BaseModel):
    """AI分析结果数据模型"""
    category: str = Field(..., description="分类")
    industry: str = Field(..., description="下游行业")
    tech_domain: str = Field(..., description="技术领域")
    action_type: str = Field(..., description="动作类型")
    companies_mentioned: List[str] = Field(default_factory=list, description="涉及公司")
    importance: int = Field(..., ge=1, le=5, description="重要性")
    decision_value: bool = Field(..., description="决策价值")
    is_news: bool = Field(..., description="是否为新闻")
    news_freshness: str = Field(..., description="新闻新鲜度")
    summary_zh: str = Field(..., description="中文摘要")
    one_line_insight: str = Field(..., description="一句话点评")
    tags: List[str] = Field(default_factory=list, description="标签")


class RawIntelData(BaseModel):
    """原始采集数据模型"""
    title: str = Field(..., description="标题")
    url: str = Field(..., description="URL")
    source: str = Field(..., description="来源")
    source_type: str = Field(..., description="来源类型")
    pub_date: Optional[datetime] = Field(default=None, description="发布日期")
    content: str = Field(default="", description="内容")
    summary: str = Field(default="", description="摘要")


__all__ = [
    'Category',
    'Industry', 
    'TechDomain',
    'ActionType',
    'NewsFreshness',
    'IntelItem',
    'WeeklyReport',
    'AnalysisResult',
    'RawIntelData',
]
