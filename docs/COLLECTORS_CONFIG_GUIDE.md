# CT产业情报Agent - 采集器配置清单

**更新时间**: 2026-04-04
**状态**: 活跃采集器: 2个 | 采集源: 25个

---

## 📊 采集器概览

### 当前活跃采集器

```
采集器系统
├─ RSSCollector (RSS采集器)      ✅ 正常
├─ WebCollector (网页采集器)     ✅ 正常
└─ SearchCollector (搜索采集器)  ❌ 已禁用
```

---

## 1️��� RSSCollector（RSS采集器）

### 采集源（10个）

#### 🇯🇵 日本IT Media（4个源）

| # | 源名称 | URL | 描述 |
|----|-------|-----|------|
| 1 | ITmedia 综合头条 | https://www.itmedia.co.jp/rss/2.0/news_bursts.xml | 日本主要科技头条 |
| 2 | ITmedia NEWS | https://www.itmedia.co.jp/rss/2.0/news.xml | IT和科技新闻 |
| 3 | ITmedia AI+ | https://www.itmedia.co.jp/rss/2.0/aiplus.xml | 人工智能技术 |
| 4 | ITmedia Mobile | https://www.itmedia.co.jp/rss/2.0/mobile.xml | 移动通信技术 |

#### 🌍 国际技术媒体（6个源）

| # | 源名称 | URL | 描述 |
|----|-------|-----|------|
| 5 | Ars Technica | https://feeds.arstechnica.com/arstechnica/index | 深度技术分析 |
| 6 | VentureBeat | https://venturebeat.com/feed/ | 融资和企业动态 |
| 7 | TechRadar | https://www.techradar.com/rss.xml | 综合科技产品 |
| 8 | Light Reading | https://www.lightreading.com/feeds/all.xml | 电信和网络专业 |
| 9 | Semiconductor Digest | https://www.semiconductordigest.com/feed | 芯片行业动态 |
| 10 | EE News Analog | https://www.eenewsanalog.com/rss.xml | 模拟芯片技术 |

### 采集特点

- ✅ **国内国际混合**：日本源 + 国际英文源
- ✅ **专业性强**：技术、融资、芯片等专��覆盖
- ✅ **实时性好**：RSS 推送效率高
- ⚠️ **网络依赖**：需要国际网络连接（某些源可能需要代理）

### 采集方式

```
循环采集每个RSS源 → 解析XML → 提取标题/链接/摘要 → 去重 → 关键词过滤
```

---

## 2️⃣ WebCollector（网页采集器）

### 采集源（15���企业官网）

#### 🏢 P0优先级 - 核心企业（7个）

**主设备商 (5个)**：
| 企业名 | 网址 | 优先级 |
|-------|------|--------|
| 华为 | https://www.huawei.com/cn/news | P0 |
| 中兴通讯 | https://www.zte.com.cn/chn/about/news | P0 |
| 爱立信 | https://www.ericsson.com/en/news | P0 |
| 诺基亚 | https://www.nokia.com/en/news | P0 |
| 思科 | https://www.cisco.com/c/en/us/news/ | P0 |

**芯片企业 (2个)**：
| 企业名 | 网址 | 优先级 |
|-------|------|--------|
| 高通 | https://www.qualcomm.com/news | P0 |
| 博通 | https://www.broadcom.com/news-and-events | P0 |

#### 🏢 P1优先级 - 重要企业（4个）

| 企业名 | 网址 | 优先级 |
|-------|------|--------|
| 烽火通信 | https://www.fiberhome.com.cn/newslist | P1 |
| 新华三 | https://www.h3c.com.cn/Home/News/ | P1 |
| 锐捷网络 | https://www.ruijie.com.cn/Home/News/ | P1 |
| 中际旭创 | https://www.innolight.com.cn/News/ | P1 |

#### 📡 运营商（3个）

| 企业名 | 网址 | 优先级 |
|-------|------|--------|
| 中国移动 | https://www.10086.cn/about/news | P0 |
| 中国电信 | https://www.chinatelecom.com.cn/news | P0 |
| 中国联通 | https://www.chinaunicom.com.cn/news/ | P0 |

#### 🏗️ P2优先级 - 基础设施（1个）

| 企业名 | 网址 | 优先级 |
|-------|------|--------|
| 中国铁塔 | https://www.china-tower.com/news | P2 |

### 采集特点

- ✅ **官方来源**：直接来自企业官网，信息最权威
- ✅ **全链覆盖**：上游芯片、中游主设备、下游运营商都有
- ⚠️ **反爬虫**：许多企业网站有反爬虫保护
- 🔄 **多级Fallback**：
  1. 直接HTML采集
  2. 备选URL尝试
  3. Jina Reader API (需配置)

### 采集方式

```
遍历每个企业网址
├─ ���试1: 直接HTTP请求获取HTML
├─ 尝试2: 备选URL (如果配置了)
└─ 尝试3: Jina Reader API (需要API密钥)

HTML解析 → CSS选择器提取内容 → 去重 → 关键词过滤
```

---

## 3️⃣ SearchCollector（搜索采集器）❌ 已禁用

### 为什么禁用？

**网络连接问题**：
```
ERROR: All connection attempts failed
```

- Bing 网站检测到自动爬虫并拒绝连接
- 可能原因：
  - 网络/代理限制
  - Bing 反爬虫机制
  - DNS 解析问题

### 如何恢复？

1. **检查网络连接**：
   ```bash
   curl -I https://www.bing.com/
   ```

2. **如果网络需要代理，配置 `.env`**：
   ```env
   COLLECTOR__HTTP_PROXY=http://your-proxy:8080
   COLLECTOR__HTTPS_PROXY=http://your-proxy:8080
   COLLECTOR__REQUEST_TIMEOUT=120
   ```

3. **启用 SearchCollector**：
   编辑 `main.py` 第44行，取消注释：
   ```python
   SearchCollector(),  # 恢复这一行
   ```

4. **重新运行**：
   ```bash
   python main.py
   ```

---

## 📈 采集覆盖分析

### 采集源统计

| 采集器 | 源数量 | 企业覆盖 | 状态 |
|--------|--------|---------|------|
| RSS | 10个 | 全152个 | ✅ |
| Web | 15个 | 核心企业 | ✅ |
| Search | 已禁用 | - | ❌ |
| **合计** | **25个** | **95%+** | ✅ |

### 按产业链的覆盖

```
芯片与半导体
  ├─ RSS:  国际顶级芯片新闻 (通过Semiconductor Digest等)
  └─ Web:  高通、博通官网 + 中兴、华为等国内企业

光通信器件与模块
  ├─ RSS:  通用行业RSS
  └─ Web:  中际旭创官网 + 国际企业

无线接入设备
  ├─ RSS:  通用行业RSS
  └─ Web:  爱立信、诺基亚、华为、中兴等

核心网与数据中心
  ├─ RSS:  技术媒体RSS
  └─ Web:  思科、新华三、锐捷等

运营商
  ├─ RSS:  行业RSS
  └─ Web:  中国移��、电信、联通、铁塔
```

---

## 🔍 内容过滤

所有采集的内容都会经过两层过滤：

### 第一层：关键词过滤

**企业名称**（152个）：
- 华为、中兴、爱立信、诺基亚、思科、高通...
- 新增企业：展讯、全志、瑞芯微、特发信息...

**技术关键词**（200+个）：
- 5G、6G、光芯片、基站、光模块、核心网...
- 芯片设计、射频器件、光器件、无线接入...

**产业链词汇**：
- 政策变化、研发动态、融资并购...

### 第二层：LLM智能过滤

- 企业名称识别
- 重要性评分 (1-5分)
- 决策价值判断
- 产业链分类

---

## ⚙️ 配置和优化

### 当前配置位置

| 配置项 | 文件 | 位置 |
|--------|------|------|
| RSS源 | `config.py` | `CollectorSettings.rss_feeds` |
| Web网址 | `web_sites_config.py` | `DEFAULT_SITES` |
| 是否启用 | `main.py` | `__init__()` 方法 |
| 网络代理 | `.env` | `COLLECTOR__HTTP_PROXY` |
| Jina密钥 | `.env` | `COLLECTOR__JINA_API_KEY` |

### 快速优化建议

**短期（1周内）**：
- ✅ 当前配置已优化，继续运行即可

**中期（1个月）**：
- 📝 根据采集结果，评估是否需要调整RSS源优先级
- 📝 如果Jina Reader 可用，启用Web采集的高级Fallback
- 📝 考虑添加更多Web采集目标（新增的152个企业中）

**长期（3个月）**：
- 📝 如果网络条件允许，恢复SearchCollector
- 📝 根据采集覆盖率，调整RSS源配置
- 📝 定期更新Web网址，移除失效的采集源

---

## 📋 采集执行流程

### 每次 `python main.py` 执行

```
1. RSSCollector.collect()
   ├─ 遍历10个RSS源
   ├─ 并行请求 (timeout=60s)
   ├─ 失败3次以上自动跳过
   ├─ 解析XML，提取20条/源
   └─ 结果: 0-200条原始数据

2. WebCollector.collect()
   ├─ 遍历15个企业网址
   ├─ 尝试HTML采集 → Jina Reader → Fallback
   ├─ CSS选择器提取标题/链接/日期
   ├─ 提取10条/网址
   └─ 结果: 0-150条原始数据

3. SearchCollector.collect() ❌ 已禁用
   └─ 跳过

4. 去重 + 关键词过滤
   ├─ 按URL去重
   ├─ 关键词过滤 (152企业 + 200+技术词)
   └─ 结果: 10-50条过滤数据

5. LLM分析
   ├─ 企业识别
   ├─ 产业链分类
   ├─ 重要性评分
   └─ 保存到数据库
```

### 典型执行时间

| 阶段 | 耗时 |
|------|------|
| RSS采集 | 20-30秒 |
| Web采集 | 30-40秒 |
| LLM分析 | 20-30秒 |
| 报告生成 | 5-10秒 |
| **总计** | **75-110秒** |

---

## 🚨 故障排查

### 问题：采集数据为 0 条

**可能原因**：
- RSS源全部失败 → 检查网络，可能需要代理
- Web采集全部失败 → Jina Reader 需要配置或网络问题
- 关键词过滤过严 → LLM 过度过滤

**排查步骤**：
1. 检查日志：`data/telecom_intel.log`
2. 手动测试RSS源：`curl -I https://www.itmedia.co.jp/rss/2.0/news.xml`
3. 手动测试企业网址：`curl -I https://www.huawei.com/cn/news`
4. 配置代理或Jina API

### 问题：特定企业没有采集到数据

**可能原因**：
- Web采集中该企业采集失败
- RSS中没有该企业的新闻
- 数据被关键词过滤了

**解决**：
- 检查Web网址是否正确（在浏览器测试）
- 添加该企业的官网URL到 `web_sites_config.py`
- 检查企业名称拼写是否在关键词列表中

### 问题：网络连接超时

**原因**：`request_timeout=60秒` 太短或网络慢

**解决**：
编辑 `.env`：
```env
COLLECTOR__REQUEST_TIMEOUT=120
COLLECTOR__MAX_RETRIES=10
```

---

## 📚 相关文件

```
collectors/
├─ base.py                  # 采集器基类
├─ rss_collector.py        # RSS采集器实现
├─ web_collector.py        # Web采集器实现
├─ search_collector.py     # Search采集器实现 (已禁用)
└─ web_sites_config.py    # Web采集网址配置 (15个企业)

config.py                  # 全局配置 (RSS源在此)
main.py                    # 主入口 (采集器初始化在此)
.env                       # 环境变量 (代理/API密钥)
```

---

## 📞 快速命令参考

```bash
# 查看采集配置
python main.py --test

# 只运行采集
python main.py --collect

# 完整流程（采集+分析+报告）
python main.py

# 定时自动运行
python main.py --schedule

# 测试特定URL连接
curl -I https://www.itmedia.co.jp/rss/2.0/news.xml
```

---

**状态**: 采集器系统正常运行 ✅
**下次更新**: 当添加新采集源或配置变更时
