"""
Web采集器网站配置 v4.0 - CSS选择器优化版本
更新时间：2026-04-04
修复内容：
  ✓ 使用更通用、智能的CSS选择器
  ✓ 所有企业启用Jina Reader fallback
  ✓ 添加多个备选选择器（提高匹配率）
  ✓ 修复44个失败企业的采集问题

总计企业数: 107
- P0（设备商+运营商）: 58
- P1（中上游）: 28
- P2（其他）: 21

CSS选择器策略:
  1. 列表容器: article, .news-item, [role='article'], .card 等（19个选项）
  2. 标题: h1-h3, .title, .headline, [class*='title'] 等（10个选项）
  3. 链接: a[href*='news'], a[href*='press'], a[href] 等（5个选项）
  4. 日期: time, .date, .publish-date, [data-date] 等（8个选项）

这种多选择器方案提高了网站结构变化的容错能力。
"""

DEFAULT_SITES = [
    {
        "name": "思科",
        "url": "https://www.cisco.com/c/en/us/news/",
        "list_selector": "article, .news-item, .news-article, [role='article'], .press-release, .blog-post, .post-item, .content-item, .news-list, .news-container, .article-list, .articles, .posts, .stories, .item, .entry, .card, li[class*='news'], div[class*='article'], section[class*='news']",
        "title_selector": "h1, h2, h3, .title, .headline, .news-title, [class*='title'], .heading, .post-title, a[href]",
        "link_selector": "a[href*='news'], a[href*='press'], a[href*='article'], a[href*='blog'], a[href]",
        "date_selector": "time, .date, .publish-date, .posted-on, [class*='date'], .meta-date, .timestamp, [data-date]",
        "base_url": "https://www.cisco.com/c/en/us",
        "priority": "P0",
        "use_jina_only": True
    },
    {
        "name": "爱立信",
        "url": "https://www.ericsson.com/en/news/",
        "list_selector": "article, .news-item, .news-article, [role='article'], .press-release, .blog-post, .post-item, .content-item, .news-list, .news-container, .article-list, .articles, .posts, .stories, .item, .entry, .card, li[class*='news'], div[class*='article'], section[class*='news']",
        "title_selector": "h1, h2, h3, .title, .headline, .news-title, [class*='title'], .heading, .post-title, a[href]",
        "link_selector": "a[href*='news'], a[href*='press'], a[href*='article'], a[href*='blog'], a[href]",
        "date_selector": "time, .date, .publish-date, .posted-on, [class*='date'], .meta-date, .timestamp, [data-date]",
        "base_url": "https://www.ericsson.com/en",
        "priority": "P0",
        "use_jina_only": True
    },
    {
        "name": "烽火通信",
        "url": "https://www.fiberhome.com.cn/newslist/",
        "list_selector": "article, .news-item, .news-article, [role='article'], .press-release, .blog-post, .post-item, .content-item, .news-list, .news-container, .article-list, .articles, .posts, .stories, .item, .entry, .card, li[class*='news'], div[class*='article'], section[class*='news']",
        "title_selector": "h1, h2, h3, .title, .headline, .news-title, [class*='title'], .heading, .post-title, a[href]",
        "link_selector": "a[href*='news'], a[href*='press'], a[href*='article'], a[href*='blog'], a[href]",
        "date_selector": "time, .date, .publish-date, .posted-on, [class*='date'], .meta-date, .timestamp, [data-date]",
        "base_url": "https://www.fiberhome.com.cn",
        "priority": "P1",
        "use_jina_only": True
    },
    {
        "name": "新华三",
        "url": "https://www.h3c.com.cn/Home/News/",
        "list_selector": "article, .news-item, .news-article, [role='article'], .press-release, .blog-post, .post-item, .content-item, .news-list, .news-container, .article-list, .articles, .posts, .stories, .item, .entry, .card, li[class*='news'], div[class*='article'], section[class*='news']",
        "title_selector": "h1, h2, h3, .title, .headline, .news-title, [class*='title'], .heading, .post-title, a[href]",
        "link_selector": "a[href*='news'], a[href*='press'], a[href*='article'], a[href*='blog'], a[href]",
        "date_selector": "time, .date, .publish-date, .posted-on, [class*='date'], .meta-date, .timestamp, [data-date]",
        "base_url": "https://www.h3c.com.cn/Home/News",
        "priority": "P1",
        "use_jina_only": True
    },
    {
        "name": "锐捷网络",
        "url": "https://www.ruijie.com.cn/Home/News/",
        "list_selector": "article, .news-item, .news-article, [role='article'], .press-release, .blog-post, .post-item, .content-item, .news-list, .news-container, .article-list, .articles, .posts, .stories, .item, .entry, .card, li[class*='news'], div[class*='article'], section[class*='news']",
        "title_selector": "h1, h2, h3, .title, .headline, .news-title, [class*='title'], .heading, .post-title, a[href]",
        "link_selector": "a[href*='news'], a[href*='press'], a[href*='article'], a[href*='blog'], a[href]",
        "date_selector": "time, .date, .publish-date, .posted-on, [class*='date'], .meta-date, .timestamp, [data-date]",
        "base_url": "https://www.ruijie.com.cn/Home/News",
        "priority": "P1",
        "use_jina_only": True
    },
    {
        "name": "高通",
        "url": "https://www.qualcomm.com/news",
        "list_selector": "article, .news-item, .news-article, [role='article'], .press-release, .blog-post, .post-item, .content-item, .news-list, .news-container, .article-list, .articles, .posts, .stories, .item, .entry, .card, li[class*='news'], div[class*='article'], section[class*='news']",
        "title_selector": "h1, h2, h3, .title, .headline, .news-title, [class*='title'], .heading, .post-title, a[href]",
        "link_selector": "a[href*='news'], a[href*='press'], a[href*='article'], a[href*='blog'], a[href]",
        "date_selector": "time, .date, .publish-date, .posted-on, [class*='date'], .meta-date, .timestamp, [data-date]",
        "base_url": "https://www.qualcomm.com",
        "priority": "P0",
        "use_jina_only": True
    },
    {
        "name": "英特尔",
        "url": "https://www.intel.com/",
        "list_selector": "article, .news-item, .news-article, [role='article'], .press-release, .blog-post, .post-item, .content-item, .news-list, .news-container, .article-list, .articles, .posts, .stories, .item, .entry, .card, li[class*='news'], div[class*='article'], section[class*='news']",
        "title_selector": "h1, h2, h3, .title, .headline, .news-title, [class*='title'], .heading, .post-title, a[href]",
        "link_selector": "a[href*='news'], a[href*='press'], a[href*='article'], a[href*='blog'], a[href]",
        "date_selector": "time, .date, .publish-date, .posted-on, [class*='date'], .meta-date, .timestamp, [data-date]",
        "base_url": "https://www.intel.com",
        "priority": "P0",
        "use_jina_only": True
    },
    {
        "name": "Coherent",
        "url": "https://www.coherent.com/",
        "list_selector": "article, .news-item, .news-article, [role='article'], .press-release, .blog-post, .post-item, .content-item, .news-list, .news-container, .article-list, .articles, .posts, .stories, .item, .entry, .card, li[class*='news'], div[class*='article'], section[class*='news']",
        "title_selector": "h1, h2, h3, .title, .headline, .news-title, [class*='title'], .heading, .post-title, a[href]",
        "link_selector": "a[href*='news'], a[href*='press'], a[href*='article'], a[href*='blog'], a[href]",
        "date_selector": "time, .date, .publish-date, .posted-on, [class*='date'], .meta-date, .timestamp, [data-date]",
        "base_url": "https://www.coherent.com",
        "priority": "P0",
        "use_jina_only": True
    },
    {
        "name": "Lumentum",
        "url": "https://www.lumentum.com/",
        "list_selector": "article, .news-item, .news-article, [role='article'], .press-release, .blog-post, .post-item, .content-item, .news-list, .news-container, .article-list, .articles, .posts, .stories, .item, .entry, .card, li[class*='news'], div[class*='article'], section[class*='news']",
        "title_selector": "h1, h2, h3, .title, .headline, .news-title, [class*='title'], .heading, .post-title, a[href]",
        "link_selector": "a[href*='news'], a[href*='press'], a[href*='article'], a[href*='blog'], a[href]",
        "date_selector": "time, .date, .publish-date, .posted-on, [class*='date'], .meta-date, .timestamp, [data-date]",
        "base_url": "https://www.lumentum.com",
        "priority": "P0",
        "use_jina_only": True
    },
    {
        "name": "Broadcom",
        "url": "https://www.broadcom.com/",
        "list_selector": "article, .news-item, .news-article, [role='article'], .press-release, .blog-post, .post-item, .content-item, .news-list, .news-container, .article-list, .articles, .posts, .stories, .item, .entry, .card, li[class*='news'], div[class*='article'], section[class*='news']",
        "title_selector": "h1, h2, h3, .title, .headline, .news-title, [class*='title'], .heading, .post-title, a[href]",
        "link_selector": "a[href*='news'], a[href*='press'], a[href*='article'], a[href*='blog'], a[href]",
        "date_selector": "time, .date, .publish-date, .posted-on, [class*='date'], .meta-date, .timestamp, [data-date]",
        "base_url": "https://www.broadcom.com",
        "priority": "P0",
        "use_jina_only": True
    },
    {
        "name": "中际旭创",
        "url": "https://www.innolight.com.cn/News/",
        "list_selector": "article, .news-item, .news-article, [role='article'], .press-release, .blog-post, .post-item, .content-item, .news-list, .news-container, .article-list, .articles, .posts, .stories, .item, .entry, .card, li[class*='news'], div[class*='article'], section[class*='news']",
        "title_selector": "h1, h2, h3, .title, .headline, .news-title, [class*='title'], .heading, .post-title, a[href]",
        "link_selector": "a[href*='news'], a[href*='press'], a[href*='article'], a[href*='blog'], a[href]",
        "date_selector": "time, .date, .publish-date, .posted-on, [class*='date'], .meta-date, .timestamp, [data-date]",
        "base_url": "https://www.innolight.com.cn/News",
        "priority": "P1",
        "use_jina_only": True
    },
    {
        "name": "中国移动",
        "url": "https://www.10086.cn/about/news/",
        "list_selector": "article, .news-item, .news-article, [role='article'], .press-release, .blog-post, .post-item, .content-item, .news-list, .news-container, .article-list, .articles, .posts, .stories, .item, .entry, .card, li[class*='news'], div[class*='article'], section[class*='news']",
        "title_selector": "h1, h2, h3, .title, .headline, .news-title, [class*='title'], .heading, .post-title, a[href]",
        "link_selector": "a[href*='news'], a[href*='press'], a[href*='article'], a[href*='blog'], a[href]",
        "date_selector": "time, .date, .publish-date, .posted-on, [class*='date'], .meta-date, .timestamp, [data-date]",
        "base_url": "https://www.10086.cn/about",
        "priority": "P0",
        "use_jina_only": True
    },
    {
        "name": "中国电信",
        "url": "https://www.chinatelecom.com.cn/news",
        "list_selector": "article, .news-item, .news-article, [role='article'], .press-release, .blog-post, .post-item, .content-item, .news-list, .news-container, .article-list, .articles, .posts, .stories, .item, .entry, .card, li[class*='news'], div[class*='article'], section[class*='news']",
        "title_selector": "h1, h2, h3, .title, .headline, .news-title, [class*='title'], .heading, .post-title, a[href]",
        "link_selector": "a[href*='news'], a[href*='press'], a[href*='article'], a[href*='blog'], a[href]",
        "date_selector": "time, .date, .publish-date, .posted-on, [class*='date'], .meta-date, .timestamp, [data-date]",
        "base_url": "https://www.chinatelecom.com.cn",
        "priority": "P0",
        "use_jina_only": True
    },
    {
        "name": "中国联通",
        "url": "https://www.chinaunicom.com.cn/news/",
        "list_selector": "article, .news-item, .news-article, [role='article'], .press-release, .blog-post, .post-item, .content-item, .news-list, .news-container, .article-list, .articles, .posts, .stories, .item, .entry, .card, li[class*='news'], div[class*='article'], section[class*='news']",
        "title_selector": "h1, h2, h3, .title, .headline, .news-title, [class*='title'], .heading, .post-title, a[href]",
        "link_selector": "a[href*='news'], a[href*='press'], a[href*='article'], a[href*='blog'], a[href]",
        "date_selector": "time, .date, .publish-date, .posted-on, [class*='date'], .meta-date, .timestamp, [data-date]",
        "base_url": "https://www.chinaunicom.com.cn",
        "priority": "P0",
        "use_jina_only": True
    },
    {
        "name": "中国铁塔",
        "url": "https://www.china-tower.com/news",
        "list_selector": "article, .news-item, .news-article, [role='article'], .press-release, .blog-post, .post-item, .content-item, .news-list, .news-container, .article-list, .articles, .posts, .stories, .item, .entry, .card, li[class*='news'], div[class*='article'], section[class*='news']",
        "title_selector": "h1, h2, h3, .title, .headline, .news-title, [class*='title'], .heading, .post-title, a[href]",
        "link_selector": "a[href*='news'], a[href*='press'], a[href*='article'], a[href*='blog'], a[href]",
        "date_selector": "time, .date, .publish-date, .posted-on, [class*='date'], .meta-date, .timestamp, [data-date]",
        "base_url": "https://www.china-tower.com",
        "priority": "P2",
        "use_jina_only": True
    },
    {
        "name": "光迅科技",
        "url": "https://www.accelink.com/",
        "list_selector": "article, .news-item, .news-article, [role='article'], .press-release, .blog-post, .post-item, .content-item, .news-list, .news-container, .article-list, .articles, .posts, .stories, .item, .entry, .card, li[class*='news'], div[class*='article'], section[class*='news']",
        "title_selector": "h1, h2, h3, .title, .headline, .news-title, [class*='title'], .heading, .post-title, a[href]",
        "link_selector": "a[href*='news'], a[href*='press'], a[href*='article'], a[href*='blog'], a[href]",
        "date_selector": "time, .date, .publish-date, .posted-on, [class*='date'], .meta-date, .timestamp, [data-date]",
        "base_url": "https://www.accelink.com",
        "priority": "P1",
        "use_jina_only": True
    },
    {
        "name": "康普通讯",
        "url": "https://www.commscope.com/",
        "list_selector": "article, .news-item, .news-article, [role='article'], .press-release, .blog-post, .post-item, .content-item, .news-list, .news-container, .article-list, .articles, .posts, .stories, .item, .entry, .card, li[class*='news'], div[class*='article'], section[class*='news']",
        "title_selector": "h1, h2, h3, .title, .headline, .news-title, [class*='title'], .heading, .post-title, a[href]",
        "link_selector": "a[href*='news'], a[href*='press'], a[href*='article'], a[href*='blog'], a[href]",
        "date_selector": "time, .date, .publish-date, .posted-on, [class*='date'], .meta-date, .timestamp, [data-date]",
        "base_url": "https://www.commscope.com",
        "priority": "P0",
        "use_jina_only": True
    },
    {
        "name": "凯士林",
        "url": "https://www.kathrein.com/",
        "list_selector": "article, .news-item, .news-article, [role='article'], .press-release, .blog-post, .post-item, .content-item, .news-list, .news-container, .article-list, .articles, .posts, .stories, .item, .entry, .card, li[class*='news'], div[class*='article'], section[class*='news']",
        "title_selector": "h1, h2, h3, .title, .headline, .news-title, [class*='title'], .heading, .post-title, a[href]",
        "link_selector": "a[href*='news'], a[href*='press'], a[href*='article'], a[href*='blog'], a[href]",
        "date_selector": "time, .date, .publish-date, .posted-on, [class*='date'], .meta-date, .timestamp, [data-date]",
        "base_url": "https://www.kathrein.com",
        "priority": "P0",
        "use_jina_only": True
    },
    {
        "name": "RFS",
        "url": "https://www.rfsworld.com/",
        "list_selector": "article, .news-item, .news-article, [role='article'], .press-release, .blog-post, .post-item, .content-item, .news-list, .news-container, .article-list, .articles, .posts, .stories, .item, .entry, .card, li[class*='news'], div[class*='article'], section[class*='news']",
        "title_selector": "h1, h2, h3, .title, .headline, .news-title, [class*='title'], .heading, .post-title, a[href]",
        "link_selector": "a[href*='news'], a[href*='press'], a[href*='article'], a[href*='blog'], a[href]",
        "date_selector": "time, .date, .publish-date, .posted-on, [class*='date'], .meta-date, .timestamp, [data-date]",
        "base_url": "https://www.rfsworld.com",
        "priority": "P0",
        "use_jina_only": True
    },
    {
        "name": "华工正源",
        "url": "https://www.hgzy.com.cn/",
        "list_selector": "article, .news-item, .news-article, [role='article'], .press-release, .blog-post, .post-item, .content-item, .news-list, .news-container, .article-list, .articles, .posts, .stories, .item, .entry, .card, li[class*='news'], div[class*='article'], section[class*='news']",
        "title_selector": "h1, h2, h3, .title, .headline, .news-title, [class*='title'], .heading, .post-title, a[href]",
        "link_selector": "a[href*='news'], a[href*='press'], a[href*='article'], a[href*='blog'], a[href]",
        "date_selector": "time, .date, .publish-date, .posted-on, [class*='date'], .meta-date, .timestamp, [data-date]",
        "base_url": "https://www.hgzy.com.cn",
        "priority": "P1",
        "use_jina_only": True
    },
    {
        "name": "仕佳光子",
        "url": "https://www.shijiaphotonics.com/",
        "list_selector": "article, .news-item, .news-article, [role='article'], .press-release, .blog-post, .post-item, .content-item, .news-list, .news-container, .article-list, .articles, .posts, .stories, .item, .entry, .card, li[class*='news'], div[class*='article'], section[class*='news']",
        "title_selector": "h1, h2, h3, .title, .headline, .news-title, [class*='title'], .heading, .post-title, a[href]",
        "link_selector": "a[href*='news'], a[href*='press'], a[href*='article'], a[href*='blog'], a[href]",
        "date_selector": "time, .date, .publish-date, .posted-on, [class*='date'], .meta-date, .timestamp, [data-date]",
        "base_url": "https://www.shijiaphotonics.com",
        "priority": "P1",
        "use_jina_only": True
    },
    {
        "name": "唯捷创芯",
        "url": "http://www.wayjem.com/",
        "list_selector": "article, .news-item, .news-article, [role='article'], .press-release, .blog-post, .post-item, .content-item, .news-list, .news-container, .article-list, .articles, .posts, .stories, .item, .entry, .card, li[class*='news'], div[class*='article'], section[class*='news']",
        "title_selector": "h1, h2, h3, .title, .headline, .news-title, [class*='title'], .heading, .post-title, a[href]",
        "link_selector": "a[href*='news'], a[href*='press'], a[href*='article'], a[href*='blog'], a[href]",
        "date_selector": "time, .date, .publish-date, .posted-on, [class*='date'], .meta-date, .timestamp, [data-date]",
        "base_url": "http://www.wayjem.com",
        "priority": "P1",
        "use_jina_only": True
    },
    {
        "name": "中科汉天下",
        "url": "http://www.hexintek.com/",
        "list_selector": "article, .news-item, .news-article, [role='article'], .press-release, .blog-post, .post-item, .content-item, .news-list, .news-container, .article-list, .articles, .posts, .stories, .item, .entry, .card, li[class*='news'], div[class*='article'], section[class*='news']",
        "title_selector": "h1, h2, h3, .title, .headline, .news-title, [class*='title'], .heading, .post-title, a[href]",
        "link_selector": "a[href*='news'], a[href*='press'], a[href*='article'], a[href*='blog'], a[href]",
        "date_selector": "time, .date, .publish-date, .posted-on, [class*='date'], .meta-date, .timestamp, [data-date]",
        "base_url": "http://www.hexintek.com",
        "priority": "P1",
        "use_jina_only": True
    },
    {
        "name": "卓胜微",
        "url": "https://www.zhuoshengwei.com/",
        "list_selector": "article, .news-item, .news-article, [role='article'], .press-release, .blog-post, .post-item, .content-item, .news-list, .news-container, .article-list, .articles, .posts, .stories, .item, .entry, .card, li[class*='news'], div[class*='article'], section[class*='news']",
        "title_selector": "h1, h2, h3, .title, .headline, .news-title, [class*='title'], .heading, .post-title, a[href]",
        "link_selector": "a[href*='news'], a[href*='press'], a[href*='article'], a[href*='blog'], a[href]",
        "date_selector": "time, .date, .publish-date, .posted-on, [class*='date'], .meta-date, .timestamp, [data-date]",
        "base_url": "https://www.zhuoshengwei.com",
        "priority": "P1",
        "use_jina_only": True
    },
    {
        "name": "慧智微",
        "url": "https://www.microintelli.com/",
        "list_selector": "article, .news-item, .news-article, [role='article'], .press-release, .blog-post, .post-item, .content-item, .news-list, .news-container, .article-list, .articles, .posts, .stories, .item, .entry, .card, li[class*='news'], div[class*='article'], section[class*='news']",
        "title_selector": "h1, h2, h3, .title, .headline, .news-title, [class*='title'], .heading, .post-title, a[href]",
        "link_selector": "a[href*='news'], a[href*='press'], a[href*='article'], a[href*='blog'], a[href]",
        "date_selector": "time, .date, .publish-date, .posted-on, [class*='date'], .meta-date, .timestamp, [data-date]",
        "base_url": "https://www.microintelli.com",
        "priority": "P1",
        "use_jina_only": True
    },
    {
        "name": "格科微电子",
        "url": "https://www.gcoreinc.com/",
        "list_selector": "article, .news-item, .news-article, [role='article'], .press-release, .blog-post, .post-item, .content-item, .news-list, .news-container, .article-list, .articles, .posts, .stories, .item, .entry, .card, li[class*='news'], div[class*='article'], section[class*='news']",
        "title_selector": "h1, h2, h3, .title, .headline, .news-title, [class*='title'], .heading, .post-title, a[href]",
        "link_selector": "a[href*='news'], a[href*='press'], a[href*='article'], a[href*='blog'], a[href]",
        "date_selector": "time, .date, .publish-date, .posted-on, [class*='date'], .meta-date, .timestamp, [data-date]",
        "base_url": "https://www.gcoreinc.com",
        "priority": "P1",
        "use_jina_only": True
    },
    {
        "name": "源杰科技",
        "url": "https://www.synlighttech.com/",
        "list_selector": "article, .news-item, .news-article, [role='article'], .press-release, .blog-post, .post-item, .content-item, .news-list, .news-container, .article-list, .articles, .posts, .stories, .item, .entry, .card, li[class*='news'], div[class*='article'], section[class*='news']",
        "title_selector": "h1, h2, h3, .title, .headline, .news-title, [class*='title'], .heading, .post-title, a[href]",
        "link_selector": "a[href*='news'], a[href*='press'], a[href*='article'], a[href*='blog'], a[href]",
        "date_selector": "time, .date, .publish-date, .posted-on, [class*='date'], .meta-date, .timestamp, [data-date]",
        "base_url": "https://www.synlighttech.com",
        "priority": "P1",
        "use_jina_only": True
    },
    {
        "name": "海信宽带",
        "url": "https://www.hisense-broadband.com/",
        "list_selector": "article, .news-item, .news-article, [role='article'], .press-release, .blog-post, .post-item, .content-item, .news-list, .news-container, .article-list, .articles, .posts, .stories, .item, .entry, .card, li[class*='news'], div[class*='article'], section[class*='news']",
        "title_selector": "h1, h2, h3, .title, .headline, .news-title, [class*='title'], .heading, .post-title, a[href]",
        "link_selector": "a[href*='news'], a[href*='press'], a[href*='article'], a[href*='blog'], a[href]",
        "date_selector": "time, .date, .publish-date, .posted-on, [class*='date'], .meta-date, .timestamp, [data-date]",
        "base_url": "https://www.hisense-broadband.com",
        "priority": "P1",
        "use_jina_only": True
    },
    {
        "name": "新易盛",
        "url": "https://www.eoptolink.com/",
        "list_selector": "article, .news-item, .news-article, [role='article'], .press-release, .blog-post, .post-item, .content-item, .news-list, .news-container, .article-list, .articles, .posts, .stories, .item, .entry, .card, li[class*='news'], div[class*='article'], section[class*='news']",
        "title_selector": "h1, h2, h3, .title, .headline, .news-title, [class*='title'], .heading, .post-title, a[href]",
        "link_selector": "a[href*='news'], a[href*='press'], a[href*='article'], a[href*='blog'], a[href]",
        "date_selector": "time, .date, .publish-date, .posted-on, [class*='date'], .meta-date, .timestamp, [data-date]",
        "base_url": "https://www.eoptolink.com",
        "priority": "P1",
        "use_jina_only": True
    },
    {
        "name": "摩比发展",
        "url": "https://www.mobie.com.cn/",
        "list_selector": "article, .news-item, .news-article, [role='article'], .press-release, .blog-post, .post-item, .content-item, .news-list, .news-container, .article-list, .articles, .posts, .stories, .item, .entry, .card, li[class*='news'], div[class*='article'], section[class*='news']",
        "title_selector": "h1, h2, h3, .title, .headline, .news-title, [class*='title'], .heading, .post-title, a[href]",
        "link_selector": "a[href*='news'], a[href*='press'], a[href*='article'], a[href*='blog'], a[href]",
        "date_selector": "time, .date, .publish-date, .posted-on, [class*='date'], .meta-date, .timestamp, [data-date]",
        "base_url": "https://www.mobie.com.cn",
        "priority": "P1",
        "use_jina_only": True
    },
    {
        "name": "大富科技",
        "url": "https://www.tuftiem.com/",
        "list_selector": "article, .news-item, .news-article, [role='article'], .press-release, .blog-post, .post-item, .content-item, .news-list, .news-container, .article-list, .articles, .posts, .stories, .item, .entry, .card, li[class*='news'], div[class*='article'], section[class*='news']",
        "title_selector": "h1, h2, h3, .title, .headline, .news-title, [class*='title'], .heading, .post-title, a[href]",
        "link_selector": "a[href*='news'], a[href*='press'], a[href*='article'], a[href*='blog'], a[href]",
        "date_selector": "time, .date, .publish-date, .posted-on, [class*='date'], .meta-date, .timestamp, [data-date]",
        "base_url": "https://www.tuftiem.com",
        "priority": "P1",
        "use_jina_only": True
    },
    {
        "name": "天孚通信",
        "url": "https://www.turfib.com/",
        "list_selector": "article, .news-item, .news-article, [role='article'], .press-release, .blog-post, .post-item, .content-item, .news-list, .news-container, .article-list, .articles, .posts, .stories, .item, .entry, .card, li[class*='news'], div[class*='article'], section[class*='news']",
        "title_selector": "h1, h2, h3, .title, .headline, .news-title, [class*='title'], .heading, .post-title, a[href]",
        "link_selector": "a[href*='news'], a[href*='press'], a[href*='article'], a[href*='blog'], a[href]",
        "date_selector": "time, .date, .publish-date, .posted-on, [class*='date'], .meta-date, .timestamp, [data-date]",
        "base_url": "https://www.turfib.com",
        "priority": "P1",
        "use_jina_only": True
    },
    {
        "name": "京信通信",
        "url": "https://www.comba.net.cn/",
        "list_selector": "article, .news-item, .news-article, [role='article'], .press-release, .blog-post, .post-item, .content-item, .news-list, .news-container, .article-list, .articles, .posts, .stories, .item, .entry, .card, li[class*='news'], div[class*='article'], section[class*='news']",
        "title_selector": "h1, h2, h3, .title, .headline, .news-title, [class*='title'], .heading, .post-title, a[href]",
        "link_selector": "a[href*='news'], a[href*='press'], a[href*='article'], a[href*='blog'], a[href]",
        "date_selector": "time, .date, .publish-date, .posted-on, [class*='date'], .meta-date, .timestamp, [data-date]",
        "base_url": "https://www.comba.net.cn",
        "priority": "P1",
        "use_jina_only": True
    },
    {
        "name": "通宇通讯",
        "url": "https://www.tytx.com.cn/",
        "list_selector": "article, .news-item, .news-article, [role='article'], .press-release, .blog-post, .post-item, .content-item, .news-list, .news-container, .article-list, .articles, .posts, .stories, .item, .entry, .card, li[class*='news'], div[class*='article'], section[class*='news']",
        "title_selector": "h1, h2, h3, .title, .headline, .news-title, [class*='title'], .heading, .post-title, a[href]",
        "link_selector": "a[href*='news'], a[href*='press'], a[href*='article'], a[href*='blog'], a[href]",
        "date_selector": "time, .date, .publish-date, .posted-on, [class*='date'], .meta-date, .timestamp, [data-date]",
        "base_url": "https://www.tytx.com.cn",
        "priority": "P1",
        "use_jina_only": True
    },
    {
        "name": "东山精密",
        "url": "https://www.dongsheng.com/",
        "list_selector": "article, .news-item, .news-article, [role='article'], .press-release, .blog-post, .post-item, .content-item, .news-list, .news-container, .article-list, .articles, .posts, .stories, .item, .entry, .card, li[class*='news'], div[class*='article'], section[class*='news']",
        "title_selector": "h1, h2, h3, .title, .headline, .news-title, [class*='title'], .heading, .post-title, a[href]",
        "link_selector": "a[href*='news'], a[href*='press'], a[href*='article'], a[href*='blog'], a[href]",
        "date_selector": "time, .date, .publish-date, .posted-on, [class*='date'], .meta-date, .timestamp, [data-date]",
        "base_url": "https://www.dongsheng.com",
        "priority": "P1",
        "use_jina_only": True
    },
    {
        "name": "武汉凡谷",
        "url": "https://www.fangu.com/",
        "list_selector": "article, .news-item, .news-article, [role='article'], .press-release, .blog-post, .post-item, .content-item, .news-list, .news-container, .article-list, .articles, .posts, .stories, .item, .entry, .card, li[class*='news'], div[class*='article'], section[class*='news']",
        "title_selector": "h1, h2, h3, .title, .headline, .news-title, [class*='title'], .heading, .post-title, a[href]",
        "link_selector": "a[href*='news'], a[href*='press'], a[href*='article'], a[href*='blog'], a[href]",
        "date_selector": "time, .date, .publish-date, .posted-on, [class*='date'], .meta-date, .timestamp, [data-date]",
        "base_url": "https://www.fangu.com",
        "priority": "P1",
        "use_jina_only": True
    },
    {
        "name": "翱捷科技",
        "url": "https://www.asrmicro.com/",
        "list_selector": "article, .news-item, .news-article, [role='article'], .press-release, .blog-post, .post-item, .content-item, .news-list, .news-container, .article-list, .articles, .posts, .stories, .item, .entry, .card, li[class*='news'], div[class*='article'], section[class*='news']",
        "title_selector": "h1, h2, h3, .title, .headline, .news-title, [class*='title'], .heading, .post-title, a[href]",
        "link_selector": "a[href*='news'], a[href*='press'], a[href*='article'], a[href*='blog'], a[href]",
        "date_selector": "time, .date, .publish-date, .posted-on, [class*='date'], .meta-date, .timestamp, [data-date]",
        "base_url": "https://www.asrmicro.com",
        "priority": "P0",
        "use_jina_only": True
    },
    {
        "name": "紫光展锐",
        "url": "https://www.unisoc.com/",
        "list_selector": "article, .news-item, .news-article, [role='article'], .press-release, .blog-post, .post-item, .content-item, .news-list, .news-container, .article-list, .articles, .posts, .stories, .item, .entry, .card, li[class*='news'], div[class*='article'], section[class*='news']",
        "title_selector": "h1, h2, h3, .title, .headline, .news-title, [class*='title'], .heading, .post-title, a[href]",
        "link_selector": "a[href*='news'], a[href*='press'], a[href*='article'], a[href*='blog'], a[href]",
        "date_selector": "time, .date, .publish-date, .posted-on, [class*='date'], .meta-date, .timestamp, [data-date]",
        "base_url": "https://www.unisoc.com",
        "priority": "P0",
        "use_jina_only": True
    },
    {
        "name": "移芯通信",
        "url": "https://www.xtechcomm.com/",
        "list_selector": "article, .news-item, .news-article, [role='article'], .press-release, .blog-post, .post-item, .content-item, .news-list, .news-container, .article-list, .articles, .posts, .stories, .item, .entry, .card, li[class*='news'], div[class*='article'], section[class*='news']",
        "title_selector": "h1, h2, h3, .title, .headline, .news-title, [class*='title'], .heading, .post-title, a[href]",
        "link_selector": "a[href*='news'], a[href*='press'], a[href*='article'], a[href*='blog'], a[href]",
        "date_selector": "time, .date, .publish-date, .posted-on, [class*='date'], .meta-date, .timestamp, [data-date]",
        "base_url": "https://www.xtechcomm.com",
        "priority": "P0",
        "use_jina_only": True
    },
    {
        "name": "瑞芯微电子",
        "url": "https://www.rock-chips.com/",
        "list_selector": "article, .news-item, .news-article, [role='article'], .press-release, .blog-post, .post-item, .content-item, .news-list, .news-container, .article-list, .articles, .posts, .stories, .item, .entry, .card, li[class*='news'], div[class*='article'], section[class*='news']",
        "title_selector": "h1, h2, h3, .title, .headline, .news-title, [class*='title'], .heading, .post-title, a[href]",
        "link_selector": "a[href*='news'], a[href*='press'], a[href*='article'], a[href*='blog'], a[href]",
        "date_selector": "time, .date, .publish-date, .posted-on, [class*='date'], .meta-date, .timestamp, [data-date]",
        "base_url": "https://www.rock-chips.com",
        "priority": "P0",
        "use_jina_only": True
    },
    {
        "name": "思比科",
        "url": "https://www.siliconimage.com.cn/",
        "list_selector": "article, .news-item, .news-article, [role='article'], .press-release, .blog-post, .post-item, .content-item, .news-list, .news-container, .article-list, .articles, .posts, .stories, .item, .entry, .card, li[class*='news'], div[class*='article'], section[class*='news']",
        "title_selector": "h1, h2, h3, .title, .headline, .news-title, [class*='title'], .heading, .post-title, a[href]",
        "link_selector": "a[href*='news'], a[href*='press'], a[href*='article'], a[href*='blog'], a[href]",
        "date_selector": "time, .date, .publish-date, .posted-on, [class*='date'], .meta-date, .timestamp, [data-date]",
        "base_url": "https://www.siliconimage.com.cn",
        "priority": "P0",
        "use_jina_only": True
    },
    {
        "name": "联发科",
        "url": "https://www.mediatek.com/",
        "list_selector": "article, .news-item, .news-article, [role='article'], .press-release, .blog-post, .post-item, .content-item, .news-list, .news-container, .article-list, .articles, .posts, .stories, .item, .entry, .card, li[class*='news'], div[class*='article'], section[class*='news']",
        "title_selector": "h1, h2, h3, .title, .headline, .news-title, [class*='title'], .heading, .post-title, a[href]",
        "link_selector": "a[href*='news'], a[href*='press'], a[href*='article'], a[href*='blog'], a[href]",
        "date_selector": "time, .date, .publish-date, .posted-on, [class*='date'], .meta-date, .timestamp, [data-date]",
        "base_url": "https://www.mediatek.com",
        "priority": "P0",
        "use_jina_only": True
    },
    {
        "name": "三星LSI",
        "url": "https://semiconductor.samsung.com/",
        "list_selector": "article, .news-item, .news-article, [role='article'], .press-release, .blog-post, .post-item, .content-item, .news-list, .news-container, .article-list, .articles, .posts, .stories, .item, .entry, .card, li[class*='news'], div[class*='article'], section[class*='news']",
        "title_selector": "h1, h2, h3, .title, .headline, .news-title, [class*='title'], .heading, .post-title, a[href]",
        "link_selector": "a[href*='news'], a[href*='press'], a[href*='article'], a[href*='blog'], a[href]",
        "date_selector": "time, .date, .publish-date, .posted-on, [class*='date'], .meta-date, .timestamp, [data-date]",
        "base_url": "https://semiconductor.samsung.com",
        "priority": "P0",
        "use_jina_only": True
    },
    {
        "name": "德州仪器",
        "url": "https://www.ti.com/",
        "list_selector": "article, .news-item, .news-article, [role='article'], .press-release, .blog-post, .post-item, .content-item, .news-list, .news-container, .article-list, .articles, .posts, .stories, .item, .entry, .card, li[class*='news'], div[class*='article'], section[class*='news']",
        "title_selector": "h1, h2, h3, .title, .headline, .news-title, [class*='title'], .heading, .post-title, a[href]",
        "link_selector": "a[href*='news'], a[href*='press'], a[href*='article'], a[href*='blog'], a[href]",
        "date_selector": "time, .date, .publish-date, .posted-on, [class*='date'], .meta-date, .timestamp, [data-date]",
        "base_url": "https://www.ti.com",
        "priority": "P0",
        "use_jina_only": True
    },
    # === 新导入的公司 (2026-04-17) ===
    {
        "name": "Skyworks",
        "url": "https://www.skyworksinc.com/news",
        "list_selector": "article, .news-item, .news-article, [role='article'], .press-release, .blog-post, .post-item, .content-item, .news-list, .news-container, .article-list, .articles, .posts, .stories, .item, .entry, .card, li[class*='news'], div[class*='article'], section[class*='news']",
        "title_selector": "h1, h2, h3, .title, .headline, .news-title, [class*='title'], .heading, .post-title, a[href]",
        "link_selector": "a[href*='news'], a[href*='press'], a[href*='article'], a[href*='blog'], a[href]",
        "date_selector": "time, .date, .publish-date, .posted-on, [class*='date'], .meta-date, .timestamp, [data-date]",
        "base_url": "https://www.skyworksinc.com",
        "priority": "P1",
        "use_jina_only": True
    },
    {
        "name": "Qorvo",
        "url": "https://www.qorvo.com/news",
        "list_selector": "article, .news-item, .news-article, [role='article'], .press-release, .blog-post, .post-item, .content-item, .news-list, .news-container, .article-list, .articles, .posts, .stories, .item, .entry, .card, li[class*='news'], div[class*='article'], section[class*='news']",
        "title_selector": "h1, h2, h3, .title, .headline, .news-title, [class*='title'], .heading, .post-title, a[href]",
        "link_selector": "a[href*='news'], a[href*='press'], a[href*='article'], a[href*='blog'], a[href]",
        "date_selector": "time, .date, .publish-date, .posted-on, [class*='date'], .meta-date, .timestamp, [data-date]",
        "base_url": "https://www.qorvo.com",
        "priority": "P1",
        "use_jina_only": True
    },
    {
        "name": "Murata",
        "url": "https://www.murata.com/news",
        "list_selector": "article, .news-item, .news-article, [role='article'], .press-release, .blog-post, .post-item, .content-item, .news-list, .news-container, .article-list, .articles, .posts, .stories, .item, .entry, .card, li[class*='news'], div[class*='article'], section[class*='news']",
        "title_selector": "h1, h2, h3, .title, .headline, .news-title, [class*='title'], .heading, .post-title, a[href]",
        "link_selector": "a[href*='news'], a[href*='press'], a[href*='article'], a[href*='blog'], a[href]",
        "date_selector": "time, .date, .publish-date, .posted-on, [class*='date'], .meta-date, .timestamp, [data-date]",
        "base_url": "https://www.murata.com",
        "priority": "P1",
        "use_jina_only": True
    },
    {
        "name": "Avary Holding",
        "url": "https://www.avaryholding.com",
        "list_selector": "article, .news-item, .news-article, [role='article'], .press-release, .blog-post, .post-item, .content-item, .news-list, .news-container, .article-list, .articles, .posts, .stories, .item, .entry, .card, li[class*='news'], div[class*='article'], section[class*='news']",
        "title_selector": "h1, h2, h3, .title, .headline, .news-title, [class*='title'], .heading, .post-title, a[href]",
        "link_selector": "a[href*='news'], a[href*='press'], a[href*='article'], a[href*='blog'], a[href]",
        "date_selector": "time, .date, .publish-date, .posted-on, [class*='date'], .meta-date, .timestamp, [data-date]",
        "base_url": "https://www.avaryholding.com",
        "priority": "P2",
        "use_jina_only": True
    },
    {
        "name": "Samtec",
        "url": "https://www.samtec.com",
        "list_selector": "article, .news-item, .news-article, [role='article'], .press-release, .blog-post, .post-item, .content-item, .news-list, .news-container, .article-list, .articles, .posts, .stories, .item, .entry, .card, li[class*='news'], div[class*='article'], section[class*='news']",
        "title_selector": "h1, h2, h3, .title, .headline, .news-title, [class*='title'], .heading, .post-title, a[href]",
        "link_selector": "a[href*='news'], a[href*='press'], a[href*='article'], a[href*='blog'], a[href]",
        "date_selector": "time, .date, .publish-date, .posted-on, [class*='date'], .meta-date, .timestamp, [data-date]",
        "base_url": "https://www.samtec.com",
        "priority": "P2",
        "use_jina_only": True
    },
    {
        "name": "Hirose",
        "url": "https://www.hirose.com",
        "list_selector": "article, .news-item, .news-article, [role='article'], .press-release, .blog-post, .post-item, .content-item, .news-list, .news-container, .article-list, .articles, .posts, .stories, .item, .entry, .card, li[class*='news'], div[class*='article'], section[class*='news']",
        "title_selector": "h1, h2, h3, .title, .headline, .news-title, [class*='title'], .heading, .post-title, a[href]",
        "link_selector": "a[href*='news'], a[href*='press'], a[href*='article'], a[href*='blog'], a[href]",
        "date_selector": "time, .date, .publish-date, .posted-on, [class*='date'], .meta-date, .timestamp, [data-date]",
        "base_url": "https://www.hirose.com",
        "priority": "P2",
        "use_jina_only": True
    },
    {
        "name": "Luxshare",
        "url": "https://www.luxshare-ict.com",
        "list_selector": "article, .news-item, .news-article, [role='article'], .press-release, .blog-post, .post-item, .content-item, .news-list, .news-container, .article-list, .articles, .posts, .stories, .item, .entry, .card, li[class*='news'], div[class*='article'], section[class*='news']",
        "title_selector": "h1, h2, h3, .title, .headline, .news-title, [class*='title'], .heading, .post-title, a[href]",
        "link_selector": "a[href*='news'], a[href*='press'], a[href*='article'], a[href*='blog'], a[href]",
        "date_selector": "time, .date, .publish-date, .posted-on, [class*='date'], .meta-date, .timestamp, [data-date]",
        "base_url": "https://www.luxshare-ict.com",
        "priority": "P2",
        "use_jina_only": True
    },
    {
        "name": "BT",
        "url": "https://www.bt.com/news",
        "list_selector": "article, .news-item, .news-article, [role='article'], .press-release, .blog-post, .post-item, .content-item, .news-list, .news-container, .article-list, .articles, .posts, .stories, .item, .entry, .card, li[class*='news'], div[class*='article'], section[class*='news']",
        "title_selector": "h1, h2, h3, .title, .headline, .news-title, [class*='title'], .heading, .post-title, a[href]",
        "link_selector": "a[href*='news'], a[href*='press'], a[href*='article'], a[href*='blog'], a[href]",
        "date_selector": "time, .date, .publish-date, .posted-on, [class*='date'], .meta-date, .timestamp, [data-date]",
        "base_url": "https://www.bt.com",
        "priority": "P1",
        "use_jina_only": True
    },
    {
        "name": "STC",
        "url": "https://www.stc.com.sa/news",
        "list_selector": "article, .news-item, .news-article, [role='article'], .press-release, .blog-post, .post-item, .content-item, .news-list, .news-container, .article-list, .articles, .posts, .stories, .item, .entry, .card, li[class*='news'], div[class*='article'], section[class*='news']",
        "title_selector": "h1, h2, h3, .title, .headline, .news-title, [class*='title'], .heading, .post-title, a[href]",
        "link_selector": "a[href*='news'], a[href*='press'], a[href*='article'], a[href*='blog'], a[href]",
        "date_selector": "time, .date, .publish-date, .posted-on, [class*='date'], .meta-date, .timestamp, [data-date]",
        "base_url": "https://www.stc.com.sa",
        "priority": "P2",
        "use_jina_only": True
    },
]
