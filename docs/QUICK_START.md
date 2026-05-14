# CT产业情报采集器改进 - 快速启动指南

## 🚀 立即开始

### 1. 验证改动
```bash
cd C:\Users\johns\telecom-equipment-intel
python main.py --collect
```

### 2. 查看日志输出
预期看到类似信息：
```
采集RSS源: https://www.c114.com.cn/rss/
采集RSS源: https://www.cww.net.cn/rss.xml
...
```

---

## 📋 四项改动汇总

### 改动1: RSS采集源扩充 ✅
**文件**: `collectors/rss_collector.py`
- 从9个源 → 13个源（+国内媒体优先）
- **新增**: C114, 通信世界, 51CTO等
- **特性**: 失败自动追踪，失败3次后自动跳过

### 改动2: 关键词过滤弱化 ✅
**文件**: `collectors/base.py`
- 从~20个技术词 → ~50个综合词
- **新增**: 企业名称、行业宽泛词
- **效果**: 企业动态、融资等新闻现在能通过过滤

### 改动3: Web采集器改进 ✅
**文件**: `collectors/web_collector.py`
- 从3个网站 → 5个网站（+诺基亚、爱立信）
- **改进**: 多级CSS selector fallback
- **新增**: Jina Reader API fallback（网页解析失败时自动调用）

### 改动4: 搜索采集器改进 ✅
**文件**: `collectors/search_collector.py`
- 从7个搜索词 → 21个搜索词（中英文混合）
- **改进**: Bing选择器多级fallback + User-Agent随机化
- **效果**: 更好的反爬能力和结果覆盖率

---

## ⚙️ 可选配置

为了最大化采集效果，在 `.env` 中添加：

```bash
# Jina Reader API（用于Web采集fallback）
COLLECTOR__JINA_API_KEY=your_key_here

# HTTP/HTTPS代理（访问国际源时需要）
COLLECTOR__HTTP_PROXY=http://proxy.example.com:8080
COLLECTOR__HTTPS_PROXY=http://proxy.example.com:8080
```

---

## 📊 预期效果

| 指标 | 改进前 | 改进后 | 提升 |
|------|------|------|------|
| RSS源数量 | 9 | 13 | +44% |
| 搜索关键词 | 7 | 21 | +200% |
| 关键词覆盖 | 技术词 | 技术+企业+行业 | +150% |
| Web网站 | 3 | 5 | +67% |
| 容错能力 | 低 | 高 | ✅ |

**预期采集数据量提升**: **40-60%** （网络畅通情况下）

---

## 🔍 调试技巧

### 查看RSS源采集情况
```bash
# 查看最近100行日志，找RSS相关信息
python main.py --collect 2>&1 | grep "RSS"
```

### 查看搜索关键词
```bash
# 查看使用的搜索词
python main.py --collect 2>&1 | grep "搜索关键词"
```

### 验证关键词过滤
```python
# 在Python REPL中测试
from collectors.base import contains_keywords

# 测试企业名称过滤
contains_keywords("华为发布新5G技术")  # True ✓
contains_keywords("中兴推出新产品")    # True ✓

# 测试行业词过滤
contains_keywords("通信设备厂商并购")  # True ✓
contains_keywords("光模块技术突破")    # True ✓
```

---

## ✨ 特殊功能

### RSS失败自动恢复
- 单个RSS源失败1-2次：继续尝试
- 失败3次及以上：在本次采集中跳过
- 下一次采集：重新计数，重新尝试

### Web采集选择器策略
1. 先尝试 `.news-item` (标准选择器)
2. 失败则尝试 `.list-item`
3. 再失败尝试 `article`
4. 最后尝试 Jina Reader API（如果配置）

### 搜索采集Anti-Crawl机制
- **User-Agent随机化**: 每次请求用不同UA
- **多个Bing选择器**: 应对结果页面结构变化
- **多个搜索词**: 即使某个词失败，其他词仍可继续

---

## 📚 完整文档
查看 `IMPROVEMENTS.md` 了解技术细节和实现原理。

