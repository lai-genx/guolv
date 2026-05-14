#!/usr/bin/env python3
"""
从企业清单生成Web采集器配置
"""

# 从企业清单中提取的所有企业和网址
COMPANIES_FROM_CHECKLIST = [
    # ===== 中游：主设备商（优先级最高）=====
    ("华为", "https://www.huawei.com"),
    ("中兴通讯", "https://www.zte.com.cn"),
    ("爱立信", "https://www.ericsson.com"),
    ("诺基亚", "https://www.nokia.com"),
    ("思科", "https://www.cisco.com"),
    ("烽火通信", "https://www.fiberhome.com"),
    ("新华三", "https://www.h3c.com"),
    ("锐捷网络", "https://www.ruijie.com.cn"),
    ("Ciena", "https://www.ciena.com"),
    ("Infinera", "https://www.infinera.com"),
    ("Juniper", "https://www.juniper.net"),
    ("Arista Networks", "https://www.arista.com"),
    ("三星电子", "https://www.samsung.com"),
    ("NEC", "https://www.nec.com"),
    ("富士通", "https://www.fujitsu.com"),
    ("Mavenir", "https://www.mavenir.com"),

    # ===== 上游：芯片与半导体 =====
    ("高通", "https://www.qualcomm.com"),
    ("联发科", "https://www.mediatek.com"),
    ("华为海思", "https://www.hisilicon.com"),
    ("紫光展锐", "https://www.unisoc.com"),
    ("三星LSI", "https://www.samsung.com/semiconductor"),
    ("英特尔", "https://www.intel.com"),
    ("思佳讯", "https://www.skyworksinc.com"),
    ("科沃", "https://www.qorvo.com"),
    ("博通", "https://www.broadcom.com"),
    ("Coherent", "https://www.coherent.com"),
    ("Lumentum", "https://www.lumentum.com"),
    ("光迅科技", "https://www.accelink.com"),

    # ===== 上游：光通信 =====
    ("中际旭创", "https://www.innolight.com"),
    ("新易盛", "https://www.eoptolink.com"),
    ("华工正源", "https://www.hggenuine.com"),
    ("海信宽带", "https://www.hisensebroadband.com"),
    ("索尔思光电", "https://www.sourcephotonics.com"),
    ("天孚通信", "https://www.tfc.com.cn"),

    # ===== 上游：PCB制造 =====
    ("鹏鼎控股", "https://www.avaryholding.com"),
    ("东山精密", "https://www.sz-dsbj.com"),
    ("深南电路", "https://www.scc.com.cn"),
    ("沪电股份", "https://www.wuspca.com"),
    ("景旺电子", "https://www.kinwong.com"),
    ("胜宏科技", "https://www.shengyi-pcb.com"),
    ("欣兴电子", "https://www.unimicron.com"),

    # ===== 上游：连接器 =====
    ("泰科电子", "https://www.te.com"),
    ("安费诺", "https://www.amphenol.com"),
    ("莫仕", "https://www.molex.com"),
    ("中航光电", "https://www.jonhon.cn"),
    ("立讯精密", "https://www.luxshare-ict.com"),

    # ===== 上游：天线与射频 =====
    ("康普通讯", "https://www.commscope.com"),
    ("凯士林", "https://www.kathrein.com"),
    ("通宇通讯", "https://www.tongyu.com.cn"),
    ("京信通信", "https://www.comba-telecom.com"),
    ("大富科技", "https://www.tatfook.com"),

    # ===== 中游：光通信与固网接入 =====
    ("Calix", "https://www.calix.com"),
    ("ADTRAN", "https://www.adtran.com"),

    # ===== 中游：物联网模组 =====
    ("移远通信", "https://www.quectel.com"),
    ("广和通", "https://www.fibocom.com"),
    ("日海智能", "https://www.sunseaiot.com"),
    ("美格智能", "https://www.meigsmart.com"),
    ("有方科技", "https://www.neoway.com"),
    ("Sierra Wireless", "https://www.sierrawireless.com"),
    ("u-blox", "https://www.u-blox.com"),

    # ===== 中游：ODM/代工 =====
    ("富士康", "https://www.foxconn.com"),
    ("闻泰科技", "https://www.wingtech.com"),

    # ===== 下游：运营商 =====
    ("中国移动", "https://www.10086.cn"),
    ("中国电信", "https://www.chinatelecom.com.cn"),
    ("中国联通", "https://www.10010.com"),
    ("中国广电", "https://www.cbn.cn"),
    ("Verizon", "https://www.verizon.com"),
    ("AT&T", "https://www.att.com"),
    ("T-Mobile", "https://www.t-mobile.com"),
    ("德国电信", "https://www.telekom.com"),
    ("沃达丰", "https://www.vodafone.com"),
    ("法国电信", "https://www.orange.com"),

    # ===== 下游：基础设施服务 =====
    ("中国铁塔", "https://www.china-tower.com"),
    ("中国通信服务", "https://www.chinacomservice.com.cn"),
    ("润建股份", "https://www.runjian.com.cn"),
]

def generate_web_sites_config():
    """生成Web采集器的DEFAULT_SITES配置"""
    sites = []

    for company_name, base_url in COMPANIES_FROM_CHECKLIST:
        # 构造新闻页面URL（常见模式）
        news_urls = [
            f"{base_url}/news",
            f"{base_url}/cn/news",
            f"{base_url}/about/news",
            f"{base_url}/china/about/news",
            f"{base_url}/zh_cn/news",
            f"{base_url}/newsroom",
            f"{base_url.rstrip('/')}"  # 降级到首页
        ]

        # 选择第一个有效的URL（在实际运行时会尝试）
        news_url = news_urls[0]

        site_config = {
            "name": company_name,
            "url": news_url,
            "list_selector": ".news-list .news-item, .news-item, .list-item li, article, .content li, [class*='news']",
            "title_selector": "h3, h2, h1, .title, a.news-title, .news-link, .headline, [class*='title']",
            "link_selector": "a[href*='news'], a[href*='press'], a[href], a",
            "date_selector": ".date, .time, .publish-date, time, .pub-date, [class*='date']",
            "base_url": base_url
        }
        sites.append(site_config)

    return sites


if __name__ == "__main__":
    sites = generate_web_sites_config()

    print(f"生成了 {len(sites)} 个网站配置")
    print("\n前5个配置示例:")
    for site in sites[:5]:
        print(f"  - {site['name']}: {site['url']}")

    # 生成Python代码
    print("\n\n生成的DEFAULT_SITES配置:")
    print("DEFAULT_SITES = [")
    for site in sites:
        print(f'    {{')
        print(f'        "name": "{site["name"]}",')
        print(f'        "url": "{site["url"]}",')
        print(f'        "list_selector": "{site["list_selector"]}",')
        print(f'        "title_selector": "{site["title_selector"]}",')
        print(f'        "link_selector": "{site["link_selector"]}",')
        print(f'        "date_selector": "{site["date_selector"]}",')
        print(f'        "base_url": "{site["base_url"]}"')
        print(f'    }},')
    print("]")
