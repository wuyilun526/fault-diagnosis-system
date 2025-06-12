import os
import logging
from typing import List, Dict, Optional
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

# 设置环境变量以禁用 tokenizers 并行处理
os.environ["TOKENIZERS_PARALLELISM"] = "false"

logger = logging.getLogger(__name__)

class VectorDBService:
    def __init__(self):
        self.collection_name = "fault_knowledge"
        self.dim = 768  # 向量维度
        self.model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        self._init_client()
        self._init_collection()

    def _init_client(self):
        """初始化 Chroma 客户端"""
        try:
            # 设置持久化存储路径
            persist_directory = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'chroma')
            os.makedirs(persist_directory, exist_ok=True)
            
            # 初始化客户端
            self.client = chromadb.PersistentClient(
                path=persist_directory,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            logger.info("Successfully initialized Chroma client")
        except Exception as e:
            logger.error(f"Failed to initialize Chroma client: {str(e)}")
            raise

    def _init_collection(self):
        """初始化或获取集合"""
        try:
            # 获取或创建集合
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}  # 使用余弦相似度
            )
            logger.info(f"Successfully initialized collection: {self.collection_name}")
        except Exception as e:
            logger.error(f"Failed to initialize collection: {str(e)}")
            raise

    def _generate_vector(self, text: str) -> List[float]:
        """生成文本的向量表示"""
        try:
            return self.model.encode(text).tolist()
        except Exception as e:
            logger.error(f"Failed to generate vector: {str(e)}")
            raise

    def add_knowledge(self, knowledge_data: Dict) -> bool:
        """添加知识条目到向量数据库"""
        try:
            # 生成症状描述的向量
            symptoms_vector = self._generate_vector(knowledge_data['symptoms'])
            
            # 准备元数据
            metadata = {
                'knowledge_id': str(knowledge_data['id']),
                'category': knowledge_data['category'],
                'title': knowledge_data['title'],
                'solution': knowledge_data['solution']
            }
            
            # 插入数据
            self.collection.add(
                embeddings=[symptoms_vector],
                documents=[knowledge_data['symptoms']],
                metadatas=[metadata],
                ids=[str(knowledge_data['id'])]
            )
            
            logger.info(f"Successfully added knowledge: {knowledge_data['title']}")
            return True
        except Exception as e:
            logger.error(f"Failed to add knowledge: {str(e)}")
            return False

    def search_knowledge(self, query: str, top_k: int = 3) -> List[Dict]:
        """搜索相似的知识条目"""
        try:
            # 生成查询向量
            query_vector = self._generate_vector(query)
            
            # 执行向量搜索
            results = self.collection.query(
                query_embeddings=[query_vector],
                n_results=top_k,
                include=['metadatas', 'distances', 'documents']
            )
            
            # 检查结果是否为空
            if not results or not results.get('metadatas') or not results['metadatas'][0]:
                logger.info("No results found in vector search")
                return []
            
            # 处理搜索结果
            matched_knowledge = []
            for i, (metadata, distance) in enumerate(zip(results['metadatas'][0], results['distances'][0])):
                # 将距离转换为相似度分数 (0-1之间，1表示最相似)
                similarity_score = (1 - distance) * 100  # 转换为百分比
                matched_knowledge.append({
                    'id': int(metadata['knowledge_id']),
                    'category': metadata['category'],
                    'title': metadata['title'],
                    'symptoms': results['documents'][0][i],
                    'solution': metadata['solution'],
                    'score': similarity_score
                })
            
            logger.info(f"Found {len(matched_knowledge)} matches with scores: {[k['score'] for k in matched_knowledge]}")
            return matched_knowledge
        except Exception as e:
            logger.error(f"Failed to search knowledge: {str(e)}")
            logger.error(f"Query: {query}")
            logger.error(f"Query vector shape: {len(query_vector) if 'query_vector' in locals() else 'Not generated'}")
            return []

    def delete_knowledge(self, knowledge_id: int) -> bool:
        """删除知识条目"""
        try:
            self.collection.delete(ids=[str(knowledge_id)])
            logger.info(f"Successfully deleted knowledge with ID: {knowledge_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete knowledge: {str(e)}")
            return False

    def update_knowledge(self, knowledge_data: Dict) -> bool:
        """更新知识条目"""
        try:
            # 先删除旧数据
            if not self.delete_knowledge(knowledge_data['id']):
                return False
            
            # 添加新数据
            return self.add_knowledge(knowledge_data)
        except Exception as e:
            logger.error(f"Failed to update knowledge: {str(e)}")
            return False 