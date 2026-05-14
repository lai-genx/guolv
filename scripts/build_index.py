"""
知识库向量索引构建工具

用法:
    python build_index.py           # 构建索引
    python build_index.py --reset   # 重置并重建索引
"""
import argparse
import yaml
from pathlib import Path
import sys
from loguru import logger

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config import settings
from processors.rag import VectorRAG


def build_index(reset: bool = False):
    """构建向量索引"""
    logger.info("开始构建知识库向量索引...")
    
    kb_path = settings.knowledge_base_dir / "technical_keywords.yaml"
    
    # 如果重置，删除现有索引
    if reset and kb_path.exists():
        logger.info("重置知识库...")
        # 保留文件，只重置向量数据
    
    # 初始化RAG系统（会自动构建索引）
    rag = VectorRAG()
    
    if rag.is_initialized:
        logger.info(f"索引构建成功！共 {len(rag.knowledge_chunks)} 个知识片段")
        
        # 测试搜索
        test_queries = [
            "5G基站技术",
            "光通信波分复用",
            "Open RAN架构",
        ]
        
        print("\n测试检索:")
        for query in test_queries:
            results = rag.search(query, top_k=2)
            print(f"\n查询: {query}")
            for i, result in enumerate(results, 1):
                print(f"  [{i}] {result['category']}: {result['content'][:60]}...")
    else:
        logger.error("索引构建失败")


def show_knowledge_base():
    """显示知识库内容"""
    kb_path = settings.knowledge_base_dir / "technical_keywords.yaml"
    
    if not kb_path.exists():
        logger.error(f"知识库文件不存在: {kb_path}")
        return
    
    with open(kb_path, 'r', encoding='utf-8') as f:
        knowledge = yaml.safe_load(f)
    
    print("\n知识库内容概览:")
    print("=" * 50)
    
    for category, items in knowledge.items():
        print(f"\n【{category}】 ({len(items)} 条)")
        for i, item in enumerate(items[:3], 1):  # 只显示前3条
            if isinstance(item, dict):
                desc = item.get('description', '')[:50]
                print(f"  {i}. {desc}...")
            else:
                print(f"  {i}. {str(item)[:50]}...")
        if len(items) > 3:
            print(f"  ... 还有 {len(items) - 3} 条")


def add_knowledge(category: str, description: str, keywords: str = ""):
    """添加新知识"""
    rag = VectorRAG()
    
    kw_list = [k.strip() for k in keywords.split(',') if k.strip()]
    rag.add_knowledge(category, description, kw_list)
    rag.save_knowledge_base()
    
    logger.info(f"已添加新知识到类别 '{category}'")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='知识库索引构建工具')
    parser.add_argument('--reset', action='store_true', help='重置并重建索引')
    parser.add_argument('--show', action='store_true', help='显示知识库内容')
    parser.add_argument('--add', action='store_true', help='添加新知识')
    parser.add_argument('--category', type=str, help='知识类别')
    parser.add_argument('--description', type=str, help='知识描述')
    parser.add_argument('--keywords', type=str, help='关键词（逗号分隔）')
    
    args = parser.parse_args()
    
    if args.show:
        show_knowledge_base()
    elif args.add:
        if not args.category or not args.description:
            print("错误: 添加知识需要 --category 和 --description 参数")
        else:
            add_knowledge(args.category, args.description, args.keywords or "")
    else:
        build_index(args.reset)
