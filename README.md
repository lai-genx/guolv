# CT产业情报Agent v1.1

通信设备产业情报自动采集、AI分析与周报生成系统。

## 功能概览

- **多源采集**：RSS订阅（16个源） + 企业官网爬取 + 搜索引擎
- **AI分析**：DeepSeek/通义千问/Kimi/Claude 多模型路由，自动降级
- **智能分类**：6大分类、6大技术领域、产业链标注、重要度评分
- **周报生成**：自动生成 Markdown + HTML 周报，支持邮件/企微分发
- **Agent升级**：周计划自主规划、历史记忆系统、RAG检索增强

## Web界面（v1.1 新增）

基于 Streamlit 构建，5个功能页面：

| 页面 | 功能 |
|------|------|
| 📊 仪表盘 | 最新周报摘要 + 情报数量趋势图 + 分类/重要度分布图 |
| 📋 报告列表 | 历史周报，可展开查看完整 Markdown/HTML 内容 |
| 🔍 情报库 | 所有情报条目，按分类/领域/重要度筛选，**支持原文链接跳转** |
| 🚀 采集中心 | 手动触发采集，**实时显示采集进度**（正在采集哪个源、获取多少条、AI分析进度） |
| ⚙️ 设置 | 邮件/企微配置（Web界面直接改），API Key状态展示 |

## 快速开始

### 1. 环境准备

```bash
# 方式一：自动安装（推荐）
bash setup.sh          # Linux/Mac
setup.bat              # Windows 双击运行

# 方式二：手动安装
pip install -r requirements.txt
```

### 2. 配置

```bash
# 复制配置模板
cp .env.example .env

# 编辑 .env，至少配置：
# - LLM__DEEPSEEK_API_KEY  （DeepSeek API密钥，必填）
# - DISTRIBUTION__SMTP_*    （邮件配置，可选）
```

### 3. 启动

```bash
streamlit run web_app.py --server.port 8501
```

浏览器打开 http://localhost:8501

### 4. 命令行使用（无Web界面）

```bash
python main.py              # 完整流程：采集+分析+生成周报
python main.py --collect    # 仅采集+分析
python main.py --report     # 仅生成周报
python main.py --schedule   # 定时调度（默认每周五9:00）
python main.py --test       # 检查配置
```

## 配置说明

### LLM配置（必填至少一个）

| 变量 | 说明 | 默认值 |
|------|------|--------|
| LLM__DEEPSEEK_API_KEY | DeepSeek API密钥 | - |
| LLM__QWEN_API_KEY | 通义千问API密钥 | - |
| LLM__KIMI_API_KEY | Kimi API密钥 | - |
| LLM__CLAUDE_API_KEY | Claude API密钥 | - |
| LLM__DEFAULT_MODEL | 默认模型 | deepseek-chat |

### 邮件配置（可选）

| 变量 | 说明 | 示例 |
|------|------|------|
| DISTRIBUTION__SMTP_SERVER | SMTP服务器 | smtp.exmail.qq.com |
| DISTRIBUTION__SMTP_PORT | 端口 | 587 |
| DISTRIBUTION__SMTP_USER | 发信邮箱 | user@example.com |
| DISTRIBUTION__SMTP_PASSWORD | 授权码 | - |
| DISTRIBUTION__EMAIL_RECIPIENTS | 收件人（JSON数组） | ["a@example.com"] |
| DISTRIBUTION__ENABLE_EMAIL | 启用邮件 | true |

### 采集配置（可选）

| 变量 | 说明 | 默认值 |
|------|------|--------|
| COLLECTOR__HTTP_PROXY | HTTP代理 | - |
| COLLECTOR__JINA_API_KEY | Jina Reader密钥 | - |

## 项目结构

```
telecom-equipment-intel/
├── web_app.py              # Streamlit Web界面（v1.1新增）
├── main.py                 # 命令行主入口
├── config.py               # 配置管理
├── llm.py                  # LLM多模型路由
├── database.py             # SQLite数据库
├── models/                 # 数据模型
├── collectors/             # 数据采集器
│   ├── rss_collector.py    # RSS采集
│   ├── web_collector.py    # 网站爬取
│   └── search_collector.py # 搜索采集
├── processors/             # AI处理
│   ├── analyzer.py         # 情报分析
│   ├── rag.py              # RAG检索增强
│   ├── planning_agent.py   # 周计划Agent
│   └── episodic_memory.py  # 历史记忆
├── reporters/              # 报告生成与分发
├── data/                   # 数据目录
│   ├── intel.db            # SQLite数据库
│   └── reports/            # 周报文件
├── requirements.txt        # Python依赖
├── setup.sh / setup.bat    # 环境初始化脚本
└── .env.example            # 配置模板
```

## 监控范围

- **130+家公司**：华为、中兴、爱立信、高通、Broadcom、Ciena、Verizon等
- **16个RSS源**：Ars Technica, VentureBeat, C114通信网, Semiconductor Digest等
- **6大分类**：关键公司动态、专利、新技术、投资收购、下游应用、其他
- **6大技术领域**：无线通信、光通信、核心网、传输承载、接入网、终端设备

## 版本历史

### v1.1 (2026-04-16)

- 新增 Streamlit Web界面，5个功能页面
- 采集中心：手动触发采集，实时显示进度日志
- 情报库：支持分类/领域/重要度筛选，原文链接可点击跳转
- 设置页面：邮件/企微配置可在Web界面修改
- 依赖自动检测：缺少依赖时页面提示一键安装
- 新增 requirements.txt、setup.sh/setup.bat 环境初始化
- 新增 Git 版本管理

### v1.0 (2026-03-28)

- 初始版本
- RSS + Web + Search 多源采集
- DeepSeek/Qwen/Kimi/Claude 多模型路由
- AI分析分类、重要度评分、中文摘要
- 周报自动生成与邮件/企微分发
- RAG检索增强、周计划Agent、历史记忆系统
