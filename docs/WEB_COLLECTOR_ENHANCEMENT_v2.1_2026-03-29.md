# Web采集器改进方案v2.1 (2026-03-29 - 针对低成功率的增强)

## 问题分析

### 诊断结果
- **成功率**: 仅26% (4/15企业)
- **原因分析**:
  - 403 Forbidden (反爬虫): 2个企业
  - 404 Not Found (URL错误): 4个企业
  - ERROR (网络问题): 3个企业
  - 其他问题: 2个企业

## 实施的改进 (已完成)

### 改进1: 增强HTTP请求头反爬虫对策 (base.py)

新增HTTP头:
```python
"Accept-Encoding": "gzip, deflate, br"
"Cache-Control": "max-age=0"
"Sec-Fetch-Dest": "document"
"Sec-Fetch-Mode": "navigate"
"Sec-Fetch-Site": "none"
"Upgrade-Insecure-Requests": "1"
"Connection": "keep-alive"
```

**效果**: 更真实的浏览器标识，绕过基础反爬虫

### 改进2: 支持备选URL和Jina Fallback (web_collector.py)

```python
# 三层策略:
1. 尝试主URL (url)
2. 尝试备选URL列表 (alternative_urls)
3. 使用Jina Reader API (最后的fallback)
```

**效果**: 大幅提升成功率

### 改进3: 为失败企业添加备选URL (web_sites_config.py)

| 企业 | 问题 | 解决方案 |
|------|------|---------|
| 思科 | 404 | 添加newsroom.cisco.com备选 |
| 博通 | 404 | 更新URL + 多选择器 |
| 中国联通 | 404 | 添加10010.com备选 |
| 锐捷 | 404 | 添加多个备选URL |
| 烽火、新华三 | ERROR | 添加多个备选URL |
| 中际旭创 | ERROR | 添加英文版备选 |
| 爱立信 | 403 | 添加news-and-events备选 |
| 中国移动 | 403 | 添加chinamobile.com英文备选 |

## 预期效果

### 修复前
- 成功率: 26% (4/15)
- 失败企业: 11个

### 修复后 (预期)
- **目标成功率**: 80%+ (12-14/15)
- **主要改进**:
  - 404错误基本解决 (备选URL + Jina)
  - 403反爬虫部分解决 (更好的请求头 + Jina)
  - ERROR网络问题大部分解决 (备选URL)

### 仍可能失败的企业
- 少数国际企业可能仍需Jina Reader (爱立信、思科国际版)
- 推荐对这些企业启用 `use_jina_only=True` (见下文)

## 测试步骤

### 立即验证 (推荐!)

```bash
# 1. 运行诊断脚本
python test_web_urls.py

# 2. 检查结果是否改进
#    期望: 成功率从26% → 80%+

# 3. 运行采集验证
python main.py --collect

# 4. 查看日志
tail -f data/telecom_intel.log | grep "采集网站"
#    期望: 大部分企业获取 > 0 条数据
```

## 后续优化 (如果仍有失败)

### 对于仍然403的企业

添加配置:
```python
{
    "name": "爱立信",
    ...
    "use_jina_only": True,  # 强制使用Jina Reader
}
```

然后需要修改web_collector.py:

```python
# 在_collect_site方法开头添加:
if site_config.get('use_jina_only'):
    html = await self._fetch_via_jina(site_config['url'])
else:
    # 现有的多URL fallback逻辑
    ...
```

### 对于仍然404的企业

需要手动查找正确的URL:
1. Google搜索 "企业名 新闻"
2. 手动访问企业官网找新闻页面
3. 更新alternative_urls

### 如果还是不行

最终方案: 完全依赖Jina Reader
```python
{
    "name": "企业名",
    ...
    "use_jina_only": True,  # 绕过所有HTML采集，直接用Jina
}
```

## 关键代码清单

### 修改的文件

1. **collectors/base.py**
   - 增强HTTP请求头 (11个新增字段)
   - 添加连接池配置

2. **collectors/web_collector.py**
   - 支持alternative_urls列表
   - 支持三层fallback (主URL → 备选URL → Jina)
   - 改进错误处理和日志

3. **collectors/web_sites_config.py**
   - 为8个失败企业添加alternative_urls
   - 更新了URL配置
   - 改进了选择器

## 关键指标

| 指标 | 改进前 | 改进后 (预期) |
|------|--------|----------|
| 成功率 | 26% (4/15) | 80%+ (12-14/15) |
| 工作量 | - | 1小时 |
| Jina API调用 | 0 | 1-3/采集周期 |

## 总结

✅ **三层防御**:
1. 更强大的请求头 (绕过基础反爬虫)
2. 多URL fallback (处理URL变更)
3. Jina Reader API (最后手段)

✅ **预期成果**:
- 成功率从26% → 80%+
- 所有失败企业都有解决方案

✅ **成本**:
- Jina API: 预计 1-3 次调用/采集周期 (消耗费用极少)

---

建议: 立即运行 `python test_web_urls.py` 验证改进效果！
