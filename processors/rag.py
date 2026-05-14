"""
RAG检索模块 - 向量知识检索
"""
import os
import yaml
from typing import List, Dict, Any, Optional
from pathlib import Path

from loguru import logger

from config import settings


class VectorRAG:
    """向量RAG检索系统"""
    
    def __init__(self):
        self.knowledge_base_path = settings.knowledge_base_dir / "technical_keywords.yaml"
        self.vector_db_path = settings.knowledge_base_dir / "chroma_db"
        self.embedding_model = settings.embedding_model
        self.top_k = settings.top_k
        self.similarity_threshold = settings.similarity_threshold
        
        self.knowledge_chunks: List[Dict[str, Any]] = []
        self.embeddings: List[List[float]] = []
        self.chroma_client = None
        self.chroma_collection = None
        self.is_initialized = False
        
        # 延迟初始化
        self._init_vector_store()
    
    def _init_vector_store(self):
        """初始化向量存储"""
        try:
            # 尝试导入sentence-transformers
            try:
                from sentence_transformers import SentenceTransformer
                self.model = SentenceTransformer(self.embedding_model)
                logger.info(f"加载嵌入模型: {self.embedding_model}")
            except ImportError:
                logger.warning("未安装sentence-transformers，使用简单的关键词匹配")
                self.model = None
            
            # 加载知识库
            self._load_knowledge_base()
            
            # 构建向量索引
            self._build_index()
            
            self.is_initialized = True
            logger.info(f"RAG系统初始化完成，共 {len(self.knowledge_chunks)} 个知识片段")
        
        except Exception as e:
            logger.error(f"RAG初始化失败: {e}")
            self.is_initialized = False
    
    def _load_knowledge_base(self):
        """加载知识库文件"""
        if not self.knowledge_base_path.exists():
            logger.warning(f"知识库文件不存在: {self.knowledge_base_path}")
            # 创建默认知识库
            self._create_default_knowledge_base()
        
        try:
            with open(self.knowledge_base_path, 'r', encoding='utf-8') as f:
                knowledge = yaml.safe_load(f)
            
            # 将知识库转换为文本片段
            for category, items in knowledge.items():
                if isinstance(items, list):
                    for item in items:
                        if isinstance(item, dict):
                            # 结构化数据
                            content = item.get('description', '')
                            keywords = item.get('keywords', [])
                            if content:
                                self.knowledge_chunks.append({
                                    'category': category,
                                    'content': content,
                                    'keywords': keywords,
                                    'full_text': f"{category}: {content} {' '.join(keywords)}"
                                })
                        elif isinstance(item, str):
                            # 简单字符串
                            self.knowledge_chunks.append({
                                'category': category,
                                'content': item,
                                'keywords': [],
                                'full_text': f"{category}: {item}"
                            })
        
        except Exception as e:
            logger.error(f"加载知识库失败: {e}")
            self.knowledge_chunks = []
    
    def _create_default_knowledge_base(self):
        """创建默认知识库"""
        default_knowledge = {
            "通信标准": [
                {"description": "3GPP是制定移动通信标准的国际组织，负责5G NR、6G等技术标准制定", "keywords": ["3GPP", "5G NR", "6G", "Release 18", "Release 19"]},
                {"description": "ITU-R负责国际无线电通信规则制定，包括IMT-2020(5G)和IMT-2030(6G)标准", "keywords": ["ITU-R", "IMT-2020", "IMT-2030"]},
                {"description": "5G-A(5G-Advanced)是5G向6G演进的关键阶段，也称为5.5G", "keywords": ["5G-A", "5G-Advanced", "5.5G"]},
            ],
            "无线技术": [
                {"description": "Massive MIMO大规模天线技术，通过大量天线提升频谱效率和系统容量", "keywords": ["Massive MIMO", "64T64R", "32T32R", "波束赋形"]},
                {"description": "毫米波(mmWave)使用24GHz以上频段，提供超大带宽但覆盖范围有限", "keywords": ["毫米波", "mmWave", "26GHz", "28GHz"]},
                {"description": "sub-6GHz是5G主要频段，兼顾覆盖和容量，包括3.5GHz、2.6GHz等", "keywords": ["sub-6GHz", "3.5GHz", "C-band", "2.6GHz"]},
                {"description": "载波聚合(CA)将多个载波绑定提升速率，是4G/5G的关键技术", "keywords": ["载波聚合", "CA", "载波绑定"]},
                {"description": "OFDMA正交频分多址是5G下行和上行多址技术，支持灵活的频谱分配", "keywords": ["OFDMA", "正交频分多址", "多址技术"]},
            ],
            "光通信技术": [
                {"description": "WDM波分复用技术在一根光纤上传输多路光信号，提升传输容量", "keywords": ["WDM", "波分复用", "CWDM", "DWDM"]},
                {"description": "DWDM密集波分复用支持80-160个波长，是骨干网主流技术", "keywords": ["DWDM", "密集波分复用", "100G", "400G"]},
                {"description": "OTN光传送网是下一代骨干传送网技术，支持大颗粒业务调度", "keywords": ["OTN", "光传送网", "OSN", "交叉调度"]},
                {"description": "PON无源光网络是光纤接入主流技术，包括GPON、XG-PON、XGS-PON、50G PON", "keywords": ["PON", "GPON", "XGS-PON", "50G PON", "FTTH"]},
                {"description": "硅光技术基于硅材料的光器件技术，可降低成本和功耗", "keywords": ["硅光", "硅光子", "硅基光电子", "光模块"]},
                {"description": "相干光通信使用相位和幅度调制，支持超长距离传输", "keywords": ["相干光通信", "相干检测", "QPSK", "QAM"]},
            ],
            "核心网技术": [
                {"description": "5G Core基于云原生架构，采用SBA服务化架构，支持网络切片", "keywords": ["5G Core", "5GC", "SBA", "服务化架构"]},
                {"description": "网络切片技术允许在单一物理网络上创建多个虚拟网络，满足不同业务需求", "keywords": ["网络切片", "Network Slicing", "eMBB", "uRLLC", "mMTC"]},
                {"description": "MEC多接入边缘计算将计算能力下沉到网络边缘，降低时延", "keywords": ["MEC", "边缘计算", "边缘云", "UPF下沉"]},
                {"description": "UPF用户面功能是5G核心网关键网元，负责用户数据转发", "keywords": ["UPF", "用户面功能", "数据转发"]},
                {"description": "NFV网络功能虚拟化将网络功能软件化，部署在通用服务器上", "keywords": ["NFV", "网络功能虚拟化", "vIMS", "vEPC"]},
                {"description": "SDN软件定义网络实现控制面和转发面分离，支持灵活的网络编程", "keywords": ["SDN", "软件定义网络", "OpenFlow", "控制器"]},
            ],
            "网络架构": [
                {"description": "RAN无线接入网包括基站和射频设备，向Open RAN和vRAN演进", "keywords": ["RAN", "接入网", "基站", "gNB", "eNB"]},
                {"description": "Open RAN开放无线接入网，通过开放接口实现多厂商设备互联互通", "keywords": ["Open RAN", "O-RAN", "开放接口", "白盒基站"]},
                {"description": "vRAN虚拟化无线接入网将基站功能云化，运行在通用硬件上", "keywords": ["vRAN", "虚拟化基站", "云化基站", "C-RAN"]},
                {"description": "承载网负责接入网和核心网之间的数据传输，包括前传、中传、回传", "keywords": ["承载网", "前传", "中传", "回传", "Fronthaul"]},
                {"description": "DCI数据中心互联连接多个数据中心，要求高带宽低时延", "keywords": ["DCI", "数据中心互联", "数据中心互联"]},
            ],
            "芯片技术": [
                {"description": "基带芯片处理基带信号，是手机、基站的核心器件", "keywords": ["基带芯片", "Modem", "Balong", "X55", "X70"]},
                {"description": "射频前端包括PA、LNA、滤波器、开关等，是无线通信关键器件", "keywords": ["射频前端", "RFFE", "PA", "LNA", "滤波器"]},
                {"description": "光模块芯片包括激光器、探测器、驱动芯片、DSP等", "keywords": ["光模块芯片", "光芯片", "EML", "DML", "APD"]},
                {"description": "交换机芯片是网络设备核心，高端市场由博通、思科主导", "keywords": ["交换机芯片", "交换芯片", "Tomahawk", "Trident"]},
                {"description": "FPGA现场可编程门阵列在通信领域用于协议处理、信号处理等", "keywords": ["FPGA", "现场可编程", "可编程逻辑"]},
            ],
            "关键技术": [
                {"description": "AI原生网络在网络中引入人工智能，实现智能优化和自动化运维", "keywords": ["AI原生网络", "AI-RAN", "智能网络", "网络自动化"]},
                {"description": "算网融合将计算和网络资源统一调度，实现算力网络", "keywords": ["算网融合", "算力网络", "CFN", "计算优先网络"]},
                {"description": "确定性网络提供可保障的时延、抖动和丢包率，满足工业控制需求", "keywords": ["确定性网络", "DetNet", "TSN", "时间敏感网络"]},
                {"description": "NTN非地面网络通过卫星实现广域覆盖，是6G的重要组成部分", "keywords": ["NTN", "非地面网络", "卫星通信", "空天地一体化"]},
                {"description": "通感一体化将通信和感知功能融合，是6G潜在关键技术", "keywords": ["通感一体化", "ISAC", "通信感知", "雷达通信"]},
            ],
            "下游应用": [
                {"description": "5G专网为企业构建独立或半独立的5G网络，满足行业特殊需求", "keywords": ["5G专网", "行业专网", "专网专用", "5G LAN"]},
                {"description": "工业物联网(IIoT)将工业设备联网，实现智能制造和预测性维护", "keywords": ["工业物联网", "IIoT", "智能制造", "工业互联网"]},
                {"description": "车联网V2X实现车与车、车与路、车与人之间的通信", "keywords": ["车联网", "V2X", "C-V2X", "车路协同"]},
                {"description": "智慧城市利用物联网、大数据等技术提升城市管理效率", "keywords": ["智慧城市", "Smart City", "城市大脑", "数字孪生"]},
                {"description": "FTTR光纤到房间将光纤延伸至室内每个房间，解决WiFi覆盖问题", "keywords": ["FTTR", "光纤到房间", "室内光纤", "隐形光缆"]},
            ],
            "市场与竞争": [
                {"description": "全球通信设备市场由华为、爱立信、诺基亚、中兴、思科五大厂商主导", "keywords": ["通信设备市场", "市场份额", "华为", "爱立信", "诺基亚", "中兴"]},
                {"description": "Open RAN市场新兴厂商包括Mavenir、Parallel Wireless、富士通等", "keywords": ["Open RAN市场", "Mavenir", "vRAN", "开放式基站"]},
                {"description": "光模块市场中国厂商份额领先，包括中际旭创、光迅科技、华工正源等", "keywords": ["光模块市场", "中际旭创", "光迅科技", "800G", "1.6T"]},
            ],
        }
        
        # 确保目录存在
        self.knowledge_base_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 写入文件
        with open(self.knowledge_base_path, 'w', encoding='utf-8') as f:
            yaml.dump(default_knowledge, f, allow_unicode=True, sort_keys=False)
        
        logger.info(f"创建默认知识库: {self.knowledge_base_path}")
    
    def _build_index(self):
        """构建向量索引，优先持久化到ChromaDB，失败则保留内存索引"""
        if not self.knowledge_chunks:
            return
        
        try:
            texts = [chunk['full_text'] for chunk in self.knowledge_chunks]
            if self.model:
                self.embeddings = self.model.encode(texts).tolist()
                logger.info(f"构建内存向量索引完成，共 {len(self.embeddings)} 个向量")

            # ChromaDB 持久化索引
            try:
                import chromadb

                self.vector_db_path.mkdir(parents=True, exist_ok=True)
                self.chroma_client = chromadb.PersistentClient(path=str(self.vector_db_path))
                self.chroma_collection = self.chroma_client.get_or_create_collection(
                    name="technical_knowledge",
                    metadata={"description": "通信技术知识库"}
                )

                ids = [f"technical_{i}" for i in range(len(self.knowledge_chunks))]
                metadatas = [
                    {
                        "category": chunk.get("category", ""),
                        "keywords": ", ".join(chunk.get("keywords", [])),
                    }
                    for chunk in self.knowledge_chunks
                ]

                if self.embeddings:
                    self.chroma_collection.upsert(
                        ids=ids,
                        documents=texts,
                        metadatas=metadatas,
                        embeddings=self.embeddings,
                    )
                else:
                    self.chroma_collection.upsert(
                        ids=ids,
                        documents=texts,
                        metadatas=metadatas,
                    )

                logger.info(f"ChromaDB持久化索引完成: {self.vector_db_path}")
            except Exception as e:
                self.chroma_client = None
                self.chroma_collection = None
                logger.warning(f"ChromaDB索引不可用，使用内存/关键词检索: {e}")
        
        except Exception as e:
            logger.error(f"构建向量索引失败: {e}")
            self.embeddings = []
    
    def search(self, query: str, top_k: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        搜索相关知识
        
        Args:
            query: 查询文本
            top_k: 返回结果数量
        
        Returns:
            相关知识片段列表
        """
        if not top_k:
            top_k = self.top_k
        
        if not self.is_initialized or not self.knowledge_chunks:
            return []
        
        try:
            if self.chroma_collection:
                return self._chroma_search(query, top_k)
            elif self.model and self.embeddings:
                # 使用向量相似度搜索
                return self._vector_search(query, top_k)
            else:
                # 使用关键词匹配
                return self._keyword_search(query, top_k)
        
        except Exception as e:
            logger.error(f"搜索失败: {e}")
            return []

    def _chroma_search(self, query: str, top_k: int) -> List[Dict[str, Any]]:
        """使用ChromaDB持久化向量库搜索"""
        if not self.chroma_collection:
            return []

        query_embeddings = None
        if self.model:
            query_embeddings = self.model.encode([query]).tolist()

        if query_embeddings:
            response = self.chroma_collection.query(
                query_embeddings=query_embeddings,
                n_results=top_k,
                include=["documents", "metadatas", "distances"]
            )
        else:
            response = self.chroma_collection.query(
                query_texts=[query],
                n_results=top_k,
                include=["documents", "metadatas", "distances"]
            )

        documents = response.get("documents", [[]])[0]
        metadatas = response.get("metadatas", [[]])[0]
        distances = response.get("distances", [[]])[0]

        results = []
        for doc, meta, distance in zip(documents, metadatas, distances):
            similarity = 1 - float(distance)
            if similarity < self.similarity_threshold:
                continue

            content = doc
            category = meta.get("category", "") if meta else ""
            if ": " in doc:
                _, content = doc.split(": ", 1)

            keywords = []
            if meta and meta.get("keywords"):
                keywords = [kw.strip() for kw in meta["keywords"].split(",") if kw.strip()]

            results.append({
                "category": category,
                "content": content,
                "keywords": keywords,
                "full_text": doc,
                "similarity": similarity,
            })

        return results
    
    def _vector_search(self, query: str, top_k: int) -> List[Dict[str, Any]]:
        """向量相似度搜索"""
        from numpy import dot
        from numpy.linalg import norm
        
        # 计算查询向量
        query_embedding = self.model.encode([query])[0]
        
        # 计算相似度
        similarities = []
        for i, emb in enumerate(self.embeddings):
            cos_sim = dot(query_embedding, emb) / (norm(query_embedding) * norm(emb))
            similarities.append((i, cos_sim))
        
        # 排序并筛选
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        results = []
        for idx, score in similarities[:top_k]:
            if score >= self.similarity_threshold:
                chunk = self.knowledge_chunks[idx].copy()
                chunk['similarity'] = float(score)
                results.append(chunk)
        
        return results
    
    def _keyword_search(self, query: str, top_k: int) -> List[Dict[str, Any]]:
        """关键词匹配搜索"""
        query_keywords = set(query.lower().split())
        
        results = []
        for chunk in self.knowledge_chunks:
            chunk_text = chunk['full_text'].lower()
            
            # 计算匹配的关键词数量
            matches = sum(1 for kw in query_keywords if kw in chunk_text)
            
            if matches > 0:
                result = chunk.copy()
                result['similarity'] = matches / len(query_keywords) if query_keywords else 0
                results.append(result)
        
        # 按相似度排序
        results.sort(key=lambda x: x['similarity'], reverse=True)
        
        return results[:top_k]
    
    def get_context_for_analysis(self, query: str, top_k: Optional[int] = None) -> str:
        """
        为分析任务获取相关知识上下文
        
        Args:
            query: 查询文本
        
        Returns:
            格式化的知识上下文
        """
        results = self.search(query, top_k=top_k or 3)
        
        if not results:
            return ""
        
        context_parts = []
        for i, result in enumerate(results, 1):
            context_parts.append(f"[{i}] {result['category']}: {result['content']}")
            if result.get('keywords'):
                context_parts.append(f"    关键词: {', '.join(result['keywords'])}")
        
        return "\n\n".join(context_parts)
    
    def add_knowledge(self, category: str, content: str, keywords: List[str] = None):
        """
        添加新知识到知识库
        
        Args:
            category: 知识类别
            content: 知识内容
            keywords: 关键词列表
        """
        new_chunk = {
            'category': category,
            'content': content,
            'keywords': keywords or [],
            'full_text': f"{category}: {content} {' '.join(keywords or [])}"
        }
        
        self.knowledge_chunks.append(new_chunk)
        
        # 重新计算向量
        if self.model:
            new_embedding = self.model.encode([new_chunk['full_text']])[0].tolist()
            self.embeddings.append(new_embedding)
        
        logger.info(f"添加新知识: {category}")
    
    def save_knowledge_base(self):
        """保存知识库到文件"""
        try:
            knowledge = {}
            for chunk in self.knowledge_chunks:
                category = chunk['category']
                if category not in knowledge:
                    knowledge[category] = []
                
                knowledge[category].append({
                    'description': chunk['content'],
                    'keywords': chunk.get('keywords', [])
                })
            
            with open(self.knowledge_base_path, 'w', encoding='utf-8') as f:
                yaml.dump(knowledge, f, allow_unicode=True, sort_keys=False)
            
            logger.info(f"知识库已保存: {self.knowledge_base_path}")
        
        except Exception as e:
            logger.error(f"保存知识库失败: {e}")


# 全局RAG实例
rag = VectorRAG()
