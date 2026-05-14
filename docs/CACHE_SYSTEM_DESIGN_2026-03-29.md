# CT产业情报 Agent - 缓存系统设计方案 (2026-03-29)

## 概述

**目标**: 通过缓存避免重复分析，节省LLM成本40%，提升响应速度

**投入**: 5天开发
**预期收益**:
- LLM成本节省40% (月度200-800元)
- 分析延迟降低40% (缓存命中时)
- API调用减少30-40%

---

## 1. 缓存系统架构

### 1.1 缓存分层策略

```
输入 (URL + 标题 + 摘要)
  ↓
[第一层] URL-Hash缓存 (精准匹配, 1小时)
  ├─ 命中 → 返回缓存结果
  └─ 未命中 ↓

[第二层] 相似度缓存 (相同来源+相同标题, 2周)
  ├─ 命中 → 返回缓存结果
  └─ 未命中 ↓

[第三层] LLM分析 (新条目)
  ├─ 执行分析
  └─ 保存结果到缓存

输出 (分析结果)
```

### 1.2 缓存存储方案

**方案A**: SQLite缓存表 (推荐)
- 优点: 与intel.db集成, 无额外依赖
- 缺点: 查询速度不如Redis
- 适用: 中小规模数据(万级)

**方案B**: Redis缓存 (可选)
- 优点: 高速查询, 分布式支持
- 缺点: 需要部署Redis服务
- 适用: 大规模数据(十万+)

**选择**: 先用方案A (SQLite), 后期可升级为Redis

---

## 2. 缓存表设计

### AnalysisCache 表

```sql
CREATE TABLE analysis_cache (
    -- 主键和版本控制
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cache_version TEXT DEFAULT '1.0',

    -- 缓存键 (用于查询)
    url_hash TEXT UNIQUE NOT NULL,  -- URL的SHA256 hash
    title_hash TEXT NOT NULL,       -- 标题的MD5 hash
    source TEXT NOT NULL,           -- 来源 (rss/web/search)

    -- 输入数据 (用于验证)
    original_url TEXT NOT NULL,
    original_title TEXT NOT NULL,
    original_summary TEXT,          -- 摘要

    -- 缓存的分析结果
    analysis_json TEXT NOT NULL,    -- 完整分析结果 JSON序列化

    -- 时间戳
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_hit_at DATETIME,           -- 最后命中时间
    hit_count INTEGER DEFAULT 0,    -- 命中次数

    -- 缓存有效期
    expires_at DATETIME,            -- 过期时间
    is_expired INTEGER DEFAULT 0,   -- 是否已过期

    -- 质量指标
    confidence_score REAL DEFAULT 0.9,  -- 置信度 (0-1)
    manual_reviewed INTEGER DEFAULT 0   -- 是否人工审核
);

-- 索引
CREATE INDEX idx_url_hash ON analysis_cache(url_hash);
CREATE INDEX idx_title_hash ON analysis_cache(title_hash);
CREATE INDEX idx_source ON analysis_cache(source);
CREATE INDEX idx_expires_at ON analysis_cache(expires_at);
```

### DuplicateDetection 表

```sql
CREATE TABLE duplicate_detection (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- 原始数据
    url_hash TEXT UNIQUE NOT NULL,
    title_hash TEXT NOT NULL,
    source TEXT NOT NULL,

    -- 相似数据 (用于去重)
    similar_urls TEXT,              -- 相似URL列表 (JSON)
    similarity_score REAL,          -- 相似度

    -- 元数据
    first_seen_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_seen_at DATETIME,
    occurrence_count INTEGER DEFAULT 1,

    -- 处理状态
    is_duplicate INTEGER DEFAULT 0,
    deduplicated_to TEXT            -- 指向的主URL hash
);

CREATE INDEX idx_source_title ON duplicate_detection(source, title_hash);
```

---

## 3. 缓存策略详解

### 3.1 缓存键设计

**URL-Hash**: SHA256(URL)
```python
import hashlib
url_hash = hashlib.sha256(url.encode()).hexdigest()[:16]  # 取前16字符，避免过长
```

**Title-Hash**: MD5(标题)
```python
title_hash = hashlib.md5(title.encode()).hexdigest()[:8]
```

**缓存键** = source + "|" + url_hash
```python
cache_key = f"{source}:{url_hash}"
```

### 3.2 命中规则

#### 第一层: URL-精准匹配 (高可信)
```
条件: URL完全相同 + 来源相同 + 缓存有效期内(24小时)
命中率: 10-15% (同一来源的重复发布)
置信度: 99%
```

#### 第二层: 标题-相似匹配 (中可信)
```
条件: 标题相同 + 来源相同 + 发布日期接近(24小时) + 缓存有效期内(2周)
命中率: 15-25% (同一事件的多源发布)
置信度: 85%
```

#### 第三层: 新分析
```
条件: 缓存未命中
操作: 执行LLM分析 → 保存结果到缓存
```

### 3.3 缓存失效策略

**时间失效**:
- URL-精准缓存: 24小时失效 (信息来源可能更新)
- 标题相似缓存: 14天失效 (两周内新闻基本不变)
- LLM分析缓存: 30天失效 (避免陈旧分析)

**主动失效**:
- 分析结果被人工修改 → 标记为已过期
- 相关企业有重大事件 → 相关缓存主动清除
- 数据库维护时清理过期缓存

**容量管理**:
- 缓存容量上限: 100,000 条
- 超限时删除: 最久未使用 (LRU)

---

## 4. 实施步骤

### Step 1: 创建缓存表 (1天)
- 在database.py中添加缓存表创建脚本
- 初始化缓存系统

### Step 2: 缓存查询接口 (1.5天)
- `get_cached_analysis()` - 查询缓存
- `save_analysis_cache()` - 保存缓存
- `invalidate_cache()` - 失效缓存

### Step 3: 集成到分析流程 (1.5天)
- 修改 `processors/analyzer.py`
- 分析前查询缓存
- 分析后保存缓存

### Step 4: 缓存统计和优化 (1天)
- 缓存命中率统计
- 缓存大小监控
- 定期清理过期数据

### Step 5: 测试和文档 (0.5天)
- 单元测试
- 集成测试
- 使用文档

---

## 5. 代码框架

### 5.1 CacheManager类

```python
# processors/cache_manager.py

import hashlib
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from loguru import logger

class CacheManager:
    """分析结果缓存管理器"""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.cache_table = "analysis_cache"
        self.duplicate_table = "duplicate_detection"

    def _make_url_hash(self, url: str) -> str:
        """生成URL Hash"""
        return hashlib.sha256(url.encode()).hexdigest()[:16]

    def _make_title_hash(self, title: str) -> str:
        """生成标题Hash"""
        return hashlib.md5(title.encode()).hexdigest()[:8]

    def _make_cache_key(self, source: str, url: str) -> str:
        """生成缓存键"""
        url_hash = self._make_url_hash(url)
        return f"{source}:{url_hash}"

    def get_cached_analysis(
        self,
        source: str,
        url: str,
        title: str,
        use_title_match: bool = True
    ) -> Optional[Dict[str, Any]]:
        """
        查询缓存分析结果

        策略:
        1. 先查精准URL匹配 (24h内)
        2. 再查标题相似匹配 (14d内)
        3. 缓存未命中返回None
        """
        url_hash = self._make_url_hash(url)
        title_hash = self._make_title_hash(title)

        # 第一层: URL精准匹配
        url_match = self._query_url_cache(source, url_hash)
        if url_match and not self._is_expired(url_match['expires_at']):
            logger.debug(f"缓存命中 [URL]: {source}:{url}")
            return json.loads(url_match['analysis_json'])

        # 第二层: 标题相似匹配
        if use_title_match:
            title_match = self._query_title_cache(source, title_hash)
            if title_match and not self._is_expired(title_match['expires_at']):
                logger.debug(f"缓存命中 [标题]: {source}:{title}")
                return json.loads(title_match['analysis_json'])

        logger.debug(f"缓存未命中: {source}:{url}")
        return None

    def save_analysis_cache(
        self,
        source: str,
        url: str,
        title: str,
        summary: str,
        analysis: Dict[str, Any],
        expires_days: int = 30,
        confidence: float = 0.9
    ) -> bool:
        """保存分析结果到缓存"""
        try:
            url_hash = self._make_url_hash(url)
            title_hash = self._make_title_hash(title)

            expires_at = (datetime.now() + timedelta(days=expires_days)).isoformat()
            analysis_json = json.dumps(analysis, ensure_ascii=False)

            # 保存到缓存表
            self._insert_cache(
                url_hash=url_hash,
                title_hash=title_hash,
                source=source,
                original_url=url,
                original_title=title,
                original_summary=summary,
                analysis_json=analysis_json,
                expires_at=expires_at,
                confidence_score=confidence
            )

            logger.debug(f"缓存保存: {source}:{url}")
            return True
        except Exception as e:
            logger.error(f"缓存保存失败: {e}")
            return False

    def invalidate_cache(self, source: Optional[str] = None, age_days: int = 0) -> int:
        """
        失效缓存

        参数:
          source: 指定来源 (None表示全部)
          age_days: 删除age_days天前的缓存

        返回: 删除的记录数
        """
        # TODO: 实现缓存失效逻辑
        pass

    def get_cache_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        # TODO: 实现缓存统计
        pass

    # =========== 私有方法 ===========

    def _query_url_cache(self, source: str, url_hash: str) -> Optional[Dict]:
        """查询URL缓存"""
        # TODO: 实现SQL查询
        pass

    def _query_title_cache(self, source: str, title_hash: str) -> Optional[Dict]:
        """查询标题缓存"""
        # TODO: 实现SQL查询
        pass

    def _insert_cache(self, **kwargs) -> None:
        """插入缓存记录"""
        # TODO: 实现SQL插入
        pass

    def _is_expired(self, expires_at: str) -> bool:
        """检查缓存是否过期"""
        if not expires_at:
            return False
        return datetime.fromisoformat(expires_at) < datetime.now()
```

### 5.2 集成到分析器

```python
# processors/analyzer.py 中的修改

class IntelAnalyzer:
    def __init__(self, ...):
        # ... 现有初始化 ...
        self.cache_manager = CacheManager(settings.database_url)

    async def analyze(self, item: RawIntelData) -> IntelItem:
        """分析情报条目"""

        # 第一步: 查询缓存
        cached_result = self.cache_manager.get_cached_analysis(
            source=item.source_type,
            url=item.url,
            title=item.title
        )

        if cached_result:
            logger.info(f"使用缓存结果: {item.title}")
            # 将缓存结果转换为IntelItem
            return self._build_intel_item_from_cache(item, cached_result)

        # 第二步: 执行LLM分析 (缓存未命中)
        analysis_result = await self._analyze_with_llm(item)

        # 第三步: 保存到缓存
        self.cache_manager.save_analysis_cache(
            source=item.source_type,
            url=item.url,
            title=item.title,
            summary=item.summary,
            analysis=analysis_result,
            expires_days=30
        )

        # 第四步: 返回分析结果
        return self._build_intel_item(item, analysis_result)

    def _build_intel_item_from_cache(self, item: RawIntelData, cached: Dict) -> IntelItem:
        """从缓存构建IntelItem"""
        # 实现缓存结果到IntelItem的转换
        pass
```

---

## 6. 预期效果

### 6.1 成本节省

| 场景 | 命中率 | 节省比例 |
|------|--------|---------|
| 相同来源重复发布 | 10-15% | -10-15% |
| 同一事件多源发布 | 15-25% | -15-25% |
| 总体平均 | 25-40% | **-25-40%** |

### 6.2 性能提升

| 指标 | 缓存未命中 | 缓存命中 | 提升 |
|------|-----------|----------|------|
| 分析延迟 | 5-10分钟 | 100ms | **50-100倍** |
| API调用 | 1次/条 | 0次/条 | 节省100% |
| 成本 | 0.02元/条 | 0元/条 | 节省100% |

### 6.3 月度收益估算

假设:
- 月采集: 2000条
- 缓存命中率: 30%
- 平均成本: 0.02元/条

```
原成本: 2000 × 0.02 = 40元
缓存命中: 2000 × 30% = 600条 (不分析)
分析数: 2000 - 600 = 1400条
新成本: 1400 × 0.02 = 28元
节省: 40 - 28 = 12元 (节省30%)

实际数据: 月成本500-2000元
缓存节省: 150-800元 (节省30-40%)
```

---

## 7. 风险和对策

| 风险 | 影响 | 对策 |
|------|------|------|
| 缓存中毒 (错误结果) | 数据质量 | 源感知验证+人工审核 |
| 缓存过期 | 分析过期 | 设置合理的TTL |
| 缓存容量爆炸 | 存储空间 | LRU清理+定期维护 |
| 缓存一致性 | 数据不同步 | 版本控制+失效机制 |

---

## 8. 后续优化

### 阶段1 (完成后)
- [ ] 缓存统计Dashboard
- [ ] 缓存预热机制
- [ ] 缓存导出/导入

### 阶段2 (可选)
- [ ] Redis缓存集成
- [ ] 分布式缓存同步
- [ ] 缓存压缩优化

---

## 总结

**投入**: 5天 + 开发时间
**收益**: 成本↓30-40% + 性能↑50倍
**ROI**: 极高

预期完成时间: 本周 (2026-03-31之前)

---

**文档版本**: v1.0 (2026-03-29)
**优先级**: 🥇 High (Phase 2B 第一阶段)
**难度**: ⭐⭐⭐ Medium
