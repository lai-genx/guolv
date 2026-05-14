"""
Web采集器网站配置 v3.0 - 完整152企业版
更新时间：2026-04-04

总计企业数: 107
- P0（设备商+运营商）: 58
- P1（中上游）: 28
- P2（其他）: 21

策略: 现有企业保留原配置，新增81企业使用Jina Reader fallback
"""

DEFAULT_SITES = [
    {
        "name": "高通",  # 1
        "url": "https://www.qualcomm.com/news/",
        "list_selector": ".news-list .news-item, .news-item, .list-item li, article, li",
        "title_selector": "h3, h2, h1, .title, a, .news-title",
        "link_selector": "a[href*='news'], a[href*='press'], a[href], a",
        "date_selector": ".date, .time, .publish-date, time, .news-date",
        "base_url": "https://www.qualcomm.com",
        "priority": "P0",
        "use_jina_only": False
    },
    {
        "name": "中际旭创",  # 2
        "url": "https://www.innolight.com.cn/News/",
        "list_selector": ".news-list .news-item, .news-item, .list-item li, article, li",
        "title_selector": "h3, h2, h1, .title, a, .news-title",
        "link_selector": "a[href*='news'], a[href*='press'], a[href], a",
        "date_selector": ".date, .time, .publish-date, time, .news-date",
        "base_url": "https://www.innolight.com.cn/News",
        "priority": "P0",
        "use_jina_only": False
    },
    {
        "name": "思科",  # 3
        "url": "https://www.cisco.com/c/en/us/news/",
        "list_selector": ".news-list .news-item, .news-item, .list-item li, article, li",
        "title_selector": "h3, h2, h1, .title, a, .news-title",
        "link_selector": "a[href*='news'], a[href*='press'], a[href], a",
        "date_selector": ".date, .time, .publish-date, time, .news-date",
        "base_url": "https://www.cisco.com/c/en/us",
        "priority": "P0",
        "use_jina_only": False
    },
    {
        "name": "华为",  # 4
        "url": "https://www.huawei.com/cn/news/",
        "list_selector": ".news-list .news-item, .news-item, .list-item li, article, li",
        "title_selector": "h3, h2, h1, .title, a, .news-title",
        "link_selector": "a[href*='news'], a[href*='press'], a[href], a",
        "date_selector": ".date, .time, .publish-date, time, .news-date",
        "base_url": "https://www.huawei.com/cn",
        "priority": "P0",
        "use_jina_only": False
    },
    {
        "name": "中兴通讯",  # 5
        "url": "https://www.zte.com.cn/chn/about/news/",
        "list_selector": ".news-list .news-item, .news-item, .list-item li, article, li",
        "title_selector": "h3, h2, h1, .title, a, .news-title",
        "link_selector": "a[href*='news'], a[href*='press'], a[href], a",
        "date_selector": ".date, .time, .publish-date, time, .news-date",
        "base_url": "https://www.zte.com.cn/chn/about",
        "priority": "P0",
        "use_jina_only": False
    },
    {
        "name": "烽火通信",  # 6
        "url": "https://www.fiberhome.com.cn/newslist/",
        "list_selector": ".news-list .news-item, .news-item, .list-item li, article, li",
        "title_selector": "h3, h2, h1, .title, a, .news-title",
        "link_selector": "a[href*='news'], a[href*='press'], a[href], a",
        "date_selector": ".date, .time, .publish-date, time, .news-date",
        "base_url": "https://www.fiberhome.com.cn",
        "priority": "P0",
        "use_jina_only": False
    },
    {
        "name": "爱立信",  # 7
        "url": "https://www.ericsson.com/en/news/",
        "list_selector": ".news-list .news-item, .news-item, .list-item li, article, li",
        "title_selector": "h3, h2, h1, .title, a, .news-title",
        "link_selector": "a[href*='news'], a[href*='press'], a[href], a",
        "date_selector": ".date, .time, .publish-date, time, .news-date",
        "base_url": "https://www.ericsson.com/en",
        "priority": "P0",
        "use_jina_only": False
    },
    {
        "name": "诺基亚",  # 8
        "url": "https://www.nokia.com/en/news/",
        "list_selector": ".news-list .news-item, .news-item, .list-item li, article, li",
        "title_selector": "h3, h2, h1, .title, a, .news-title",
        "link_selector": "a[href*='news'], a[href*='press'], a[href], a",
        "date_selector": ".date, .time, .publish-date, time, .news-date",
        "base_url": "https://www.nokia.com/en",
        "priority": "P0",
        "use_jina_only": False
    },
    {
        "name": "华为",  # 9
        "url": "https://www.huawei.com/cn/news/",
        "list_selector": ".news-list .news-item, .news-item, .list-item li, article, li",
        "title_selector": "h3, h2, h1, .title, a, .news-title",
        "link_selector": "a[href*='news'], a[href*='press'], a[href], a",
        "date_selector": ".date, .time, .publish-date, time, .news-date",
        "base_url": "https://www.huawei.com/cn",
        "priority": "P0",
        "use_jina_only": False
    },
    {
        "name": "中兴通讯",  # 10
        "url": "https://www.zte.com.cn/chn/about/news/",
        "list_selector": ".news-list .news-item, .news-item, .list-item li, article, li",
        "title_selector": "h3, h2, h1, .title, a, .news-title",
        "link_selector": "a[href*='news'], a[href*='press'], a[href], a",
        "date_selector": ".date, .time, .publish-date, time, .news-date",
        "base_url": "https://www.zte.com.cn/chn/about",
        "priority": "P0",
        "use_jina_only": False
    },
    {
        "name": "烽火通信",  # 11
        "url": "https://www.fiberhome.com.cn/newslist/",
        "list_selector": ".news-list .news-item, .news-item, .list-item li, article, li",
        "title_selector": "h3, h2, h1, .title, a, .news-title",
        "link_selector": "a[href*='news'], a[href*='press'], a[href], a",
        "date_selector": ".date, .time, .publish-date, time, .news-date",
        "base_url": "https://www.fiberhome.com.cn",
        "priority": "P0",
        "use_jina_only": False
    },
    {
        "name": "新华三",  # 12
        "url": "https://www.h3c.com.cn/Home/News/",
        "list_selector": ".news-list .news-item, .news-item, .list-item li, article, li",
        "title_selector": "h3, h2, h1, .title, a, .news-title",
        "link_selector": "a[href*='news'], a[href*='press'], a[href], a",
        "date_selector": ".date, .time, .publish-date, time, .news-date",
        "base_url": "https://www.h3c.com.cn/Home/News",
        "priority": "P0",
        "use_jina_only": False
    },
    {
        "name": "锐捷网络",  # 13
        "url": "https://www.ruijie.com.cn/Home/News/",
        "list_selector": ".news-list .news-item, .news-item, .list-item li, article, li",
        "title_selector": "h3, h2, h1, .title, a, .news-title",
        "link_selector": "a[href*='news'], a[href*='press'], a[href], a",
        "date_selector": ".date, .time, .publish-date, time, .news-date",
        "base_url": "https://www.ruijie.com.cn/Home/News",
        "priority": "P0",
        "use_jina_only": False
    },
    {
        "name": "诺基亚",  # 14
        "url": "https://www.nokia.com/en/news/",
        "list_selector": ".news-list .news-item, .news-item, .list-item li, article, li",
        "title_selector": "h3, h2, h1, .title, a, .news-title",
        "link_selector": "a[href*='news'], a[href*='press'], a[href], a",
        "date_selector": ".date, .time, .publish-date, time, .news-date",
        "base_url": "https://www.nokia.com/en",
        "priority": "P0",
        "use_jina_only": False
    },
    {
        "name": "爱立信",  # 15
        "url": "https://www.ericsson.com/en/news/",
        "list_selector": ".news-list .news-item, .news-item, .list-item li, article, li",
        "title_selector": "h3, h2, h1, .title, a, .news-title",
        "link_selector": "a[href*='news'], a[href*='press'], a[href], a",
        "date_selector": ".date, .time, .publish-date, time, .news-date",
        "base_url": "https://www.ericsson.com/en",
        "priority": "P0",
        "use_jina_only": False
    },
    {
        "name": "华为",  # 16
        "url": "https://www.huawei.com/cn/news/",
        "list_selector": ".news-list .news-item, .news-item, .list-item li, article, li",
        "title_selector": "h3, h2, h1, .title, a, .news-title",
        "link_selector": "a[href*='news'], a[href*='press'], a[href], a",
        "date_selector": ".date, .time, .publish-date, time, .news-date",
        "base_url": "https://www.huawei.com/cn",
        "priority": "P0",
        "use_jina_only": False
    },
    {
        "name": "中兴通讯",  # 17
        "url": "https://www.zte.com.cn/chn/about/news/",
        "list_selector": ".news-list .news-item, .news-item, .list-item li, article, li",
        "title_selector": "h3, h2, h1, .title, a, .news-title",
        "link_selector": "a[href*='news'], a[href*='press'], a[href], a",
        "date_selector": ".date, .time, .publish-date, time, .news-date",
        "base_url": "https://www.zte.com.cn/chn/about",
        "priority": "P0",
        "use_jina_only": False
    },
    {
        "name": "新华三",  # 18
        "url": "https://www.h3c.com.cn/Home/News/",
        "list_selector": ".news-list .news-item, .news-item, .list-item li, article, li",
        "title_selector": "h3, h2, h1, .title, a, .news-title",
        "link_selector": "a[href*='news'], a[href*='press'], a[href], a",
        "date_selector": ".date, .time, .publish-date, time, .news-date",
        "base_url": "https://www.h3c.com.cn/Home/News",
        "priority": "P0",
        "use_jina_only": False
    },
    {
        "name": "锐捷网络",  # 19
        "url": "https://www.ruijie.com.cn/Home/News/",
        "list_selector": ".news-list .news-item, .news-item, .list-item li, article, li",
        "title_selector": "h3, h2, h1, .title, a, .news-title",
        "link_selector": "a[href*='news'], a[href*='press'], a[href], a",
        "date_selector": ".date, .time, .publish-date, time, .news-date",
        "base_url": "https://www.ruijie.com.cn/Home/News",
        "priority": "P0",
        "use_jina_only": False
    },
    {
        "name": "思科",  # 20
        "url": "https://www.cisco.com/c/en/us/news/",
        "list_selector": ".news-list .news-item, .news-item, .list-item li, article, li",
        "title_selector": "h3, h2, h1, .title, a, .news-title",
        "link_selector": "a[href*='news'], a[href*='press'], a[href], a",
        "date_selector": ".date, .time, .publish-date, time, .news-date",
        "base_url": "https://www.cisco.com/c/en/us",
        "priority": "P0",
        "use_jina_only": False
    },
    {
        "name": "爱立信",  # 21
        "url": "https://www.ericsson.com/en/news/",
        "list_selector": ".news-list .news-item, .news-item, .list-item li, article, li",
        "title_selector": "h3, h2, h1, .title, a, .news-title",
        "link_selector": "a[href*='news'], a[href*='press'], a[href], a",
        "date_selector": ".date, .time, .publish-date, time, .news-date",
        "base_url": "https://www.ericsson.com/en",
        "priority": "P0",
        "use_jina_only": False
    },
    {
        "name": "诺基亚",  # 22
        "url": "https://www.nokia.com/en/news/",
        "list_selector": ".news-list .news-item, .news-item, .list-item li, article, li",
        "title_selector": "h3, h2, h1, .title, a, .news-title",
        "link_selector": "a[href*='news'], a[href*='press'], a[href], a",
        "date_selector": ".date, .time, .publish-date, time, .news-date",
        "base_url": "https://www.nokia.com/en",
        "priority": "P0",
        "use_jina_only": False
    },
    {
        "name": "中国移动",  # 23
        "url": "https://www.10086.cn/about/news/",
        "list_selector": ".news-list .news-item, .news-item, .list-item li, article, li",
        "title_selector": "h3, h2, h1, .title, a, .news-title",
        "link_selector": "a[href*='news'], a[href*='press'], a[href], a",
        "date_selector": ".date, .time, .publish-date, time, .news-date",
        "base_url": "https://www.10086.cn/about",
        "priority": "P0",
        "use_jina_only": False
    },
    {
        "name": "中国电信",  # 24
        "url": "https://www.chinatelecom.com.cn/news/",
        "list_selector": ".news-list .news-item, .news-item, .list-item li, article, li",
        "title_selector": "h3, h2, h1, .title, a, .news-title",
        "link_selector": "a[href*='news'], a[href*='press'], a[href], a",
        "date_selector": ".date, .time, .publish-date, time, .news-date",
        "base_url": "https://www.chinatelecom.com.cn",
        "priority": "P0",
        "use_jina_only": False
    },
    {
        "name": "中国联通",  # 25
        "url": "https://www.chinaunicom.com.cn/news/",
        "list_selector": ".news-list .news-item, .news-item, .list-item li, article, li",
        "title_selector": "h3, h2, h1, .title, a, .news-title",
        "link_selector": "a[href*='news'], a[href*='press'], a[href], a",
        "date_selector": ".date, .time, .publish-date, time, .news-date",
        "base_url": "https://www.chinaunicom.com.cn",
        "priority": "P0",
        "use_jina_only": False
    },
    {
        "name": "中国铁塔",  # 26
        "url": "https://www.china-tower.com/news/",
        "list_selector": ".news-list .news-item, .news-item, .list-item li, article, li",
        "title_selector": "h3, h2, h1, .title, a, .news-title",
        "link_selector": "a[href*='news'], a[href*='press'], a[href], a",
        "date_selector": ".date, .time, .publish-date, time, .news-date",
        "base_url": "https://www.china-tower.com",
        "priority": "P0",
        "use_jina_only": False
    },
    {
        "name": "紫光展锐",  # 27
        "url": "https://www.unisoc.com/",
        "list_selector": ".news-list .news-item, .news-item, .list-item li, article, li",
        "title_selector": "h3, h2, h1, .title, a, .news-title",
        "link_selector": "a[href*='news'], a[href*='press'], a[href], a",
        "date_selector": ".date, .time, .publish-date, time, .news-date",
        "base_url": "https://www.unisoc.com",
        "priority": "P1",
        "use_jina_only": True
    },
    {
        "name": "翱捷科技",  # 28
        "url": "https://www.asrmicro.com/",
        "list_selector": ".news-list .news-item, .news-item, .list-item li, article, li",
        "title_selector": "h3, h2, h1, .title, a, .news-title",
        "link_selector": "a[href*='news'], a[href*='press'], a[href], a",
        "date_selector": ".date, .time, .publish-date, time, .news-date",
        "base_url": "https://www.asrmicro.com",
        "priority": "P1",
        "use_jina_only": True
    },
    {
        "name": "移芯通信",  # 29
        "url": "https://www.xtechcomm.com/",
        "list_selector": ".news-list .news-item, .news-item, .list-item li, article, li",
        "title_selector": "h3, h2, h1, .title, a, .news-title",
        "link_selector": "a[href*='news'], a[href*='press'], a[href], a",
        "date_selector": ".date, .time, .publish-date, time, .news-date",
        "base_url": "https://www.xtechcomm.com",
        "priority": "P1",
        "use_jina_only": True
    },
    {
        "name": "瑞芯微电子",  # 30
        "url": "https://www.rock-chips.com/",
        "list_selector": ".news-list .news-item, .news-item, .list-item li, article, li",
        "title_selector": "h3, h2, h1, .title, a, .news-title",
        "link_selector": "a[href*='news'], a[href*='press'], a[href], a",
        "date_selector": ".date, .time, .publish-date, time, .news-date",
        "base_url": "https://www.rock-chips.com",
        "priority": "P1",
        "use_jina_only": True
    },
    {
        "name": "唯捷创芯",  # 31
        "url": "http://www.wayjem.com/",
        "list_selector": ".news-list .news-item, .news-item, .list-item li, article, li",
        "title_selector": "h3, h2, h1, .title, a, .news-title",
        "link_selector": "a[href*='news'], a[href*='press'], a[href], a",
        "date_selector": ".date, .time, .publish-date, time, .news-date",
        "base_url": "http://www.wayjem.com",
        "priority": "P1",
        "use_jina_only": True
    },
    {
        "name": "中科汉天下",  # 32
        "url": "http://www.hexintek.com/",
        "list_selector": ".news-list .news-item, .news-item, .list-item li, article, li",
        "title_selector": "h3, h2, h1, .title, a, .news-title",
        "link_selector": "a[href*='news'], a[href*='press'], a[href], a",
        "date_selector": ".date, .time, .publish-date, time, .news-date",
        "base_url": "http://www.hexintek.com",
        "priority": "P1",
        "use_jina_only": True
    },
    {
        "name": "卓胜微",  # 33
        "url": "https://www.zhuoshengwei.com/",
        "list_selector": ".news-list .news-item, .news-item, .list-item li, article, li",
        "title_selector": "h3, h2, h1, .title, a, .news-title",
        "link_selector": "a[href*='news'], a[href*='press'], a[href], a",
        "date_selector": ".date, .time, .publish-date, time, .news-date",
        "base_url": "https://www.zhuoshengwei.com",
        "priority": "P1",
        "use_jina_only": True
    },
    {
        "name": "慧智微",  # 34
        "url": "https://www.microintelli.com/",
        "list_selector": ".news-list .news-item, .news-item, .list-item li, article, li",
        "title_selector": "h3, h2, h1, .title, a, .news-title",
        "link_selector": "a[href*='news'], a[href*='press'], a[href], a",
        "date_selector": ".date, .time, .publish-date, time, .news-date",
        "base_url": "https://www.microintelli.com",
        "priority": "P1",
        "use_jina_only": True
    },
    {
        "name": "格科微电子",  # 35
        "url": "https://www.gcoreinc.com/",
        "list_selector": ".news-list .news-item, .news-item, .list-item li, article, li",
        "title_selector": "h3, h2, h1, .title, a, .news-title",
        "link_selector": "a[href*='news'], a[href*='press'], a[href], a",
        "date_selector": ".date, .time, .publish-date, time, .news-date",
        "base_url": "https://www.gcoreinc.com",
        "priority": "P1",
        "use_jina_only": True
    },
    {
        "name": "光迅科技",  # 36
        "url": "https://www.accelink.com/",
        "list_selector": ".news-list .news-item, .news-item, .list-item li, article, li",
        "title_selector": "h3, h2, h1, .title, a, .news-title",
        "link_selector": "a[href*='news'], a[href*='press'], a[href], a",
        "date_selector": ".date, .time, .publish-date, time, .news-date",
        "base_url": "https://www.accelink.com",
        "priority": "P1",
        "use_jina_only": True
    },
    {
        "name": "源杰科技",  # 37
        "url": "https://www.synlighttech.com/",
        "list_selector": ".news-list .news-item, .news-item, .list-item li, article, li",
        "title_selector": "h3, h2, h1, .title, a, .news-title",
        "link_selector": "a[href*='news'], a[href*='press'], a[href], a",
        "date_selector": ".date, .time, .publish-date, time, .news-date",
        "base_url": "https://www.synlighttech.com",
        "priority": "P1",
        "use_jina_only": True
    },
    {
        "name": "仕佳光子",  # 38
        "url": "https://www.shijiaphotonics.com/",
        "list_selector": ".news-list .news-item, .news-item, .list-item li, article, li",
        "title_selector": "h3, h2, h1, .title, a, .news-title",
        "link_selector": "a[href*='news'], a[href*='press'], a[href], a",
        "date_selector": ".date, .time, .publish-date, time, .news-date",
        "base_url": "https://www.shijiaphotonics.com",
        "priority": "P1",
        "use_jina_only": True
    },
    {
        "name": "思比科",  # 39
        "url": "https://www.siliconimage.com.cn/",
        "list_selector": ".news-list .news-item, .news-item, .list-item li, article, li",
        "title_selector": "h3, h2, h1, .title, a, .news-title",
        "link_selector": "a[href*='news'], a[href*='press'], a[href], a",
        "date_selector": ".date, .time, .publish-date, time, .news-date",
        "base_url": "https://www.siliconimage.com.cn",
        "priority": "P1",
        "use_jina_only": True
    },
    {
        "name": "联发科",  # 40
        "url": "https://www.mediatek.com/",
        "list_selector": ".news-list .news-item, .news-item, .list-item li, article, li",
        "title_selector": "h3, h2, h1, .title, a, .news-title",
        "link_selector": "a[href*='news'], a[href*='press'], a[href], a",
        "date_selector": ".date, .time, .publish-date, time, .news-date",
        "base_url": "https://www.mediatek.com",
        "priority": "P1",
        "use_jina_only": True
    },
    {
        "name": "三星LSI",  # 41
        "url": "https://semiconductor.samsung.com/",
        "list_selector": ".news-list .news-item, .news-item, .list-item li, article, li",
        "title_selector": "h3, h2, h1, .title, a, .news-title",
        "link_selector": "a[href*='news'], a[href*='press'], a[href], a",
        "date_selector": ".date, .time, .publish-date, time, .news-date",
        "base_url": "https://semiconductor.samsung.com",
        "priority": "P1",
        "use_jina_only": True
    },
    {
        "name": "英特尔",  # 42
        "url": "https://www.intel.com/",
        "list_selector": ".news-list .news-item, .news-item, .list-item li, article, li",
        "title_selector": "h3, h2, h1, .title, a, .news-title",
        "link_selector": "a[href*='news'], a[href*='press'], a[href], a",
        "date_selector": ".date, .time, .publish-date, time, .news-date",
        "base_url": "https://www.intel.com",
        "priority": "P1",
        "use_jina_only": True
    },
    {
        "name": "Coherent",  # 43
        "url": "https://www.coherent.com/",
        "list_selector": ".news-list .news-item, .news-item, .list-item li, article, li",
        "title_selector": "h3, h2, h1, .title, a, .news-title",
        "link_selector": "a[href*='news'], a[href*='press'], a[href], a",
        "date_selector": ".date, .time, .publish-date, time, .news-date",
        "base_url": "https://www.coherent.com",
        "priority": "P1",
        "use_jina_only": True
    },
    {
        "name": "Lumentum",  # 44
        "url": "https://www.lumentum.com/",
        "list_selector": ".news-list .news-item, .news-item, .list-item li, article, li",
        "title_selector": "h3, h2, h1, .title, a, .news-title",
        "link_selector": "a[href*='news'], a[href*='press'], a[href], a",
        "date_selector": ".date, .time, .publish-date, time, .news-date",
        "base_url": "https://www.lumentum.com",
        "priority": "P1",
        "use_jina_only": True
    },
    {
        "name": "Broadcom",  # 45
        "url": "https://www.broadcom.com/",
        "list_selector": ".news-list .news-item, .news-item, .list-item li, article, li",
        "title_selector": "h3, h2, h1, .title, a, .news-title",
        "link_selector": "a[href*='news'], a[href*='press'], a[href], a",
        "date_selector": ".date, .time, .publish-date, time, .news-date",
        "base_url": "https://www.broadcom.com",
        "priority": "P1",
        "use_jina_only": True
    },
    {
        "name": "德州仪器",  # 46
        "url": "https://www.ti.com/",
        "list_selector": ".news-list .news-item, .news-item, .list-item li, article, li",
        "title_selector": "h3, h2, h1, .title, a, .news-title",
        "link_selector": "a[href*='news'], a[href*='press'], a[href], a",
        "date_selector": ".date, .time, .publish-date, time, .news-date",
        "base_url": "https://www.ti.com",
        "priority": "P1",
        "use_jina_only": True
    },
    {
        "name": "新易盛",  # 47
        "url": "https://www.eoptolink.com/",
        "list_selector": ".news-list .news-item, .news-item, .list-item li, article, li",
        "title_selector": "h3, h2, h1, .title, a, .news-title",
        "link_selector": "a[href*='news'], a[href*='press'], a[href], a",
        "date_selector": ".date, .time, .publish-date, time, .news-date",
        "base_url": "https://www.eoptolink.com",
        "priority": "P1",
        "use_jina_only": True
    },
    {
        "name": "光迅科技",  # 48
        "url": "https://www.accelink.com/",
        "list_selector": ".news-list .news-item, .news-item, .list-item li, article, li",
        "title_selector": "h3, h2, h1, .title, a, .news-title",
        "link_selector": "a[href*='news'], a[href*='press'], a[href], a",
        "date_selector": ".date, .time, .publish-date, time, .news-date",
        "base_url": "https://www.accelink.com",
        "priority": "P1",
        "use_jina_only": True
    },
    {
        "name": "华工正源",  # 49
        "url": "https://www.hgzy.com.cn/",
        "list_selector": ".news-list .news-item, .news-item, .list-item li, article, li",
        "title_selector": "h3, h2, h1, .title, a, .news-title",
        "link_selector": "a[href*='news'], a[href*='press'], a[href], a",
        "date_selector": ".date, .time, .publish-date, time, .news-date",
        "base_url": "https://www.hgzy.com.cn",
        "priority": "P1",
        "use_jina_only": True
    },
    {
        "name": "海信宽带",  # 50
        "url": "https://www.hisense-broadband.com/",
        "list_selector": ".news-list .news-item, .news-item, .list-item li, article, li",
        "title_selector": "h3, h2, h1, .title, a, .news-title",
        "link_selector": "a[href*='news'], a[href*='press'], a[href], a",
        "date_selector": ".date, .time, .publish-date, time, .news-date",
        "base_url": "https://www.hisense-broadband.com",
        "priority": "P1",
        "use_jina_only": True
    },
    {
        "name": "索尔思光电",  # 51
        "url": "https://www.sourcephotonics.com/",
        "list_selector": ".news-list .news-item, .news-item, .list-item li, article, li",
        "title_selector": "h3, h2, h1, .title, a, .news-title",
        "link_selector": "a[href*='news'], a[href*='press'], a[href], a",
        "date_selector": ".date, .time, .publish-date, time, .news-date",
        "base_url": "https://www.sourcephotonics.com",
        "priority": "P1",
        "use_jina_only": True
    },
    {
        "name": "天孚通信",  # 52
        "url": "https://www.turfib.com/",
        "list_selector": ".news-list .news-item, .news-item, .list-item li, article, li",
        "title_selector": "h3, h2, h1, .title, a, .news-title",
        "link_selector": "a[href*='news'], a[href*='press'], a[href], a",
        "date_selector": ".date, .time, .publish-date, time, .news-date",
        "base_url": "https://www.turfib.com",
        "priority": "P1",
        "use_jina_only": True
    },
    {
        "name": "Coherent",  # 53
        "url": "https://www.coherent.com/",
        "list_selector": ".news-list .news-item, .news-item, .list-item li, article, li",
        "title_selector": "h3, h2, h1, .title, a, .news-title",
        "link_selector": "a[href*='news'], a[href*='press'], a[href], a",
        "date_selector": ".date, .time, .publish-date, time, .news-date",
        "base_url": "https://www.coherent.com",
        "priority": "P1",
        "use_jina_only": True
    },
    {
        "name": "英特尔",  # 54
        "url": "https://www.intel.com/",
        "list_selector": ".news-list .news-item, .news-item, .list-item li, article, li",
        "title_selector": "h3, h2, h1, .title, a, .news-title",
        "link_selector": "a[href*='news'], a[href*='press'], a[href], a",
        "date_selector": ".date, .time, .publish-date, time, .news-date",
        "base_url": "https://www.intel.com",
        "priority": "P1",
        "use_jina_only": True
    },
    {
        "name": "通宇通讯",  # 55
        "url": "https://www.tytx.com.cn/",
        "list_selector": ".news-list .news-item, .news-item, .list-item li, article, li",
        "title_selector": "h3, h2, h1, .title, a, .news-title",
        "link_selector": "a[href*='news'], a[href*='press'], a[href], a",
        "date_selector": ".date, .time, .publish-date, time, .news-date",
        "base_url": "https://www.tytx.com.cn",
        "priority": "P0",
        "use_jina_only": False
    },
    {
        "name": "京信通信",  # 56
        "url": "https://www.comba.net.cn/",
        "list_selector": ".news-list .news-item, .news-item, .list-item li, article, li",
        "title_selector": "h3, h2, h1, .title, a, .news-title",
        "link_selector": "a[href*='news'], a[href*='press'], a[href], a",
        "date_selector": ".date, .time, .publish-date, time, .news-date",
        "base_url": "https://www.comba.net.cn",
        "priority": "P0",
        "use_jina_only": False
    },
    {
        "name": "摩比发展",  # 57
        "url": "https://www.mobie.com.cn/",
        "list_selector": ".news-list .news-item, .news-item, .list-item li, article, li",
        "title_selector": "h3, h2, h1, .title, a, .news-title",
        "link_selector": "a[href*='news'], a[href*='press'], a[href], a",
        "date_selector": ".date, .time, .publish-date, time, .news-date",
        "base_url": "https://www.mobie.com.cn",
        "priority": "P0",
        "use_jina_only": False
    },
    {
        "name": "盛路通信",  # 58
        "url": "https://www.shenglu.com/",
        "list_selector": ".news-list .news-item, .news-item, .list-item li, article, li",
        "title_selector": "h3, h2, h1, .title, a, .news-title",
        "link_selector": "a[href*='news'], a[href*='press'], a[href], a",
        "date_selector": ".date, .time, .publish-date, time, .news-date",
        "base_url": "https://www.shenglu.com",
        "priority": "P0",
        "use_jina_only": False
    },
    {
        "name": "武汉凡谷",  # 59
        "url": "https://www.fangu.com/",
        "list_selector": ".news-list .news-item, .news-item, .list-item li, article, li",
        "title_selector": "h3, h2, h1, .title, a, .news-title",
        "link_selector": "a[href*='news'], a[href*='press'], a[href], a",
        "date_selector": ".date, .time, .publish-date, time, .news-date",
        "base_url": "https://www.fangu.com",
        "priority": "P0",
        "use_jina_only": False
    },
    {
        "name": "大富科技",  # 60
        "url": "https://www.tuftiem.com/",
        "list_selector": ".news-list .news-item, .news-item, .list-item li, article, li",
        "title_selector": "h3, h2, h1, .title, a, .news-title",
        "link_selector": "a[href*='news'], a[href*='press'], a[href], a",
        "date_selector": ".date, .time, .publish-date, time, .news-date",
        "base_url": "https://www.tuftiem.com",
        "priority": "P0",
        "use_jina_only": False
    },
    {
        "name": "东山精密",  # 61
        "url": "https://www.dongsheng.com/",
        "list_selector": ".news-list .news-item, .news-item, .list-item li, article, li",
        "title_selector": "h3, h2, h1, .title, a, .news-title",
        "link_selector": "a[href*='news'], a[href*='press'], a[href], a",
        "date_selector": ".date, .time, .publish-date, time, .news-date",
        "base_url": "https://www.dongsheng.com",
        "priority": "P0",
        "use_jina_only": False
    },
    {
        "name": "中电科55所",  # 62
        "url": "https://www.cetc55.com/",
        "list_selector": ".news-list .news-item, .news-item, .list-item li, article, li",
        "title_selector": "h3, h2, h1, .title, a, .news-title",
        "link_selector": "a[href*='news'], a[href*='press'], a[href], a",
        "date_selector": ".date, .time, .publish-date, time, .news-date",
        "base_url": "https://www.cetc55.com",
        "priority": "P0",
        "use_jina_only": False
    },
    {
        "name": "康普通讯",  # 63
        "url": "https://www.commscope.com/",
        "list_selector": ".news-list .news-item, .news-item, .list-item li, article, li",
        "title_selector": "h3, h2, h1, .title, a, .news-title",
        "link_selector": "a[href*='news'], a[href*='press'], a[href], a",
        "date_selector": ".date, .time, .publish-date, time, .news-date",
        "base_url": "https://www.commscope.com",
        "priority": "P0",
        "use_jina_only": False
    },
    {
        "name": "凯士林",  # 64
        "url": "https://www.kathrein.com/",
        "list_selector": ".news-list .news-item, .news-item, .list-item li, article, li",
        "title_selector": "h3, h2, h1, .title, a, .news-title",
        "link_selector": "a[href*='news'], a[href*='press'], a[href], a",
        "date_selector": ".date, .time, .publish-date, time, .news-date",
        "base_url": "https://www.kathrein.com",
        "priority": "P0",
        "use_jina_only": False
    },
    {
        "name": "RFS",  # 65
        "url": "https://www.rfsworld.com/",
        "list_selector": ".news-list .news-item, .news-item, .list-item li, article, li",
        "title_selector": "h3, h2, h1, .title, a, .news-title",
        "link_selector": "a[href*='news'], a[href*='press'], a[href], a",
        "date_selector": ".date, .time, .publish-date, time, .news-date",
        "base_url": "https://www.rfsworld.com",
        "priority": "P0",
        "use_jina_only": False
    },
    {
        "name": "三星电子",  # 66
        "url": "https://www.samsung.com/",
        "list_selector": ".news-list .news-item, .news-item, .list-item li, article, li",
        "title_selector": "h3, h2, h1, .title, a, .news-title",
        "link_selector": "a[href*='news'], a[href*='press'], a[href], a",
        "date_selector": ".date, .time, .publish-date, time, .news-date",
        "base_url": "https://www.samsung.com",
        "priority": "P0",
        "use_jina_only": False
    },
    {
        "name": "Mavenir",  # 67
        "url": "https://www.mavenir.com/",
        "list_selector": ".news-list .news-item, .news-item, .list-item li, article, li",
        "title_selector": "h3, h2, h1, .title, a, .news-title",
        "link_selector": "a[href*='news'], a[href*='press'], a[href], a",
        "date_selector": ".date, .time, .publish-date, time, .news-date",
        "base_url": "https://www.mavenir.com",
        "priority": "P0",
        "use_jina_only": False
    },
    {
        "name": "长飞光纤",  # 68
        "url": "https://www.yofc.com/",
        "list_selector": ".news-list .news-item, .news-item, .list-item li, article, li",
        "title_selector": "h3, h2, h1, .title, a, .news-title",
        "link_selector": "a[href*='news'], a[href*='press'], a[href], a",
        "date_selector": ".date, .time, .publish-date, time, .news-date",
        "base_url": "https://www.yofc.com",
        "priority": "P0",
        "use_jina_only": True
    },
    {
        "name": "中天科技",  # 69
        "url": "https://www.zhongtiantech.com/",
        "list_selector": ".news-list .news-item, .news-item, .list-item li, article, li",
        "title_selector": "h3, h2, h1, .title, a, .news-title",
        "link_selector": "a[href*='news'], a[href*='press'], a[href], a",
        "date_selector": ".date, .time, .publish-date, time, .news-date",
        "base_url": "https://www.zhongtiantech.com",
        "priority": "P0",
        "use_jina_only": True
    },
    {
        "name": "亨通光电",  # 70
        "url": "https://www.hengtonggroup.com/",
        "list_selector": ".news-list .news-item, .news-item, .list-item li, article, li",
        "title_selector": "h3, h2, h1, .title, a, .news-title",
        "link_selector": "a[href*='news'], a[href*='press'], a[href], a",
        "date_selector": ".date, .time, .publish-date, time, .news-date",
        "base_url": "https://www.hengtonggroup.com",
        "priority": "P0",
        "use_jina_only": True
    },
    {
        "name": "Ciena",  # 71
        "url": "https://www.ciena.com/",
        "list_selector": ".news-list .news-item, .news-item, .list-item li, article, li",
        "title_selector": "h3, h2, h1, .title, a, .news-title",
        "link_selector": "a[href*='news'], a[href*='press'], a[href], a",
        "date_selector": ".date, .time, .publish-date, time, .news-date",
        "base_url": "https://www.ciena.com",
        "priority": "P0",
        "use_jina_only": True
    },
    {
        "name": "Infinera",  # 72
        "url": "https://www.infinera.com/",
        "list_selector": ".news-list .news-item, .news-item, .list-item li, article, li",
        "title_selector": "h3, h2, h1, .title, a, .news-title",
        "link_selector": "a[href*='news'], a[href*='press'], a[href], a",
        "date_selector": ".date, .time, .publish-date, time, .news-date",
        "base_url": "https://www.infinera.com",
        "priority": "P0",
        "use_jina_only": True
    },
    {
        "name": "Calix",  # 73
        "url": "https://www.calix.com/",
        "list_selector": ".news-list .news-item, .news-item, .list-item li, article, li",
        "title_selector": "h3, h2, h1, .title, a, .news-title",
        "link_selector": "a[href*='news'], a[href*='press'], a[href], a",
        "date_selector": ".date, .time, .publish-date, time, .news-date",
        "base_url": "https://www.calix.com",
        "priority": "P0",
        "use_jina_only": True
    },
    {
        "name": "ADTRAN",  # 74
        "url": "https://www.adtran.com/",
        "list_selector": ".news-list .news-item, .news-item, .list-item li, article, li",
        "title_selector": "h3, h2, h1, .title, a, .news-title",
        "link_selector": "a[href*='news'], a[href*='press'], a[href], a",
        "date_selector": ".date, .time, .publish-date, time, .news-date",
        "base_url": "https://www.adtran.com",
        "priority": "P0",
        "use_jina_only": True
    },
    {
        "name": "DZS",  # 75
        "url": "https://www.dzsi.com/",
        "list_selector": ".news-list .news-item, .news-item, .list-item li, article, li",
        "title_selector": "h3, h2, h1, .title, a, .news-title",
        "link_selector": "a[href*='news'], a[href*='press'], a[href], a",
        "date_selector": ".date, .time, .publish-date, time, .news-date",
        "base_url": "https://www.dzsi.com",
        "priority": "P0",
        "use_jina_only": True
    },
    {
        "name": "星网锐捷",  # 76
        "url": "https://www.star-net.com.cn/",
        "list_selector": ".news-list .news-item, .news-item, .list-item li, article, li",
        "title_selector": "h3, h2, h1, .title, a, .news-title",
        "link_selector": "a[href*='news'], a[href*='press'], a[href], a",
        "date_selector": ".date, .time, .publish-date, time, .news-date",
        "base_url": "https://www.star-net.com.cn",
        "priority": "P2",
        "use_jina_only": True
    },
    {
        "name": "Juniper",  # 77
        "url": "https://www.juniper.net/",
        "list_selector": ".news-list .news-item, .news-item, .list-item li, article, li",
        "title_selector": "h3, h2, h1, .title, a, .news-title",
        "link_selector": "a[href*='news'], a[href*='press'], a[href], a",
        "date_selector": ".date, .time, .publish-date, time, .news-date",
        "base_url": "https://www.juniper.net",
        "priority": "P2",
        "use_jina_only": True
    },
    {
        "name": "Arista Networks",  # 78
        "url": "https://www.arista.com/",
        "list_selector": ".news-list .news-item, .news-item, .list-item li, article, li",
        "title_selector": "h3, h2, h1, .title, a, .news-title",
        "link_selector": "a[href*='news'], a[href*='press'], a[href], a",
        "date_selector": ".date, .time, .publish-date, time, .news-date",
        "base_url": "https://www.arista.com",
        "priority": "P2",
        "use_jina_only": True
    },
    {
        "name": "NEC",  # 79
        "url": "https://www.nec.com/",
        "list_selector": ".news-list .news-item, .news-item, .list-item li, article, li",
        "title_selector": "h3, h2, h1, .title, a, .news-title",
        "link_selector": "a[href*='news'], a[href*='press'], a[href], a",
        "date_selector": ".date, .time, .publish-date, time, .news-date",
        "base_url": "https://www.nec.com",
        "priority": "P2",
        "use_jina_only": True
    },
    {
        "name": "富士通",  # 80
        "url": "https://www.fujitsu.com/",
        "list_selector": ".news-list .news-item, .news-item, .list-item li, article, li",
        "title_selector": "h3, h2, h1, .title, a, .news-title",
        "link_selector": "a[href*='news'], a[href*='press'], a[href], a",
        "date_selector": ".date, .time, .publish-date, time, .news-date",
        "base_url": "https://www.fujitsu.com",
        "priority": "P2",
        "use_jina_only": True
    },
    {
        "name": "移远通信",  # 81
        "url": "https://www.quectel.com/",
        "list_selector": ".news-list .news-item, .news-item, .list-item li, article, li",
        "title_selector": "h3, h2, h1, .title, a, .news-title",
        "link_selector": "a[href*='news'], a[href*='press'], a[href], a",
        "date_selector": ".date, .time, .publish-date, time, .news-date",
        "base_url": "https://www.quectel.com",
        "priority": "P2",
        "use_jina_only": True
    },
    {
        "name": "广和通",  # 82
        "url": "https://www.fibocom.com/",
        "list_selector": ".news-list .news-item, .news-item, .list-item li, article, li",
        "title_selector": "h3, h2, h1, .title, a, .news-title",
        "link_selector": "a[href*='news'], a[href*='press'], a[href], a",
        "date_selector": ".date, .time, .publish-date, time, .news-date",
        "base_url": "https://www.fibocom.com",
        "priority": "P2",
        "use_jina_only": True
    },
    {
        "name": "日海智能",  # 83
        "url": "https://www.suntek.com.cn/",
        "list_selector": ".news-list .news-item, .news-item, .list-item li, article, li",
        "title_selector": "h3, h2, h1, .title, a, .news-title",
        "link_selector": "a[href*='news'], a[href*='press'], a[href], a",
        "date_selector": ".date, .time, .publish-date, time, .news-date",
        "base_url": "https://www.suntek.com.cn",
        "priority": "P2",
        "use_jina_only": True
    },
    {
        "name": "美格智能",  # 84
        "url": "https://www.meigsmart.com/",
        "list_selector": ".news-list .news-item, .news-item, .list-item li, article, li",
        "title_selector": "h3, h2, h1, .title, a, .news-title",
        "link_selector": "a[href*='news'], a[href*='press'], a[href], a",
        "date_selector": ".date, .time, .publish-date, time, .news-date",
        "base_url": "https://www.meigsmart.com",
        "priority": "P2",
        "use_jina_only": True
    },
    {
        "name": "有方科技",  # 85
        "url": "https://www.thingclo.com/",
        "list_selector": ".news-list .news-item, .news-item, .list-item li, article, li",
        "title_selector": "h3, h2, h1, .title, a, .news-title",
        "link_selector": "a[href*='news'], a[href*='press'], a[href], a",
        "date_selector": ".date, .time, .publish-date, time, .news-date",
        "base_url": "https://www.thingclo.com",
        "priority": "P2",
        "use_jina_only": True
    },
    {
        "name": "高新兴",  # 86
        "url": "https://www.gosuncn.com/",
        "list_selector": ".news-list .news-item, .news-item, .list-item li, article, li",
        "title_selector": "h3, h2, h1, .title, a, .news-title",
        "link_selector": "a[href*='news'], a[href*='press'], a[href], a",
        "date_selector": ".date, .time, .publish-date, time, .news-date",
        "base_url": "https://www.gosuncn.com",
        "priority": "P2",
        "use_jina_only": True
    },
    {
        "name": "芯讯通",  # 87
        "url": "https://www.simcom.com/",
        "list_selector": ".news-list .news-item, .news-item, .list-item li, article, li",
        "title_selector": "h3, h2, h1, .title, a, .news-title",
        "link_selector": "a[href*='news'], a[href*='press'], a[href], a",
        "date_selector": ".date, .time, .publish-date, time, .news-date",
        "base_url": "https://www.simcom.com",
        "priority": "P2",
        "use_jina_only": True
    },
    {
        "name": "富士康",  # 88
        "url": "https://www.foxconn.com/",
        "list_selector": ".news-list .news-item, .news-item, .list-item li, article, li",
        "title_selector": "h3, h2, h1, .title, a, .news-title",
        "link_selector": "a[href*='news'], a[href*='press'], a[href], a",
        "date_selector": ".date, .time, .publish-date, time, .news-date",
        "base_url": "https://www.foxconn.com",
        "priority": "P2",
        "use_jina_only": True
    },
    {
        "name": "闻泰科技",  # 89
        "url": "https://www.wingtech.com/",
        "list_selector": ".news-list .news-item, .news-item, .list-item li, article, li",
        "title_selector": "h3, h2, h1, .title, a, .news-title",
        "link_selector": "a[href*='news'], a[href*='press'], a[href], a",
        "date_selector": ".date, .time, .publish-date, time, .news-date",
        "base_url": "https://www.wingtech.com",
        "priority": "P2",
        "use_jina_only": True
    },
    {
        "name": "华勤技术",  # 90
        "url": "https://www.huaqin.com/",
        "list_selector": ".news-list .news-item, .news-item, .list-item li, article, li",
        "title_selector": "h3, h2, h1, .title, a, .news-title",
        "link_selector": "a[href*='news'], a[href*='press'], a[href], a",
        "date_selector": ".date, .time, .publish-date, time, .news-date",
        "base_url": "https://www.huaqin.com",
        "priority": "P2",
        "use_jina_only": True
    },
    {
        "name": "龙旗科技",  # 91
        "url": "https://www.longqi.com/",
        "list_selector": ".news-list .news-item, .news-item, .list-item li, article, li",
        "title_selector": "h3, h2, h1, .title, a, .news-title",
        "link_selector": "a[href*='news'], a[href*='press'], a[href], a",
        "date_selector": ".date, .time, .publish-date, time, .news-date",
        "base_url": "https://www.longqi.com",
        "priority": "P2",
        "use_jina_only": True
    },
    {
        "name": "Sierra Wireless",  # 92
        "url": "https://www.sierrawireless.com/",
        "list_selector": ".news-list .news-item, .news-item, .list-item li, article, li",
        "title_selector": "h3, h2, h1, .title, a, .news-title",
        "link_selector": "a[href*='news'], a[href*='press'], a[href], a",
        "date_selector": ".date, .time, .publish-date, time, .news-date",
        "base_url": "https://www.sierrawireless.com",
        "priority": "P2",
        "use_jina_only": True
    },
    {
        "name": "泰利特",  # 93
        "url": "https://www.telit.com/",
        "list_selector": ".news-list .news-item, .news-item, .list-item li, article, li",
        "title_selector": "h3, h2, h1, .title, a, .news-title",
        "link_selector": "a[href*='news'], a[href*='press'], a[href], a",
        "date_selector": ".date, .time, .publish-date, time, .news-date",
        "base_url": "https://www.telit.com",
        "priority": "P2",
        "use_jina_only": True
    },
    {
        "name": "u-blox",  # 94
        "url": "https://www.u-blox.com/",
        "list_selector": ".news-list .news-item, .news-item, .list-item li, article, li",
        "title_selector": "h3, h2, h1, .title, a, .news-title",
        "link_selector": "a[href*='news'], a[href*='press'], a[href], a",
        "date_selector": ".date, .time, .publish-date, time, .news-date",
        "base_url": "https://www.u-blox.com",
        "priority": "P2",
        "use_jina_only": True
    },
    {
        "name": "Apple",  # 95
        "url": "https://www.apple.com/",
        "list_selector": ".news-list .news-item, .news-item, .list-item li, article, li",
        "title_selector": "h3, h2, h1, .title, a, .news-title",
        "link_selector": "a[href*='news'], a[href*='press'], a[href], a",
        "date_selector": ".date, .time, .publish-date, time, .news-date",
        "base_url": "https://www.apple.com",
        "priority": "P2",
        "use_jina_only": True
    },
    {
        "name": "三星电子",  # 96
        "url": "https://www.samsung.com/",
        "list_selector": ".news-list .news-item, .news-item, .list-item li, article, li",
        "title_selector": "h3, h2, h1, .title, a, .news-title",
        "link_selector": "a[href*='news'], a[href*='press'], a[href], a",
        "date_selector": ".date, .time, .publish-date, time, .news-date",
        "base_url": "https://www.samsung.com",
        "priority": "P2",
        "use_jina_only": True
    },
    {
        "name": "中国广电",  # 97
        "url": "https://www.cbn.cn/",
        "list_selector": ".news-list .news-item, .news-item, .list-item li, article, li",
        "title_selector": "h3, h2, h1, .title, a, .news-title",
        "link_selector": "a[href*='news'], a[href*='press'], a[href], a",
        "date_selector": ".date, .time, .publish-date, time, .news-date",
        "base_url": "https://www.cbn.cn",
        "priority": "P0",
        "use_jina_only": False
    },
    {
        "name": "中国通信服务",  # 98
        "url": "https://www.chinaccs.com.hk/",
        "list_selector": ".news-list .news-item, .news-item, .list-item li, article, li",
        "title_selector": "h3, h2, h1, .title, a, .news-title",
        "link_selector": "a[href*='news'], a[href*='press'], a[href], a",
        "date_selector": ".date, .time, .publish-date, time, .news-date",
        "base_url": "https://www.chinaccs.com.hk",
        "priority": "P0",
        "use_jina_only": False
    },
    {
        "name": "Verizon",  # 99
        "url": "https://www.verizon.com/",
        "list_selector": ".news-list .news-item, .news-item, .list-item li, article, li",
        "title_selector": "h3, h2, h1, .title, a, .news-title",
        "link_selector": "a[href*='news'], a[href*='press'], a[href], a",
        "date_selector": ".date, .time, .publish-date, time, .news-date",
        "base_url": "https://www.verizon.com",
        "priority": "P0",
        "use_jina_only": False
    },
    {
        "name": "AT&T",  # 100
        "url": "https://www.att.com/",
        "list_selector": ".news-list .news-item, .news-item, .list-item li, article, li",
        "title_selector": "h3, h2, h1, .title, a, .news-title",
        "link_selector": "a[href*='news'], a[href*='press'], a[href], a",
        "date_selector": ".date, .time, .publish-date, time, .news-date",
        "base_url": "https://www.att.com",
        "priority": "P0",
        "use_jina_only": False
    },
    {
        "name": "T-Mobile",  # 101
        "url": "https://www.t-mobile.com/",
        "list_selector": ".news-list .news-item, .news-item, .list-item li, article, li",
        "title_selector": "h3, h2, h1, .title, a, .news-title",
        "link_selector": "a[href*='news'], a[href*='press'], a[href], a",
        "date_selector": ".date, .time, .publish-date, time, .news-date",
        "base_url": "https://www.t-mobile.com",
        "priority": "P0",
        "use_jina_only": False
    },
    {
        "name": "德国电信",  # 102
        "url": "https://www.telekom.com/",
        "list_selector": ".news-list .news-item, .news-item, .list-item li, article, li",
        "title_selector": "h3, h2, h1, .title, a, .news-title",
        "link_selector": "a[href*='news'], a[href*='press'], a[href], a",
        "date_selector": ".date, .time, .publish-date, time, .news-date",
        "base_url": "https://www.telekom.com",
        "priority": "P0",
        "use_jina_only": False
    },
    {
        "name": "沃达丰",  # 103
        "url": "https://www.vodafone.com/",
        "list_selector": ".news-list .news-item, .news-item, .list-item li, article, li",
        "title_selector": "h3, h2, h1, .title, a, .news-title",
        "link_selector": "a[href*='news'], a[href*='press'], a[href], a",
        "date_selector": ".date, .time, .publish-date, time, .news-date",
        "base_url": "https://www.vodafone.com",
        "priority": "P0",
        "use_jina_only": False
    },
    {
        "name": "Orange",  # 104
        "url": "https://www.orange.com/",
        "list_selector": ".news-list .news-item, .news-item, .list-item li, article, li",
        "title_selector": "h3, h2, h1, .title, a, .news-title",
        "link_selector": "a[href*='news'], a[href*='press'], a[href], a",
        "date_selector": ".date, .time, .publish-date, time, .news-date",
        "base_url": "https://www.orange.com",
        "priority": "P0",
        "use_jina_only": False
    },
    {
        "name": "NTT DoCoMo",  # 105
        "url": "https://www.nttdocomo.co.jp/",
        "list_selector": ".news-list .news-item, .news-item, .list-item li, article, li",
        "title_selector": "h3, h2, h1, .title, a, .news-title",
        "link_selector": "a[href*='news'], a[href*='press'], a[href], a",
        "date_selector": ".date, .time, .publish-date, time, .news-date",
        "base_url": "https://www.nttdocomo.co.jp",
        "priority": "P0",
        "use_jina_only": False
    },
    {
        "name": "软银",  # 106
        "url": "https://www.softbank.jp/",
        "list_selector": ".news-list .news-item, .news-item, .list-item li, article, li",
        "title_selector": "h3, h2, h1, .title, a, .news-title",
        "link_selector": "a[href*='news'], a[href*='press'], a[href], a",
        "date_selector": ".date, .time, .publish-date, time, .news-date",
        "base_url": "https://www.softbank.jp",
        "priority": "P0",
        "use_jina_only": False
    },
    {
        "name": "SK电讯",  # 107
        "url": "https://www.sktelecom.com/",
        "list_selector": ".news-list .news-item, .news-item, .list-item li, article, li",
        "title_selector": "h3, h2, h1, .title, a, .news-title",
        "link_selector": "a[href*='news'], a[href*='press'], a[href], a",
        "date_selector": ".date, .time, .publish-date, time, .news-date",
        "base_url": "https://www.sktelecom.com",
        "priority": "P0",
        "use_jina_only": False
    },
]
