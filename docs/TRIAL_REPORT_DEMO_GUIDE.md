# 官网试用版报告接入说明书

## 1. 功能定位

这个试用版不是给访客实时采集全网数据，而是基于系统每周已经采集、分析、入库的情报数据，按访客选择的周次和技术方向生成一份有限预览。

这样可以做到：

- 官网访问速度快，通常几秒内出结果。
- 不会因为每个访客点击而消耗 Serper、Jina、DeepSeek 等接口费用。
- 试用内容稳定，可提前审核。
- 末尾自动引导访客联系销售或咨询顾问获取完整报告。

## 2. 新增文件

- `trial_report_service.py`：试用报告服务层，负责读取数据库、筛选方向、生成 Markdown/HTML 预览。
- `trial_demo_app.py`：面向官网试用的 Streamlit 页面。
- `docs/TRIAL_REPORT_DEMO_GUIDE.md`：本说明书。

## 3. 数据来源

试用版读取本项目数据库：

```text
data/intel.db
```

主要使用两张表：

- `weekly_reports`：获取最近三期周报、期号和日期范围。
- `intel_items`：获取该日期范围内的情报条目，并按技术方向筛选。

技术方向的判断优先级：

1. 优先使用 `supply_chain` 字段，例如“光通信器件与模块”“无线接入设备”“芯片与半导体”。
2. 如果 `supply_chain` 为空或为“其他”，则使用 `tech_domain` 字段，例如“光通信”“无线通信”“终端设备”。
3. 如果仍无法判断，则归入“综合技术动态”。

## 4. 使用前准备

先在主系统里完成一次完整流程：

```bash
python main.py
```

或者通过主 Web 页面点击“开始采集”，确保已经生成周报，并且 `data/intel.db` 中有数据。

建议每周固定运行一次采集任务，把最新周报沉淀到数据库里。官网试用页只读取这些已生成的数据。

## 5. 配置联系方式

在 `.env` 里增加以下配置：

```env
TRIAL__CONTACT_NAME=薄云咨询产业情报团队
TRIAL__CONTACT_PHONE=填写联系电话
TRIAL__CONTACT_WECHAT=填写微信号
TRIAL__CONTACT_EMAIL=填写邮箱
```

这些内容会显示在试用报告末尾，用于引导访客咨询完整报告和定制监测。

## 6. 本地启动试用页

在项目根目录执行：

```bash
streamlit run trial_demo_app.py --server.port 8502
```

浏览器访问：

```text
http://localhost:8502
```

页面支持：

- 选择最近三期中的任意一期。
- 多选技术方向。
- 选择预览条数。
- 生成试用版报告预览。
- 在末尾展示完整报告咨询方式。

## 7. 接入公司官网的方式

### 方式一：iframe 嵌入

这是最快的接入方式。把 `trial_demo_app.py` 部署到服务器，例如：

```text
https://ai.yourcompany.com/trial-report
```

然后在公司官网页面中嵌入：

```html
<iframe
  src="https://ai.yourcompany.com/trial-report"
  style="width: 100%; height: 1100px; border: 0;"
  loading="lazy">
</iframe>
```

适合快速上线试用版。

### 方式二：官网前端调用服务层

如果官网已有自己的前端和后端，可以复用 `trial_report_service.py` 中的函数：

```python
from trial_report_service import get_recent_weeks, get_available_directions, build_trial_report

weeks = get_recent_weeks(3)
directions = get_available_directions(issue_no=weeks[0].issue_no)
report = build_trial_report(
    issue_no=weeks[0].issue_no,
    directions=directions[:2],
    max_total=8,
)
```

返回结果中：

- `report["markdown"]`：Markdown 版本。
- `report["html"]`：HTML 版本。
- `report["items_count"]`：本次展示条数。

官网后端可以把这些内容包装成自己的 API 返回给官网前端。

## 8. 推荐上线架构

建议采用以下流程：

```text
每周定时采集
  -> AI分析
  -> 生成周报
  -> 入库 data/intel.db
  -> 官网试用页读取数据库
  -> 访客选择周次和方向
  -> 返回试用版预览
  -> 引导联系销售/顾问
```

试用页不要直接触发采集和 AI 分析。采集、分析、生成周报应该由后台固定任务完成。

## 9. 试用版展示限制

当前默认限制：

- 只展示最近三期周报。
- 默认最多展示 8 条情报。
- 每个技术方向默认最多展示 3 条。
- 不展示完整报告中的全部来源链接和深度分析。

可以在 `trial_demo_app.py` 中调整：

```python
max_total = st.selectbox("预览条数", [6, 8, 10, 12], index=1)
```

也可以在调用 `build_trial_report()` 时调整：

```python
build_trial_report(issue_no, directions, max_total=10, max_per_direction=3)
```

## 10. 商业化建议

官网试用版建议只展示“样例价值”，不要把完整内容一次性开放。

推荐保留到付费版本中的内容：

- 完整报告全文。
- 全量原文链接。
- 竞品公司持续监测。
- 专利线索完整清单。
- 按客户自定义关键词采集。
- 企业微信和邮箱定时推送。
- 定制技术方向和人工审核版本。

## 11. 常见问题

### 试用页没有周报可选

说明 `data/intel.db` 中还没有周报数据。先运行主系统采集并生成周报。

### 技术方向为空或很少

说明历史情报中的 `supply_chain` 或 `tech_domain` 字段不完整。需要先保证 AI 分析阶段正常运行，并且分析结果成功入库。

### 能不能让访客以为是实时生成

建议表述为“基于已监测的产业情报库生成试用报告”。不要写成“正在实时全网采集”，这样更稳，也避免误导。

### 是否会消耗 API

试用页本身不会调用 Serper、Jina 或 DeepSeek。只有后台每周采集分析时才会消耗接口。
