# 2026-05-14 功能补齐与修正文档

本次修正目标：按照 `docs/README.md` 中描述的功能，补齐缺失实现、修正已禁用功能、补齐运行配置，并保留现有项目架构。

## 1. 运行与配置修正

### 新增 `.env.example`

新增文件：

- `.env.example`

修正原因：

- README 和 `setup.bat` / `setup.sh` 都要求从 `.env.example` 复制 `.env`，但项目根目录原本不存在该文件。

新增内容：

- LLM API Key 配置
- Jina Reader 配置
- 搜索采集开关 `COLLECTOR__ENABLE_SEARCH`
- 专利采集开关 `COLLECTOR__ENABLE_PATENT`
- EPO API 配置占位
- 邮件与企业微信配置
- 定时调度配置
- Agent 增强开关

### 新增根目录 `build_index.py`

新增文件：

- `build_index.py`

修正原因：

- README 中写的是 `python build_index.py --reset`，但实际脚本原本位于 `scripts/build_index.py`。

修正方式：

- 根目录新增兼容入口，内部转发到 `scripts/build_index.py`。
- 同时修正 `scripts/build_index.py`，确保直接执行 `python scripts/build_index.py` 时也能导入项目模块。

### 补齐依赖

修改文件：

- `requirements.txt`
- `web_app.py`

新增依赖：

- `PyYAML>=6.0.0`
- `lxml>=5.0.0`

修正原因：

- `processors/rag.py` 使用 `yaml`。
- `collectors/base.py` 使用 `BeautifulSoup(..., 'lxml')`。
- 原依赖文件没有显式声明这两个包。

## 2. 多源采集功能修正

### 搜索采集恢复接入主流程

修改文件：

- `config.py`
- `main.py`

修正前：

- `SearchCollector` 虽然存在，但在 `main.py` 中被注释，完整流程不会执行搜索采集。

修正后：

- 新增配置项 `COLLECTOR__ENABLE_SEARCH`。
- 默认启用搜索采集。
- `main.py` 根据配置动态加入 `SearchCollector()`。

### 新增专利采集器

新增文件：

- `collectors/patent_collector.py`

修改文件：

- `collectors/__init__.py`
- `config.py`
- `main.py`

实现内容：

- 新增 `PatentCollector`。
- 当前版本通过公开搜索页面采集 Google Patents 和 Espacenet 的专利线索。
- 输出统一为 `RawIntelData`。
- 使用现有关键词过滤逻辑筛选通信设备相关专利线索。

说明：

- `config.py` 中保留了 EPO Key/Secret 字段。
- 本次实现先补齐 README 中“专利数据等”的可用采集入口；后续可在同一采集器中扩展 EPO OPS API 的正式认证调用。

## 3. AI分析与原始数据留存

### 新增原始采集数据表

修改文件：

- `database.py`
- `processors/analyzer.py`

新增表：

- `raw_intel_items`

用途：

- 保存采集到的原始标题、URL、来源、摘要、正文。
- 记录分析状态：`pending`、`analyzed`、`failed`、`skipped_duplicate`、`skipped_duplicate_title`。
- 分析失败时保留错误原因，便于后续重试和排查。

修正原因：

- 原流程中，只有 LLM 分析成功后的数据才进入 `intel_items`，分析失败会导致原始采集数据丢失。

## 4. 产业链周报修正

### 补齐产业链字段入库

修改文件：

- `database.py`

新增/迁移字段：

- `supply_chain`
- `supply_chain_segment`
- `subsector_type`

修正原因：

- `models.IntelItem` 和 LLM Prompt 已经包含产业链字段，但数据库没有保存这些字段。
- 周报生成时从数据库读取数据，字段缺失会导致产业链分组能力失效。

兼容处理：

- `_init_db()` 中增加旧库迁移逻辑，对已存在的 `intel_items` 表自动补列。

### 新增产业链配置文件

新增文件：

- `knowledge_base/supply_chain_config.yaml`

修正原因：

- `reporters/supply_chain_report.py` 依赖该文件，但项目原本缺失。

新增产业链结构：

- 芯片与半导体
- 光通信器件与模块
- 无线接入设备
- 光传输与接入
- 核心网与数据中心
- 物联网与终端
- 电信运营与基础设施
- 其他

### 修正配置文件路径

修改文件：

- `reporters/supply_chain_report.py`

修正内容：

- 从相对路径 `knowledge_base/supply_chain_config.yaml` 改为基于 `settings.knowledge_base_dir` 的绝对项目路径，减少工作目录变化导致的加载失败。

## 5. RAG / 向量数据库修正

### 接入 ChromaDB 持久化索引

修改文件：

- `processors/rag.py`

修正前：

- requirements 中声明了 `chromadb`，配置里也有 `vector_db_path`，但代码没有实际使用 ChromaDB。
- 原实现只使用 `sentence-transformers` 生成内存向量，并手动计算余弦相似度。

修正后：

- 优先使用 ChromaDB `PersistentClient`。
- 持久化目录为 `knowledge_base/chroma_db`。
- collection 名称为 `technical_knowledge`。
- 将 `technical_keywords.yaml` 中的知识片段写入 ChromaDB。
- 查询时优先使用 ChromaDB。
- 如果 ChromaDB 或 embedding 模型不可用，自动退回内存向量检索或关键词检索。

### 修正 RAG 工具调用参数

修改文件：

- `processors/rag.py`

修正内容：

- `get_context_for_analysis()` 新增可选参数 `top_k`。

修正原因：

- `processors/agent_tools.py` 中调用了 `get_context_for_analysis(topic, top_k=3)`，旧方法签名不支持该参数。

## 6. 分发功能修正

修改文件：

- `main.py`

修正前：

- `Distributor.distribute_report(report)` 被注释。
- 主流程固定返回 `{'email': False, 'wechat': False}`。

修正后：

- 恢复调用 `await self.distributor.distribute_report(report)`。
- 是否真正发送仍由 `.env` 中的 `DISTRIBUTION__ENABLE_EMAIL` 和 `DISTRIBUTION__ENABLE_WECHAT` 控制。

## 7. ReAct 工具链修正

修改文件：

- `database.py`
- `processors/rag.py`

修正内容：

- 新增 `Database.get_items_by_company()`，供 `AgentTools.search_recent_news()` 调用。
- `get_context_for_analysis()` 支持 `top_k` 参数。

修正原因：

- 原 `agent_tools.py` 调用的方法在数据库层不存在，启用 ReAct 后会报错。

## 8. Claude API 消息格式修正

修改文件：

- `llm.py`

修正内容：

- Claude 调用时，将 system prompt 从 messages 中拆出，放到 Anthropic API 的顶层 `system` 字段。
- 用户/助手消息保留在 `messages` 中。

修正原因：

- Claude API 不使用 OpenAI 兼容的 system role 格式，旧实现可能导致 Claude fallback 失败。

## 9. Web界面依赖检测修正

修改文件：

- `web_app.py`

修正内容：

- 依赖检测增加 `PyYAML` 和 `lxml`。

## 10. 本次涉及文件清单

新增文件：

- `.env.example`
- `build_index.py`
- `collectors/patent_collector.py`
- `knowledge_base/supply_chain_config.yaml`
- `docs/UPDATE_2026-05-14_FUNCTION_FIXES.md`

修改文件：

- `requirements.txt`
- `config.py`
- `main.py`
- `database.py`
- `llm.py`
- `web_app.py`
- `collectors/__init__.py`
- `processors/analyzer.py`
- `processors/rag.py`
- `reporters/supply_chain_report.py`
- `scripts/build_index.py`
- `docs/README.md`

## 11. 验证说明

当前执行环境缺少可用 Python：

- `python` 不在 PATH。
- `py` 启动器存在，但提示没有安装 Python。

因此本次无法在当前环境完成以下命令的实际运行验证：

```bash
python main.py --test
python build_index.py --show
python main.py --report
streamlit run web_app.py --server.port 8501
```

安装 Python 并执行 `pip install -r requirements.txt` 后，建议按以下顺序验证：

```bash
python main.py --test
python build_index.py --show
python build_index.py --reset
python main.py --report
python main.py --collect
streamlit run web_app.py --server.port 8501
```

如未配置 LLM API Key，`--collect` 可以采集原始数据，但 AI 分析会失败并记录到 `raw_intel_items.analysis_status = failed`。

## 12. 后续建议

本次修正重点是让 README 描述的功能在代码层闭环。后续建议继续做：

1. 将关键词、公司、采集源迁移到数据库和 Web 配置页。
2. 为 `PatentCollector` 接入正式 EPO OPS API。
3. 为采集任务增加后台队列，避免 Streamlit 页面阻塞。
4. 增加 pytest 测试套件。
5. 将 SQLite schema 迁移逻辑升级为正式 migration。

## 13. 2026-05-14 启动验证补充

本轮已完成本机启动验证。

### Python 与依赖安装

原始环境问题：

- `python` 不在 PATH。
- `py` 启动器存在，但提示没有安装 Python。

处理结果：

- 已下载 Python 3.11.9 官方 Windows 安装包。
- Python 实际安装位置：
  - `C:\Users\chend\AppData\Local\Programs\Python\Python311\python.exe`
- 已执行：

```bash
python -m pip install -r requirements.txt
python -m playwright install chromium
```

### 语法检查

已执行 `py_compile` 检查，覆盖主入口、采集器、处理器、报告器和 Web 页面，结果通过。

### 配置检查

已执行：

```bash
python main.py --test
```

结果：

- 数据库初始化成功。
- 启用采集器：`rss, web, search, patent`。
- RSS 源：16 个。
- 监控公司：203 家。
- RAG 系统已初始化。
- ChromaDB 持久化索引已写入：
  - `knowledge_base/chroma_db`

当前限制：

- 未配置任何 LLM API Key，因此 AI 分析不可用。
- 邮件和企业微信均未配置。

### 知识库命令验证

已执行：

```bash
python build_index.py --show
```

首次运行发现 Windows 控制台编码问题：脚本输出 emoji 时，GBK 控制台抛出 `UnicodeEncodeError`。

已修复文件：

- `scripts/build_index.py`

修复方式：

- 将脚本输出中的 emoji 替换为纯文本，避免 Windows GBK 控制台报错。

修复后 `python build_index.py --show` 已成功输出知识库内容概览。

### 周报生成验证

已执行：

```bash
python main.py --report
```

结果：

- 成功生成第 16 期周报。
- 输出文件：
  - `data/reports/weekly_report_20260514_16.md`
  - `data/reports/weekly_report_20260514_16.html`

说明：

- 当前由于没有新的可分析情报，报告条目数为 0。
- 分发流程已执行，但因邮件/企微未配置，结果为 `False`，属于预期。

### Web 页面启动验证

已后台启动：

```bash
python -m streamlit run web_app.py --server.port 8501 --server.headless true
```

验证结果：

- `http://localhost:8501` 返回 `200 OK`。
- Web 页面服务已启动。

### 数据库结构验证

已确认：

- `intel_items` 表包含：
  - `supply_chain`
  - `supply_chain_segment`
  - `subsector_type`
- `raw_intel_items` 表已创建，包含原始采集数据和分析状态字段。

### 当前可访问地址

Web 页面：

```text
http://localhost:8501
```

### 下一步必须配置

若要看到完整“采集 -> AI分析 -> 入库 -> 周报”的真实效果，需要在 `.env` 中至少配置一个 LLM Key：

```env
LLM__DEEPSEEK_API_KEY=你的key
```

配置后重新执行：

```bash
python main.py --collect
python main.py --report
```

## 2026-05-14 识微商情/VviHot采集器接入

### 新增能力

- 新增 `collectors/vvihot_collector.py`。
- 支持登录识微商情平台并采集已配置监测主题下的文章。
- 平台文章会统一转换为 `RawIntelData`，复用现有 LLM 分析、去重、入库和周报流程。
- 启用 `COLLECTOR__ENABLE_VVIHOT=true` 后，主流程会使用 `VviHotCollector` 替代原来的 `SearchCollector`，避免重复跑 Bing 搜索。

### 新增配置

```env
COLLECTOR__ENABLE_VVIHOT=true
COLLECTOR__VVIHOT_URL=https://zreywc.vvihot.com/swsq/
COLLECTOR__VVIHOT_USERNAME=
COLLECTOR__VVIHOT_PASSWORD=
COLLECTOR__VVIHOT_HEADLESS=true
COLLECTOR__VVIHOT_WAIT_SECONDS=12
COLLECTOR__VVIHOT_MAX_ITEMS=80
COLLECTOR__VVIHOT_TOPIC_NAMES=
```

### 文档

- 新增 `docs/VVIHOT_COLLECTOR_INTEGRATION.md`，说明平台字段映射、替代范围、主题组合建议和使用注意事项。
