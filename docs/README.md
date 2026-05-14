# CT产业情报Agent

专注于通信设备制造产业的智能情报监测与分析Agent

覆盖无线通信、光通信、核心网、传输设备等全产业链

---

## 📋 功能特性

- 🔍 **多源数据采集**: RSS、网页爬虫、搜索引擎、专利数据等
- 🧠 **AI智能分析**: 使用LLM进行情报分类、评分、决策价值判断
- 📚 **RAG知识增强**: 基于通信技术专业知识库的向量检索增强
- 📊 **周报自动生成**: 自动生成分层结构的产业情报周报
- 📤 **自动分发**: 支持邮件和企业微信Webhook发送
- ⏰ **定时调度**: 支持定时任务自动执行

---

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env`，填写你的API密钥：

```bash
cp .env.example .env
# 编辑 .env 文件，填写API密钥
```

必需配置至少一个LLM API密钥:
- `LLM__DEEPSEEK_API_KEY` - DeepSeek API密钥
- `LLM__QWEN_API_KEY` - 通义千问API密钥
- `LLM__KIMI_API_KEY` - Kimi API密钥
- `LLM__CLAUDE_API_KEY` - Claude API密钥

### 3. 运行测试

```bash
python main.py --test
```

### 4. 执行采集和分析

```bash
# 完整流程（采集+分析+生成报告）
python main.py

# 仅采集分析
python main.py --collect

# 仅生成周报
python main.py --report
```

### 5. 定时调度模式

```bash
python main.py --schedule
```

---

## 📁 项目结构

```
telecom-equipment-intel/
├── main.py                    # 主入口
├── config.py                  # 配置管理
├── database.py                # 数据库操作
├── llm.py                     # LLM路由层
├── build_index.py             # 向量索引构建
├── requirements.txt           # 依赖包
├── .env.example               # 环境变量示例
├── README.md                  # 项目说明
├── collectors/                # 采集器模块
│   ├── base.py               # 采集器基类
│   ├── rss_collector.py      # RSS采集
│   ├── web_collector.py      # 网页采集
│   └── search_collector.py   # 搜索采集
├── processors/                # 处理器模块
│   ├── analyzer.py           # AI分析器
│   └── rag.py                # RAG检索
├── reporters/                 # 报告模块
│   ├── report_generator.py   # 周报生成
│   └── distribution.py       # 分发
├── models/                    # 数据模型
│   └── __init__.py
├── knowledge_base/            # 知识库
│   └── technical_keywords.yaml
└── data/                      # 数据目录
    ├── intel.db              # SQLite数据库
    └── reports/              # 生成的周报
```

---

## 🔧 配置说明

### LLM配置

支持多模型自动降级，配置多个API密钥可提高稳定性：

```env
LLM__DEEPSEEK_API_KEY=your_key
LLM__QWEN_API_KEY=your_key
LLM__KIMI_API_KEY=your_key
LLM__CLAUDE_API_KEY=your_key
```

### 分发配置

#### 邮件发送

```env
DISTRIBUTION__SMTP_SERVER=smtp.example.com
DISTRIBUTION__SMTP_PORT=587
DISTRIBUTION__SMTP_USER=your_email@example.com
DISTRIBUTION__SMTP_PASSWORD=your_password
DISTRIBUTION__EMAIL_RECIPIENTS=recipient1@example.com,recipient2@example.com
DISTRIBUTION__ENABLE_EMAIL=true
```

#### 企业微信发送

```env
DISTRIBUTION__WECHAT_WEBHOOK_URL=https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=your_key
DISTRIBUTION__ENABLE_WECHAT=true
```

### 调度配置

```env
SCHEDULE__DAY_OF_WEEK=fri  # 每周五
SCHEDULE__HOUR=9           # 9点
SCHEDULE__MINUTE=0         # 0分
```

---

## 📖 使用指南

### 添加监控关键词

编辑 `collectors/base.py` 中的 `MONITORED_KEYWORDS`。如需平台化关键词配置，可在后续版本迁移到数据库或 Web 配置页。

### 更新知识库

```bash
# 编辑知识库文件
vim knowledge_base/technical_keywords.yaml

# 重建向量索引
python build_index.py --reset
```

### 添加新知识

```bash
python build_index.py --add --category "新技术" --description "描述内容" --keywords "关键词1,关键词2"
```

### 查看知识库

```bash
python build_index.py --show
```

---

## 🧩 系统架构

```
┌─────────────────────────────────────────────────────────┐
│  启动方式                                                │
│  python main.py              # 立即执行一次              │
│  python main.py --schedule   # 定时调度（每周五9:00）     │
│  python main.py --collect    # 仅采集分析                │
│  python main.py --report     # 仅生成周报                │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│  Step 1: 多源采集                                       │
│  - RSSCollector: RSS订阅源采集                          │
│  - WebCollector: 竞争对手官网采集                        │
│  - SearchCollector: 搜索引擎采集                         │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│  Step 2: AI分析处理                                     │
│  - URL去重 → 标题去重                                    │
│  - 向量RAG检索（知识增强）                                │
│  - LLM分析（分类/评分/决策价值判断）                      │
│  - 数据库存储                                            │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│  Step 3: 周报生成                                       │
│  - 查询本周数据                                          │
│  - 多轮过滤（时效性/重要性/新闻类型）                     │
│  - 生成Markdown + HTML格式                               │
│  - 保存到本地文件                                        │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│  Step 4: 分发                                           │
│  - 邮件发送                                              │
│  - 企业微信Webhook发送                                    │
└─────────────────────────────────────────────────────────┘
```

---

## 📊 数据模型

### 情报条目 (IntelItem)

| 字段 | 说明 |
|------|------|
| title | 标题 |
| source_url | 来源URL |
| category | 分类：关键公司动态/专利情况/新技术/投资收购/下游产业应用 |
| importance | 重要性：1-5分 |
| decision_value | 是否有决策价值 |
| tech_domain | 技术领域：无线通信/光通信/核心网/传输承载/接入网/终端设备 |
| industry | 下游行业：电信运营商/政企专网/数据中心/工业互联网/车联网 |

---

## 🔍 监控范围

| 维度 | 数量 | 说明 |
|------|------|------|
| 关键词 | 200+ | 覆盖5G/6G、光通信、核心网、SDN/NFV等 |
| 公司 | 200+ | 华为、中兴、爱立信、诺基亚、思科等国内外企业 |
| 下游行业 | 7大 | 电信运营商、政企专网、数据中心、工业互联网等 |

---

## 📜 开源协议

MIT License

---

*基于通信设备产业场景整理*
