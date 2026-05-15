"""
配置管理模块 - 使用Pydantic Settings管理所有配置
"""
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional, List, Union
from pathlib import Path

ENV_FILE = Path(__file__).resolve().parent / ".env"


class LLMSettings(BaseSettings):
    """LLM配置"""
    model_config = SettingsConfigDict(
        env_prefix="LLM__",
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8-sig",
        extra="ignore"
    )
    
    deepseek_api_key: str = Field(default="", description="DeepSeek API密钥")
    deepseek_base_url: str = Field(default="https://api.deepseek.com/v1", description="DeepSeek API基础URL")
    
    qwen_api_key: str = Field(default="", description="通义千问API密钥")
    qwen_base_url: str = Field(default="https://dashscope.aliyuncs.com/compatible-mode/v1", description="通义千问API基础URL")
    
    kimi_api_key: str = Field(default="", description="Kimi API密钥")
    kimi_base_url: str = Field(default="https://api.moonshot.cn/v1", description="Kimi API基础URL")
    
    claude_api_key: str = Field(default="", description="Claude API密钥")
    claude_base_url: str = Field(default="https://api.anthropic.com/v1", description="Claude API基础URL")
    
    default_model: str = Field(default="deepseek-chat", description="默认使用的模型")
    fallback_models: List[str] = Field(default=["qwen-max", "kimi", "claude"], description="降级模型列表")


class CollectorSettings(BaseSettings):
    """采集器配置"""
    model_config = SettingsConfigDict(
        env_prefix="COLLECTOR__",
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8-sig",
        extra="ignore"
    )
    
    http_proxy: Optional[str] = Field(default=None, description="HTTP代理")
    https_proxy: Optional[str] = Field(default=None, description="HTTPS代理")
    
    jina_api_key: str = Field(default="", description="Jina Reader API密钥")
    
    epo_key: str = Field(default="", description="欧洲专利局API Key")
    epo_secret: str = Field(default="", description="欧洲专利局API Secret")

    enable_search: bool = Field(default=True, description="是否启用搜索引擎采集")
    enable_patent: bool = Field(default=True, description="是否启用专利线索采集")
    enable_vvihot: bool = Field(default=False, description="是否启用识微商情/VviHot平台采集")
    enable_web: bool = Field(default=True, description="是否启用企业官网网页采集")
    web_max_sites: int = Field(default=0, description="网页采集单轮最多扫描网站数，0表示全部")
    web_per_site_timeout: int = Field(default=30, description="网页采集单个网站最大等待秒数")
    patent_max_queries: int = Field(default=0, description="专利采集单轮最多查询数，0表示全部")
    patent_max_results_per_query: int = Field(default=5, description="专利采集每个查询最多结果数")
    patent_per_query_timeout: int = Field(default=30, description="专利采集单个查询最大等待秒数")
    vvihot_url: str = Field(default="https://zreywc.vvihot.com/swsq/", description="识微商情平台地址")
    vvihot_username: str = Field(default="", description="识微商情账号")
    vvihot_password: str = Field(default="", description="识微商情密码")
    vvihot_headless: bool = Field(default=True, description="是否以无头浏览器运行识微商情采集")
    vvihot_wait_seconds: int = Field(default=12, description="登录后等待平台主题数据加载秒数")
    vvihot_max_items: int = Field(default=80, description="识微商情单轮最多采集条数")
    vvihot_topic_names: str = Field(default="", description="识微商情主题名白名单，逗号分隔，留空表示全部")
    vvihot_manage_topics: bool = Field(default=False, description="是否自动创建/维护识微商情通信主题")
    vvihot_delete_unmanaged_topics: bool = Field(default=False, description="主题额度不足时是否删除非托管主题")
    vvihot_managed_topic_prefix: str = Field(default="CT-", description="托管主题名前缀")
    
    request_timeout: int = Field(default=60, description="请求超时时间(秒)")
    max_retries: int = Field(default=5, description="最大重试次数")
    
    # RSS源配置 - 已验证可用的专业技术源
    rss_feeds: List[str] = Field(default=[
        # === 国际技术媒体（已验证✅）===
        "https://feeds.arstechnica.com/arstechnica/index",                # Ars Technica（深度技术分析）
        "https://venturebeat.com/feed/",                                  # VentureBeat（融资+企业动态）
        "https://www.techradar.com/rss.xml",                              # TechRadar（综合科技）
        "https://techcrunch.com/feed/",                                   # TechCrunch (科技创新)
        "https://www.theverge.com/rss/index.xml",                         # The Verge (硬件+科技)
        "https://www.technologyreview.com/feed/",                         # MIT Technology Review (深度分析)

        # === 电信/网络专业媒体（已验证✅）===
        "https://www.rcrwireless.com/feed",                              # RCR Wireless（无线通信专业）
        "https://feeds.feedburner.com/5g",                                # 5G World Pro（5G专业）
        "https://www.telecomdrive.com/feed/",                             # TelecomDrive（电信驱动）

        # === 5G/芯片专业（已验证✅）===
        "https://www.semiconductordigest.com/feed",                       # Semiconductor Digest（芯片行业）
        "https://www.eenewsanalog.com/rss.xml",                           # EE News Analog（模拟芯片）

        # === Google News（已验证✅）===
        "https://news.google.com/rss",                                     # Google News (综合)
        "https://news.google.com/rss?hl=en&gl=US&ceid=US:en",             # Google News - US Edition

        # === 技术社区 & 热点新闻（已验证✅）===
        "https://news.ycombinator.com/rss",                               # Hacker News (科技热点)
        "https://www.reddit.com/r/technology/.rss",                       # Reddit r/technology

        # === 中国通信行业（已验证✅）===
        "https://www.c114.com.cn/rss/",                                   # C114通信网（国内通信专业）
    ], description="RSS订阅源列表（已验证✅：16个源）")
    
    # 监控公司列表
    target_companies: List[str] = Field(default=[
        "ADTRAN",
        "AT&T",
        "Apple",
        "Arista Networks",
        "Broadcom",
        "Calix",
        "Ciena",
        "Coherent",
        "DZS",
        "Infinera",
        "Juniper",
        "Lumentum",
        "Mavenir",
        "NEC",
        "NTT DoCoMo",
        "Orange",
        "RFS",
        "SK电讯",
        "Sierra Wireless",
        "T-Mobile",
        "Verizon",
        "u-blox",
        "三星LSI",
        "三星电子",
        "三环集团",
        "上海艾为",
        "东山精密",
        "中兴通讯",
        "中国广电",
        "中国电信",
        "中国移动",
        "中国联通",
        "中国通信服务",
        "中国铁塔",
        "中天科技",
        "中星微",
        "中电科55所",
        "中科汉天下",
        "中航光电",
        "中际旭创",
        "亨通光电",
        "京信通信",
        "仕佳光子",
        "信维通信",
        "光库科技",
        "光迅科技",
        "全信股份",
        "全志科技",
        "共进股份",
        "凯士林",
        "北斗星通",
        "华为",
        "华为海思",
        "华勤技术",
        "华工正源",
        "华工科技",
        "卓胜微",
        "博创科技",
        "博通集成",
        "合众思壮",
        "吴通控股",
        "唯捷创芯",
        "圣邦微",
        "大富科技",
        "天孚通信",
        "天邑股份",
        "太辰光",
        "富士康",
        "富士通",
        "展讯",
        "广和通",
        "康普通讯",
        "德国电信",
        "德州仪器",
        "思比科",
        "思科",
        "思立微",
        "慧智微",
        "振芯科技",
        "摩比发展",
        "新华三",
        "新易盛",
        "日海智能",
        "昂纳",
        "星网锐捷",
        "春兴精工",
        "有方科技",
        "格科微电子",
        "欣天科技",
        "武汉凡谷",
        "汇源通信",
        "汇顶科技",
        "沃达丰",
        "泰利特",
        "海信宽带",
        "润建通信",
        "源杰科技",
        "烽火通信",
        "爱立信",
        "特发信息",
        "珠海炬力",
        "理工光科",
        "瑞芯微电子",
        "盛路通信",
        "矽睿半导体",
        "硕贝德",
        "移芯通信",
        "移远通信",
        "索尔思光电",
        "紫光展锐",
        "美新半导体",
        "美格智能",
        "翱捷科技",
        "联发科",
        "联芯科技",
        "芯讯通",
        "苏州敏芯",
        "英特尔",
        "西安华达",
        "诺基亚",
        "软银",
        "通宇通讯",
        "通鼎互联",
        "金信诺",
        "锐捷网络",
        "锐科激光",
        "长飞光纤",
        "闻泰科技",
        "集创北方",
        "风华高科",
        "高新兴",
        "高通",
        "鸿博股份",
        "鸿辉光通",
        "麦捷科技",
        "龙旗科技",
        # === 从企业清单导入的新公司 (2026-04-17) ===
        "芯翼信息",  # Xinyi Info
        "思佳讯",  # Skyworks
        "科沃",  # Qorvo
        "村田",  # Murata
        "太阳诱电",  # Taiyo Yuden
        "TDK",
        "飞骧科技",  # FX Semiconductor
        "长光华芯",  # Everbright Photonics
        "鹏鼎控股",  # Avary Holding
        "深南电路",  # SCC
        "沪电股份",  # WUS Printed Circuit
        "景旺电子",  # Kinwong
        "胜宏科技",  # Shengyi Tech
        "崇达技术",  # Chongda Tech
        "兴森科技",  # Fastprint
        "欣兴电子",  # Unimicron
        "华通电脑",  # Compeq
        "健鼎科技",  # Tripod
        "TTM Technologies",
        "奥特斯",  # AT&S
        "建滔集团",  # Kingboard
        "生益科技",  # Shengyi Tech
        "南亚塑胶",  # Nanya Plastic
        "联茂集团",  # ITEQ
        "台光电子",  # EMC
        "金安国纪",  # GDM
        "华正新材",  # Huazheng New Materials
        "松下",  # Panasonic
        "三菱化学",  # Mitsubishi Chemical
        "京瓷",  # Kyocera
        "国巨",  # Yageo
        "华新科技",  # Walsin
        "基美",  # KEMET
        "威世",  # Vishay
        "顺络电子",  # Sunlord
        "泰科电子",  # TE Connectivity
        "安费诺",  # Amphenol
        "莫仕",  # Molex
        "申泰",  # Samtec
        "航空电子",  # JAE
        "Hirose",
        "矢崎",  # Yazaki
        "航天电器",  # Aerospace Appliance
        "立讯精密",  # Luxshare
        "电连技术",  # Electric Connector
        "意华股份",  # Yihua
        "得润电子",  # Deren
        "中国巨石",  # China Jushi
        "中材科技",  # Sinoma
        "圣泉集团",  # Shengquan
        "飞荣达",  # FRD
        "中石科技",  # Zhongshi
        "领益智造",  # Lingyi
        "骐俊物联",  # Cheerzing
        "龙尚科技",  # Longsung
        "金雅拓",  # Gemalto/Thales
        "与德科技",  # Yude Tech
        "天珑移动",  # Tinno
        "中诺通讯",  # ZNV
        "英国电信",  # BT
        "KDDI",
        "韩国电信",  # KT
        "LG U+",
        "新加坡电信",  # Singtel
        "澳洲电信",  # Telstra
        "沙特电信",  # STC
        "阿联酋电信",  # Etisalat/e&
    ], description="监控的目标公司列表")


class DistributionSettings(BaseSettings):
    """分发配置"""
    model_config = SettingsConfigDict(
        env_prefix="DISTRIBUTION__",
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8-sig",
        extra="ignore"
    )

    smtp_server: str = Field(default="", description="SMTP服务器地址")
    smtp_port: int = Field(default=587, description="SMTP端口")
    smtp_user: str = Field(default="", description="SMTP用户名")
    smtp_password: str = Field(default="", description="SMTP密码")
    smtp_use_tls: bool = Field(default=True, description="是否使用TLS")

    email_recipients: Optional[str] = Field(default=None, description="邮件接收者列表（支持分号/逗号分隔）")
    email_sender: str = Field(default="", description="邮件发送者")

    wechat_webhook_url: str = Field(default="", description="企业微信Webhook URL")

    enable_email: bool = Field(default=False, description="是否启用邮件发送")
    enable_wechat: bool = Field(default=False, description="是否启用微信发送")

    @property
    def email_recipients_list(self) -> List[str]:
        """解析邮件接收者列表，支持多种分隔符格式"""
        raw = self.email_recipients
        if not raw:
            return []
        if raw.startswith('[') and raw.endswith(']'):
            import json
            try:
                return json.loads(raw)
            except:
                pass
        if ';' in raw:
            return [e.strip() for e in raw.split(';') if e.strip()]
        if ',' in raw:
            return [e.strip() for e in raw.split(',') if e.strip()]
        return [raw.strip()]


class ScheduleSettings(BaseSettings):
    """调度配置"""
    model_config = SettingsConfigDict(
        env_prefix="SCHEDULE__",
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8-sig",
        extra="ignore"
    )
    
    day_of_week: str = Field(default="fri", description="周报生成日 (mon,tue,wed,thu,fri,sat,sun)")
    hour: int = Field(default=9, description="小时")
    minute: int = Field(default=0, description="分钟")


class Settings(BaseSettings):
    """全局配置"""
    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8-sig",
        extra="ignore"
    )

    # 子配置
    llm: LLMSettings = LLMSettings()
    collector: CollectorSettings = CollectorSettings()
    distribution: DistributionSettings = DistributionSettings()
    schedule: ScheduleSettings = ScheduleSettings()

    # 项目路径
    project_root: Path = Field(default=Path(__file__).parent, description="项目根目录")
    data_dir: Path = Field(default=Path(__file__).parent / "data", description="数据目录")
    knowledge_base_dir: Path = Field(default=Path(__file__).parent / "knowledge_base", description="知识库目录")

    # 数据库配置
    database_url: str = Field(default="sqlite:///data/intel.db", description="数据库URL")

    # RAG配置
    vector_db_path: str = Field(default="knowledge_base/chroma_db", description="向量数据库路径")
    embedding_model: str = Field(default="all-MiniLM-L6-v2", description="嵌入模型名称")
    top_k: int = Field(default=5, description="RAG检索返回的文档数量")
    similarity_threshold: float = Field(default=0.7, description="相似度阈值")

    # 日志配置
    log_level: str = Field(default="INFO", description="日志级别")
    log_file: str = Field(default="data/telecom_intel.log", description="日志文件路径")

    # ===== Agent升级配置 =====
    # ReAct 工具调用循环配置
    enable_react: bool = Field(default=True, description="是否启用ReAct工具调用循环")
    react_max_iterations: int = Field(default=3, description="ReAct循环最大轮数")
    react_trigger_min_summary_len: int = Field(default=200, description="摘要短于此长度时启用ReAct")

    # 批量二次审查配置
    enable_critic: bool = Field(default=True, description="是否启用批量二次审查")
    critic_batch_size: int = Field(default=10, description="批量审查的批次大小")

    # 周计划配置
    enable_planning: bool = Field(default=True, description="是否启用每周自主规划")
    memory_weeks_context: int = Field(default=3, description="历史记忆读取周数")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 确保目录存在
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.knowledge_base_dir.mkdir(parents=True, exist_ok=True)


# 全局配置实例
settings = Settings()
