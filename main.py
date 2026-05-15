"""
CT产业情报Agent - 主入口

用法:
    python main.py              # 立即执行一次（采集+生成报告）
    python main.py --collect    # 仅执行采集分析
    python main.py --report     # 仅生成周报
    python main.py --schedule   # 定时调度模式
"""
import argparse
import asyncio
import sys
from datetime import datetime
from typing import List, Optional

from loguru import logger

# 配置日志
logger.add(
    "data/telecom_intel.log",
    rotation="500 MB",
    retention="30 days",
    level="INFO",
    encoding="utf-8"
)

from config import settings
from collectors import RSSCollector, WebCollector, SearchCollector, PatentCollector, VviHotCollector
from collectors.base import RawIntelData
from processors import IntelAnalyzer, VectorRAG
from processors.episodic_memory import EpisodicMemory
from processors.planning_agent import WeeklyPlanningAgent
from reporters import ReportGenerator, Distributor
from database import db


class TelecomIntelAgent:
    """CT产业情报Agent主类"""

    def __init__(self):
        self.collectors = [
            RSSCollector(),
        ]
        if settings.collector.enable_web:
            self.collectors.append(WebCollector())

        # 识微商情平台可替代原 Bing 搜索采集；启用后避免重复跑 SearchCollector。
        if settings.collector.enable_vvihot:
            self.collectors.append(VviHotCollector())
        elif settings.collector.enable_search:
            self.collectors.append(SearchCollector())

        if settings.collector.enable_patent:
            self.collectors.append(PatentCollector())
        self.analyzer = IntelAnalyzer()
        self.rag = VectorRAG()
        self.report_generator = ReportGenerator()
        self.distributor = Distributor()

        # ===== Agent升级：新增模块 =====
        # 历史记忆系统
        self.memory = EpisodicMemory() if settings.enable_planning else None

        # 周计划Agent
        self.planner = WeeklyPlanningAgent(llm=self.analyzer.llm) if settings.enable_planning else None

        if settings.enable_planning:
            logger.info("✅ 规划Agent已初始化")
        if self.memory:
            logger.info("✅ 历史记忆系统已初始化")
    
    async def collect_and_analyze(self) -> List[RawIntelData]:
        """
        执行数据采集和分析
        
        Returns:
            分析后的情报条目列表
        """
        logger.info("=" * 50)
        logger.info("开始数据采集和分析...")
        logger.info("=" * 50)
        
        all_raw_items = []
        
        # 1. 采集数据
        for collector in self.collectors:
            try:
                logger.info(f"使用采集器: {collector.source_type}")
                result = await collector.collect()
                
                if result.success:
                    all_raw_items.extend(result.items)
                    logger.info(f"采集成功: {result.message}")
                else:
                    logger.warning(f"采集失败: {result.message}")
            
            except Exception as e:
                logger.error(f"采集器 {collector.source_type} 异常: {e}")
            
            finally:
                # 关闭采集器
                try:
                    await collector.close()
                except:
                    pass
        
        # 去重
        seen_urls = set()
        unique_items = []
        for item in all_raw_items:
            if item.url not in seen_urls:
                seen_urls.add(item.url)
                unique_items.append(item)
        
        logger.info(f"采集完成，共 {len(unique_items)} 条唯一数据")
        
        # 2. AI分析
        analyzed_items = []
        for i, raw_data in enumerate(unique_items, 1):
            try:
                logger.info(f"[{i}/{len(unique_items)}] 分析: {raw_data.title[:50]}...")
                
                # RAG检索（对所有数据进行）
                rag_context = ""
                if self.rag.is_initialized:
                    rag_context = self.rag.get_context_for_analysis(
                        raw_data.title + " " + raw_data.summary
                    )
                
                # AI分析
                item = await self.analyzer.analyze_item(raw_data, rag_context)
                
                if item:
                    analyzed_items.append(item)
            
            except Exception as e:
                logger.error(f"分析失败: {e}")
                continue
        
        logger.info(f"分析完成，成功保存 {len(analyzed_items)} 条情报")
        
        return analyzed_items
    
    async def generate_report(self) -> Optional[dict]:
        """
        生成周报并分发
        
        Returns:
            报告结果
        """
        logger.info("=" * 50)
        logger.info("开始生成周报...")
        logger.info("=" * 50)
        
        # 1. 生成周报
        report = await self.report_generator.generate_weekly_report()
        
        if not report:
            logger.error("周报生成失败")
            return None
        
        logger.info(f"周报生成成功: 第{report.issue_no}期")
        
        # 2. 分发周报
        distribution_results = await self.distributor.distribute_report(report)
        
        return {
            'issue_no': report.issue_no,
            'total_items': report.total_items,
            'distribution': distribution_results
        }
    
    async def run_full(self) -> dict:
        """
        执行完整流程：规划 -> 采集 -> 分析 -> 生成报告 -> 保存记忆 -> 分发

        Returns:
            执行结果
        """
        start_time = datetime.now()
        logger.info("CT产业情报Agent启动")

        # ===== Agent升级：Step 0 - 生成周计划 =====
        weekly_plan = None
        if settings.enable_planning and self.planner:
            try:
                logger.info("=" * 50)
                logger.info("Step 0: 生成本周计划...")
                logger.info("=" * 50)

                memory_ctx = self.memory.get_recent_context(
                    n_weeks=settings.memory_weeks_context
                ) if self.memory else ""

                weekly_plan = await self.planner.generate_plan(memory_ctx)
                logger.info(f"✅ 本周计划生成成功")
                logger.info(f"   重点公司: {', '.join(weekly_plan.focus_companies[:3])}")
                logger.info(f"   重点话题: {', '.join(weekly_plan.focus_topics[:3])}")
                logger.info(f"   理由: {weekly_plan.rationale}")

            except Exception as e:
                logger.error(f"生成周计划失败: {e}")
                weekly_plan = None

        # 1. 采集和分析
        analyzed_items = await self.collect_and_analyze()

        # 2. 生成和分发报告
        report_result = await self.generate_report()

        # ===== Agent升级：Step 3 - 保存记忆摘要 =====
        if settings.enable_planning and self.memory and report_result:
            try:
                logger.info("=" * 50)
                logger.info("Step 3: 保存记忆摘要...")
                logger.info("=" * 50)

                # 需要获取完整的报告对象以保存记忆
                # 这里简化处理，直接从��据库获取最新报告
                from database import db
                report = db.get_latest_weekly_report()
                if report:
                    memory_file = await self.memory.save_weekly_summary(
                        report, self.analyzer.llm
                    )
                    logger.info(f"✅ 记忆摘要已保存: {memory_file}")

            except Exception as e:
                logger.error(f"保存记忆摘要失败: {e}")

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        result = {
            'success': True,
            'analyzed_items': len(analyzed_items),
            'report': report_result,
            'weekly_plan': {
                'companies': weekly_plan.focus_companies if weekly_plan else [],
                'topics': weekly_plan.focus_topics if weekly_plan else []
            } if weekly_plan else None,
            'duration_seconds': duration
        }

        logger.info("=" * 50)
        logger.info(f"任务完成！耗时: {duration:.1f}秒")
        logger.info(f"   分析情报: {len(analyzed_items)} 条")
        if report_result:
            logger.info(f"   生成周报: 第{report_result['issue_no']}期")
        logger.info("=" * 50)

        return result
    
    async def run_schedule(self):
        """定时调度模式"""
        from apscheduler.schedulers.asyncio import AsyncIOScheduler
        from apscheduler.triggers.cron import CronTrigger
        
        scheduler = AsyncIOScheduler()
        
        # 配置调度时间
        day_map = {
            'mon': 'mon',
            'tue': 'tue',
            'wed': 'wed',
            'thu': 'thu',
            'fri': 'fri',
            'sat': 'sat',
            'sun': 'sun'
        }
        
        day_of_week = settings.schedule.day_of_week.lower()
        hour = settings.schedule.hour
        minute = settings.schedule.minute
        
        logger.info(f"定时调度模式启动")
        logger.info(f"   执行时间: 每周{day_of_week} {hour:02d}:{minute:02d}")
        
        # 添加定时任务
        scheduler.add_job(
            self.run_full,
            CronTrigger(day_of_week=day_map.get(day_of_week, 'fri'), hour=hour, minute=minute),
            id='weekly_job',
            replace_existing=True
        )
        
        scheduler.start()
        
        # 保持运行
        try:
            while True:
                await asyncio.sleep(60)
        except (KeyboardInterrupt, SystemExit):
            logger.info("接收到退出信号，正在关闭...")
            scheduler.shutdown()


async def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='CT产业情报Agent')
    parser.add_argument(
        '--collect',
        action='store_true',
        help='仅执行数据采集和分析'
    )
    parser.add_argument(
        '--report',
        action='store_true',
        help='仅生成周报'
    )
    parser.add_argument(
        '--schedule',
        action='store_true',
        help='定时调度模式'
    )
    parser.add_argument(
        '--test',
        action='store_true',
        help='测试模式（检查配置）'
    )
    
    args = parser.parse_args()
    
    agent = TelecomIntelAgent()
    
    # 测试模式
    if args.test:
        print("=" * 50)
        print("CT产业情报Agent - 配置检查")
        print("=" * 50)
        print(f"\n项目路径: {settings.project_root}")
        print(f"数据目录: {settings.data_dir}")
        print(f"知识库目录: {settings.knowledge_base_dir}")
        print(f"\nLLM配置:")
        print(f"   可用模型: {agent.analyzer.llm.get_available_providers()}")
        print(f"\n采集器配置:")
        print(f"   启用采集器: {', '.join([c.source_type for c in agent.collectors])}")
        print(f"   RSS源: {len(settings.collector.rss_feeds)} 个")
        print(f"   监控公司: {len(settings.collector.target_companies)} 家")
        print(f"\n分发配置:")
        print(f"   邮件: {'已配置' if agent.distributor.email_sender.is_configured() else '未配置'}")
        print(f"   微信: {'已配置' if agent.distributor.wechat_sender.is_configured() else '未配置'}")
        print(f"\nRAG系统: {'已初始化' if agent.rag.is_initialized else '未初始化'}")
        print("=" * 50)
        return
    
    # 定时调度模式
    if args.schedule:
        await agent.run_schedule()
        return
    
    # 仅采集
    if args.collect:
        analyzed_items = await agent.collect_and_analyze()
        print(f"\n采集完成，共分析 {len(analyzed_items)} 条情报")

        # 自动发送采集结果邮件（已禁用）
        # if analyzed_items and agent.distributor.email_sender.is_configured():
        #     try:
        #         logger.info("准备发送采集结果邮件...")
        #         email_content = await agent.distributor.send_collect_summary(analyzed_items)
        #         print(f"✅ 采集结果已发送到邮箱")
        #     except Exception as e:
        #         logger.error(f"发送采集结果邮件失败: {e}")
        #         print(f"⚠️ 邮件发送失败: {e}")
        return
    
    # 仅生成报告
    if args.report:
        result = await agent.generate_report()
        if result:
            print(f"\n周报生成成功: 第{result['issue_no']}期")
            print(f"共包含 {result['total_items']} 条情报")
        return
    
    # 完整流程
    result = await agent.run_full()
    
    if result['success']:
        print("\n执行成功！")
        print(f"   分析情报: {result['analyzed_items']} 条")
        if result['report']:
            print(f"   生成周报: 第{result['report']['issue_no']}期")
        print(f"   总耗时: {result['duration_seconds']:.1f} 秒")
    else:
        print("\n执行失败")
        sys.exit(1)


if __name__ == "__main__":
    # Python 3.14+ 不需要手动设置事件循环策略
    asyncio.run(main())
