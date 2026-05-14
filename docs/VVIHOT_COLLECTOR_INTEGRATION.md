# 识微商情/VviHot采集器接入说明

## 接入目标

新增 `VviHotCollector`，用于读取识微商情平台中已配置的监测主题文章，并替代原来的搜索引擎采集。

启用后主流程为：

```text
RSSCollector
WebCollector
VviHotCollector  # 替代 SearchCollector
PatentCollector
        ↓
RawIntelData
        ↓
LLM分析、去重、入库、周报
```

## 配置方式

在 `.env` 中增加：

```env
COLLECTOR__ENABLE_VVIHOT=true
COLLECTOR__VVIHOT_URL=https://zreywc.vvihot.com/swsq/
COLLECTOR__VVIHOT_USERNAME=你的平台账号
COLLECTOR__VVIHOT_PASSWORD=你的平台密码
COLLECTOR__VVIHOT_HEADLESS=true
COLLECTOR__VVIHOT_WAIT_SECONDS=12
COLLECTOR__VVIHOT_MAX_ITEMS=80
COLLECTOR__VVIHOT_TOPIC_NAMES=
```

`COLLECTOR__VVIHOT_TOPIC_NAMES` 可选。留空表示采集全部可见主题；如果只采集部分主题，可填写：

```env
COLLECTOR__VVIHOT_TOPIC_NAMES=5G,通信设备综合,重点厂商动态
```

## 替代逻辑

`main.py` 中的采集器初始化逻辑为：

- `COLLECTOR__ENABLE_VVIHOT=true`：启用 `VviHotCollector`，跳过 `SearchCollector`。
- `COLLECTOR__ENABLE_VVIHOT=false` 且 `COLLECTOR__ENABLE_SEARCH=true`：继续使用原 `SearchCollector`。
- `RSSCollector`、`WebCollector`、`PatentCollector` 不受影响。

## 平台字段映射

平台文章会转换为：

| 平台字段 | 项目字段 |
|---|---|
| `title` | `RawIntelData.title` |
| `url` | `RawIntelData.url` |
| `websiteName/domain` | `RawIntelData.source` |
| 固定 `vvihot` | `RawIntelData.source_type` |
| `createdAt/createTime` | `RawIntelData.pub_date` |
| `content` | `RawIntelData.content` |
| 来源、媒体类型、主题、正文摘要 | `RawIntelData.summary` |

## 关键词主题建议

由于平台账号可能有主题数量限制，建议将项目关键词合并成少量主题：

```text
通信设备综合：
(5G || 6G || 5G-A || "5G Advanced" || "Open RAN" || O-RAN || vRAN || 基站 || 通信设备)

重点厂商动态：
(华为 || 中兴 || Ericsson || Nokia || Samsung || Cisco || Ciena || Juniper) && (5G || 6G || 网络 || 通信 || 设备 || 基站 || 光通信)

光通信与光模块：
(光通信 || 光模块 || 硅光 || CPO || LPO || OTN || WDM || DWDM || coherent || 光芯片)

核心网与云网：
(核心网 || "5G Core" || UPF || MEC || 网络切片 || SDN || NFV || 云原生网络 || 算网融合)

投融资/专利/标准：
(专利 || 收购 || 融资 || 投资 || 合作 || 发布 || 3GPP || Release 18 || Release 19 || ITU-R)
```

## 注意事项

- 平台账号密码只应写在本地 `.env` 中，不能提交到 GitHub。
- 平台采集依赖 Playwright 和 Chromium。首次使用需要执行：

```bash
python -m playwright install chromium
```

- 平台页面数据是异步加载的，`COLLECTOR__VVIHOT_WAIT_SECONDS` 控制登录后等待多久再结束采集。
- 采集器仍会使用项目关键词进行二次过滤，降低泛舆情内容进入分析流程的概率。
