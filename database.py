"""
数据库操作模块 - SQLite数据库管理
"""
import sqlite3
import json
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Tuple
from pathlib import Path
from contextlib import contextmanager

from loguru import logger

from config import settings
from models import (
    IntelItem,
    WeeklyReport,
    Category,
    Industry,
    TechDomain,
    ActionType,
    NewsFreshness,
    RawIntelData,
)


class Database:
    """SQLite数据库管理类"""
    
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or str(settings.data_dir / "intel.db")
        self._init_db()
    
    @contextmanager
    def _get_connection(self):
        """获取数据库连接上下文管理器"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def _init_db(self):
        """初始化数据库表结构"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # 创建情报条目表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS intel_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    source_url TEXT UNIQUE NOT NULL,
                    source_name TEXT,
                    source_type TEXT,
                    pub_date TEXT,
                    content TEXT,
                    category TEXT,
                    industry TEXT,
                    tech_domain TEXT,
                    action_type TEXT,
                    importance INTEGER DEFAULT 3,
                    decision_value INTEGER DEFAULT 0,
                    is_news INTEGER DEFAULT 1,
                    news_freshness TEXT DEFAULT 'current',
                    summary_zh TEXT,
                    one_line_insight TEXT,
                    tags TEXT,
                    companies TEXT,
                    supply_chain TEXT,
                    supply_chain_segment TEXT,
                    subsector_type TEXT,
                    rag_triggered INTEGER DEFAULT 0,
                    rag_context TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT
                )
            """)

            # 兼容旧数据库：CREATE TABLE IF NOT EXISTS 不会补新增列。
            for column_sql in [
                "ALTER TABLE intel_items ADD COLUMN supply_chain TEXT",
                "ALTER TABLE intel_items ADD COLUMN supply_chain_segment TEXT",
                "ALTER TABLE intel_items ADD COLUMN subsector_type TEXT",
            ]:
                try:
                    cursor.execute(column_sql)
                except sqlite3.OperationalError:
                    pass

            # 创建原始采集数据表，用于追溯和失败重试
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS raw_intel_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    url TEXT UNIQUE NOT NULL,
                    source TEXT,
                    source_type TEXT,
                    pub_date TEXT,
                    content TEXT,
                    summary TEXT,
                    analysis_status TEXT DEFAULT 'pending',
                    analysis_error TEXT,
                    analyzed_item_id INTEGER,
                    collected_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT
                )
            """)
            
            # 创建周报表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS weekly_reports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    issue_no INTEGER UNIQUE NOT NULL,
                    date_start TEXT NOT NULL,
                    date_end TEXT NOT NULL,
                    report_md TEXT,
                    report_html TEXT,
                    sent_email INTEGER DEFAULT 0,
                    sent_wechat INTEGER DEFAULT 0,
                    sent_at TEXT,
                    total_items INTEGER DEFAULT 0,
                    importance_distribution TEXT,
                    category_distribution TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 创建索引
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_intel_items_date 
                ON intel_items(pub_date)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_intel_items_category 
                ON intel_items(category)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_intel_items_importance 
                ON intel_items(importance)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_intel_items_created 
                ON intel_items(created_at)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_raw_items_status
                ON raw_intel_items(analysis_status)
            """)
            
            conn.commit()
            logger.info(f"数据库初始化完成: {self.db_path}")
    
    def save_intel_item(self, item: IntelItem) -> bool:
        """保存情报条目，如果URL已存在则更新"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # 检查是否已存在
                cursor.execute(
                    "SELECT id FROM intel_items WHERE source_url = ?",
                    (item.source_url,)
                )
                existing = cursor.fetchone()
                
                item_data = {
                    'title': item.title,
                    'source_url': item.source_url,
                    'source_name': item.source_name,
                    'source_type': item.source_type,
                    'pub_date': item.pub_date.isoformat() if item.pub_date else None,
                    'content': item.content,
                    'category': item.category.value if item.category else None,
                    'industry': item.industry.value if item.industry else None,
                    'tech_domain': item.tech_domain.value if item.tech_domain else None,
                    'action_type': item.action_type.value if item.action_type else None,
                    'importance': item.importance,
                    'decision_value': 1 if item.decision_value else 0,
                    'is_news': 1 if item.is_news else 0,
                    'news_freshness': item.news_freshness.value if item.news_freshness else 'current',
                    'summary_zh': item.summary_zh,
                    'one_line_insight': item.one_line_insight,
                    'tags': json.dumps(item.tags, ensure_ascii=False),
                    'companies': json.dumps(item.companies_mentioned, ensure_ascii=False),
                    'supply_chain': item.supply_chain,
                    'supply_chain_segment': item.supply_chain_segment,
                    'subsector_type': item.subsector_type,
                    'rag_triggered': 1 if item.rag_triggered else 0,
                    'rag_context': item.rag_context,
                    'updated_at': datetime.now().isoformat()
                }
                
                if existing:
                    # 更新
                    set_clause = ', '.join([f"{k} = ?" for k in item_data.keys()])
                    values = list(item_data.values())
                    cursor.execute(
                        f"UPDATE intel_items SET {set_clause} WHERE source_url = ?",
                        values + [item.source_url]
                    )
                    logger.debug(f"更新情报条目: {item.title[:50]}...")
                else:
                    # 插入
                    columns = ', '.join(item_data.keys())
                    placeholders = ', '.join(['?' for _ in item_data])
                    cursor.execute(
                        f"INSERT INTO intel_items ({columns}) VALUES ({placeholders})",
                        list(item_data.values())
                    )
                    logger.debug(f"新增情报条目: {item.title[:50]}...")
                
                conn.commit()
                return True
                
        except Exception as e:
            logger.error(f"保存情报条目失败: {e}")
            return False

    def save_raw_intel_data(self, raw_data: RawIntelData, status: str = "pending", error: str = "") -> bool:
        """保存原始采集数据，已存在则更新状态和内容"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO raw_intel_items (
                        title, url, source, source_type, pub_date, content, summary,
                        analysis_status, analysis_error, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(url) DO UPDATE SET
                        title = excluded.title,
                        source = excluded.source,
                        source_type = excluded.source_type,
                        pub_date = excluded.pub_date,
                        content = excluded.content,
                        summary = excluded.summary,
                        analysis_status = excluded.analysis_status,
                        analysis_error = excluded.analysis_error,
                        updated_at = excluded.updated_at
                """, (
                    raw_data.title,
                    raw_data.url,
                    raw_data.source,
                    raw_data.source_type,
                    raw_data.pub_date.isoformat() if raw_data.pub_date else None,
                    raw_data.content,
                    raw_data.summary,
                    status,
                    error,
                    datetime.now().isoformat()
                ))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"保存原始采集数据失败: {e}")
            return False

    def update_raw_analysis_status(
        self,
        url: str,
        status: str,
        error: str = "",
        analyzed_item_id: Optional[int] = None
    ) -> bool:
        """更新原始数据分析状态"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE raw_intel_items
                    SET analysis_status = ?, analysis_error = ?, analyzed_item_id = ?,
                        updated_at = ?
                    WHERE url = ?
                """, (status, error, analyzed_item_id, datetime.now().isoformat(), url))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"更新原始数据分析状态失败: {e}")
            return False
    
    def get_intel_item_by_url(self, url: str) -> Optional[IntelItem]:
        """通过URL获取情报条目"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT * FROM intel_items WHERE source_url = ?",
                    (url,)
                )
                row = cursor.fetchone()
                
                if row:
                    return self._row_to_intel_item(row)
                return None
                
        except Exception as e:
            logger.error(f"获取情报条目失败: {e}")
            return None
    
    def check_url_exists(self, url: str) -> bool:
        """检查URL是否已存在"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT 1 FROM intel_items WHERE source_url = ? LIMIT 1",
                    (url,)
                )
                return cursor.fetchone() is not None
        except Exception as e:
            logger.error(f"检查URL存在失败: {e}")
            return False

    def get_items_by_company(self, company: str, days: int = 30, limit: int = 20) -> List[IntelItem]:
        """按公司名查询最近情报，供Agent工具调用"""
        try:
            start_date = (datetime.now() - timedelta(days=days)).isoformat()
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM intel_items
                    WHERE created_at >= ?
                      AND (companies LIKE ? OR title LIKE ? OR content LIKE ?)
                    ORDER BY importance DESC, COALESCE(pub_date, created_at) DESC
                    LIMIT ?
                """, (
                    start_date,
                    f"%{company}%",
                    f"%{company}%",
                    f"%{company}%",
                    limit
                ))
                return [self._row_to_intel_item(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"按公司查询情报失败: {e}")
            return []
    
    def get_intel_items(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        days: Optional[int] = None,
        category: Optional[str] = None,
        min_importance: Optional[int] = None,
        decision_value_only: bool = False,
        limit: Optional[int] = None,
        offset: int = 0
    ) -> List[IntelItem]:
        """查询情报条目列表
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
            days: 最近N天（与start_date互斥，优先使用days）
            category: 分类筛选
            min_importance: 最小重要性
            decision_value_only: 仅决策价值
            limit: 限制数量
            offset: 偏移量
        """
        try:
            # 如果指定了days，计算start_date
            if days is not None:
                start_date = datetime.now() - timedelta(days=days)
            
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                query = "SELECT * FROM intel_items WHERE 1=1"
                params = []
                
                if start_date:
                    query += " AND pub_date >= ?"
                    params.append(start_date.isoformat())
                
                if end_date:
                    query += " AND pub_date <= ?"
                    params.append(end_date.isoformat())
                
                if category:
                    query += " AND category = ?"
                    params.append(category)
                
                if min_importance:
                    query += " AND importance >= ?"
                    params.append(min_importance)
                
                if decision_value_only:
                    query += " AND decision_value = 1"
                
                query += " ORDER BY pub_date DESC, importance DESC"
                
                if limit:
                    query += f" LIMIT {limit} OFFSET {offset}"
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                return [self._row_to_intel_item(row) for row in rows]
                
        except Exception as e:
            logger.error(f"查询情报条目失败: {e}")
            return []
    
    def get_items_for_report(
        self,
        days: int = 7,
        min_importance: int = 3,
        max_items: int = 9999,
        max_per_company: int = 5
    ) -> List[IntelItem]:
        """获取用于生成周报的情报条目

        过滤规则：
        - 7天内的数据
        - importance >= 3 且 decision_value=true，或 importance >= 4
        - is_news=true (排除背景介绍)
        - 每公司最多5条
        """
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                query = """
                    SELECT * FROM intel_items
                    WHERE (
                        (pub_date >= ? AND pub_date <= ?)
                        OR (pub_date IS NULL AND created_at >= ? AND created_at <= ?)
                    )
                    AND is_news = 1
                    AND (
                        (importance >= ? AND decision_value = 1)
                        OR importance >= 4
                    )
                    ORDER BY importance DESC, COALESCE(pub_date, created_at) DESC
                """
                cursor.execute(query, (
                    start_date.isoformat(), end_date.isoformat(),
                    start_date.isoformat(), end_date.isoformat(),
                    min_importance
                ))
                rows = cursor.fetchall()
                
                items = [self._row_to_intel_item(row) for row in rows]
                
                # 按公司限制数量
                company_count = {}
                filtered_items = []
                
                for item in items:
                    companies = item.companies_mentioned or ['其他']
                    primary_company = companies[0] if companies else '其他'
                    
                    if company_count.get(primary_company, 0) < max_per_company:
                        filtered_items.append(item)
                        company_count[primary_company] = company_count.get(primary_company, 0) + 1
                    
                    if len(filtered_items) >= max_items:
                        break
                
                return filtered_items
                
        except Exception as e:
            logger.error(f"获取周报数据失败: {e}")
            return []
    
    def save_weekly_report(self, report: WeeklyReport) -> bool:
        """保存周报"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT OR REPLACE INTO weekly_reports (
                        issue_no, date_start, date_end, report_md, report_html,
                        sent_email, sent_wechat, sent_at, total_items,
                        importance_distribution, category_distribution
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    report.issue_no,
                    report.date_start.isoformat(),
                    report.date_end.isoformat(),
                    report.report_md,
                    report.report_html,
                    1 if report.sent_email else 0,
                    1 if report.sent_wechat else 0,
                    report.sent_at.isoformat() if report.sent_at else None,
                    report.total_items,
                    json.dumps(report.importance_distribution, ensure_ascii=False),
                    json.dumps(report.category_distribution, ensure_ascii=False)
                ))
                
                conn.commit()
                logger.info(f"保存周报成功: 第{report.issue_no}期")
                return True
                
        except Exception as e:
            logger.error(f"保存周报失败: {e}")
            return False
    
    def get_latest_issue_no(self) -> int:
        """获取最新的期号"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT MAX(issue_no) FROM weekly_reports")
                result = cursor.fetchone()
                return (result[0] or 0) + 1
        except Exception as e:
            logger.error(f"获取最新期号失败: {e}")
            return 1

    def get_latest_weekly_report(self) -> Optional[WeeklyReport]:
        """获取最新的周报"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM weekly_reports
                    ORDER BY issue_no DESC
                    LIMIT 1
                """)
                row = cursor.fetchone()

                if not row:
                    return None

                # 转换为WeeklyReport对象
                return WeeklyReport(
                    issue_no=row['issue_no'],
                    date_start=datetime.fromisoformat(row['date_start']),
                    date_end=datetime.fromisoformat(row['date_end']),
                    report_md=row['report_md'],
                    report_html=row['report_html'],
                    total_items=row['total_items'],
                    sent_email=bool(row['sent_email']),
                    sent_wechat=bool(row['sent_wechat']),
                    sent_at=datetime.fromisoformat(row['sent_at']) if row['sent_at'] else None,
                    importance_distribution=json.loads(row['importance_distribution']) if row['importance_distribution'] else {},
                    category_distribution=json.loads(row['category_distribution']) if row['category_distribution'] else {}
                )
        except Exception as e:
            logger.error(f"获取最新周报失败: {e}")
            return None

    def get_statistics(self, days: int = 7) -> Dict[str, Any]:
        """获取统计信息"""
        try:
            start_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # 总数
                cursor.execute(
                    "SELECT COUNT(*) FROM intel_items WHERE created_at >= ?",
                    (start_date,)
                )
                total = cursor.fetchone()[0]
                
                # 分类统计
                cursor.execute("""
                    SELECT category, COUNT(*) FROM intel_items 
                    WHERE created_at >= ? AND category IS NOT NULL
                    GROUP BY category
                """, (start_date,))
                category_stats = {row[0]: row[1] for row in cursor.fetchall()}
                
                # 重要性分布
                cursor.execute("""
                    SELECT importance, COUNT(*) FROM intel_items 
                    WHERE created_at >= ?
                    GROUP BY importance
                """, (start_date,))
                importance_stats = {f"{row[0]}分": row[1] for row in cursor.fetchall()}
                
                # 来源类型统计
                cursor.execute("""
                    SELECT source_type, COUNT(*) FROM intel_items 
                    WHERE created_at >= ? AND source_type IS NOT NULL
                    GROUP BY source_type
                """, (start_date,))
                source_stats = {row[0]: row[1] for row in cursor.fetchall()}
                
                return {
                    "total_items": total,
                    "category_distribution": category_stats,
                    "importance_distribution": importance_stats,
                    "source_distribution": source_stats
                }
                
        except Exception as e:
            logger.error(f"获取统计信息失败: {e}")
            return {}
    
    def _row_to_intel_item(self, row: sqlite3.Row) -> IntelItem:
        """将数据库行转换为IntelItem对象"""
        data = dict(row)
        
        # 处理JSON字段
        tags = json.loads(data.get('tags', '[]')) if data.get('tags') else []
        companies = json.loads(data.get('companies', '[]')) if data.get('companies') else []
        
        # 处理枚举字段
        category = Category(data['category']) if data.get('category') else None
        industry = Industry(data['industry']) if data.get('industry') else None
        tech_domain = TechDomain(data['tech_domain']) if data.get('tech_domain') else None
        
        try:
            action_type = ActionType(data['action_type']) if data.get('action_type') else None
        except ValueError:
            action_type = ActionType.OTHER

        try:
            news_freshness = NewsFreshness(data['news_freshness']) if data.get('news_freshness') else NewsFreshness.CURRENT
        except ValueError:
            news_freshness = NewsFreshness.CURRENT

        return IntelItem(
            id=data.get('id'),
            title=data.get('title', ''),
            source_url=data.get('source_url', ''),
            source_name=data.get('source_name', ''),
            source_type=data.get('source_type', ''),
            pub_date=datetime.fromisoformat(data['pub_date']) if data.get('pub_date') else None,
            content=data.get('content', ''),
            category=category,
            industry=industry,
            tech_domain=tech_domain,
            action_type=action_type,
            importance=data.get('importance', 3),
            decision_value=bool(data.get('decision_value', 0)),
            is_news=bool(data.get('is_news', 1)),
            news_freshness=news_freshness,
            summary_zh=data.get('summary_zh', ''),
            one_line_insight=data.get('one_line_insight', ''),
            tags=tags,
            companies_mentioned=companies,
            supply_chain=data.get('supply_chain'),
            supply_chain_segment=data.get('supply_chain_segment'),
            subsector_type=data.get('subsector_type'),
            rag_triggered=bool(data.get('rag_triggered', 0)),
            rag_context=data.get('rag_context', ''),
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else datetime.now(),
            updated_at=datetime.fromisoformat(data['updated_at']) if data.get('updated_at') else None
        )


# 全局数据库实例
db = Database()
