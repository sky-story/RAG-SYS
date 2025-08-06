# -*- coding: utf-8 -*-
"""
embedding_service.py
段落文本向量化服务

功能：
1. 加载预训练的 sentence-transformers 模型
2. 将段落文本转换为 embedding 向量
3. 批量处理段落文本
4. 提供文本相似度计算功能

作者：AI Assistant
日期：2025-08-07
"""

import logging
import numpy as np
from typing import List, Dict, Any, Tuple
from sentence_transformers import SentenceTransformer
import torch

logger = logging.getLogger(__name__)


class EmbeddingService:
    """
    文本 Embedding 服务类
    
    使用 sentence-transformers 模型将文本转换为向量表示
    """
    
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        """
        初始化 Embedding 服务
        
        Args:
            model_name (str): sentence-transformers 模型名称
                            默认使用 'all-MiniLM-L6-v2' (轻量级，384维向量)
        """
        self.model_name = model_name
        self.model = None
        self.embedding_dim = None
        self._load_model()
    
    def _load_model(self):
        """
        加载 sentence-transformers 模型
        """
        try:
            logger.info(f"正在加载 sentence-transformers 模型: {self.model_name}")
            
            # 加载预训练模型
            self.model = SentenceTransformer(self.model_name)
            
            # 获取向量维度
            self.embedding_dim = self.model.get_sentence_embedding_dimension()
            
            logger.info(f"模型加载成功，向量维度: {self.embedding_dim}")
            
        except Exception as e:
            logger.error(f"模型加载失败: {str(e)}")
            raise Exception(f"Failed to load embedding model: {str(e)}")
    
    def encode_text(self, text: str) -> np.ndarray:
        """
        将单个文本转换为 embedding 向量
        
        Args:
            text (str): 待编码的文本
            
        Returns:
            np.ndarray: 文本对应的向量 (shape: [embedding_dim])
        """
        try:
            if not text or not text.strip():
                logger.warning("输入文本为空，返回零向量")
                return np.zeros(self.embedding_dim, dtype=np.float32)
            
            # 使用模型编码文本
            embedding = self.model.encode(
                text,
                convert_to_numpy=True,
                normalize_embeddings=True  # L2 归一化
            )
            
            return embedding.astype(np.float32)
            
        except Exception as e:
            logger.error(f"文本编码失败: {str(e)}")
            return np.zeros(self.embedding_dim, dtype=np.float32)
    
    def encode_batch(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        """
        批量将文本转换为 embedding 向量
        
        Args:
            texts (List[str]): 待编码的文本列表
            batch_size (int): 批处理大小，默认32
            
        Returns:
            np.ndarray: 文本向量矩阵 (shape: [len(texts), embedding_dim])
        """
        try:
            if not texts:
                logger.warning("输入文本列表为空")
                return np.array([]).reshape(0, self.embedding_dim)
            
            logger.info(f"开始批量编码 {len(texts)} 个文本，批大小: {batch_size}")
            
            # 过滤空文本
            valid_texts = []
            valid_indices = []
            for i, text in enumerate(texts):
                if text and text.strip():
                    valid_texts.append(text.strip())
                    valid_indices.append(i)
            
            if not valid_texts:
                logger.warning("所有输入文本都为空，返回零向量矩阵")
                return np.zeros((len(texts), self.embedding_dim), dtype=np.float32)
            
            # 批量编码
            embeddings = self.model.encode(
                valid_texts,
                batch_size=batch_size,
                convert_to_numpy=True,
                normalize_embeddings=True,
                show_progress_bar=True
            )
            
            # 处理空文本的情况
            result = np.zeros((len(texts), self.embedding_dim), dtype=np.float32)
            for i, valid_idx in enumerate(valid_indices):
                result[valid_idx] = embeddings[i]
            
            logger.info(f"批量编码完成，生成 {len(texts)} 个向量")
            return result
            
        except Exception as e:
            logger.error(f"批量编码失败: {str(e)}")
            return np.zeros((len(texts), self.embedding_dim), dtype=np.float32)
    
    def encode_segments(self, segments: List[Dict[str, Any]]) -> Tuple[np.ndarray, List[Dict[str, Any]]]:
        """
        将段落数据转换为 embedding 向量
        
        Args:
            segments (List[Dict]): 段落数据列表，每个段落包含 'text' 字段
            
        Returns:
            Tuple[np.ndarray, List[Dict]]: 
                - 向量矩阵 (shape: [len(segments), embedding_dim])
                - 对应的元数据列表
        """
        try:
            logger.info(f"开始处理 {len(segments)} 个段落的向量化")
            
            # 提取文本内容
            texts = []
            metadata = []
            
            for segment in segments:
                # 获取文本内容
                text = segment.get('text', '').strip()
                texts.append(text)
                
                # 构建元数据
                meta = {
                    'segment_id': segment.get('segment_id', ''),
                    'file_id': segment.get('file_id', ''),
                    'order': segment.get('order', 0),
                    'tags': segment.get('tags', []),
                    'file_name': segment.get('file_name', ''),
                    'character_count': len(text),
                    'created_at': segment.get('created_at'),
                    'text_preview': text[:100] + '...' if len(text) > 100 else text
                }
                metadata.append(meta)
            
            # 批量编码
            embeddings = self.encode_batch(texts)
            
            logger.info(f"段落向量化完成，生成 {len(embeddings)} 个向量")
            return embeddings, metadata
            
        except Exception as e:
            logger.error(f"段落向量化失败: {str(e)}")
            return np.array([]).reshape(0, self.embedding_dim), []
    
    def calculate_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        计算两个向量之间的余弦相似度
        
        Args:
            embedding1 (np.ndarray): 第一个向量
            embedding2 (np.ndarray): 第二个向量
            
        Returns:
            float: 余弦相似度 (-1 到 1 之间)
        """
        try:
            # 确保向量已归一化
            norm1 = np.linalg.norm(embedding1)
            norm2 = np.linalg.norm(embedding2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            # 计算余弦相似度
            similarity = np.dot(embedding1, embedding2) / (norm1 * norm2)
            return float(similarity)
            
        except Exception as e:
            logger.error(f"相似度计算失败: {str(e)}")
            return 0.0
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        获取模型信息
        
        Returns:
            Dict[str, Any]: 模型信息
        """
        return {
            'model_name': self.model_name,
            'embedding_dimension': self.embedding_dim,
            'device': str(self.model.device) if self.model else 'unknown',
            'max_seq_length': getattr(self.model, 'max_seq_length', 'unknown'),
            'is_loaded': self.model is not None
        }


# 全局单例实例
_embedding_service = None


def get_embedding_service() -> EmbeddingService:
    """
    获取 Embedding 服务单例
    
    Returns:
        EmbeddingService: Embedding 服务实例
    """
    global _embedding_service
    
    if _embedding_service is None:
        logger.info("初始化 Embedding 服务单例")
        _embedding_service = EmbeddingService()
    
    return _embedding_service


def preload_embedding_model():
    """
    预加载 embedding 模型
    在应用启动时调用，避免首次请求时的延迟
    """
    try:
        logger.info("预加载 embedding 模型")
        get_embedding_service()
        logger.info("embedding 模型预加载完成")
    except Exception as e:
        logger.error(f"embedding 模型预加载失败: {str(e)}")


if __name__ == "__main__":
    # 测试代码
    logging.basicConfig(level=logging.INFO)
    
    # 初始化服务
    service = EmbeddingService()
    
    # 测试单个文本编码
    test_text = "化工反应是化学工程的核心内容，涉及反应动力学、传热传质等多个方面。"
    embedding = service.encode_text(test_text)
    print(f"文本: {test_text}")
    print(f"向量维度: {embedding.shape}")
    print(f"向量前5维: {embedding[:5]}")
    
    # 测试批量编码
    test_texts = [
        "化工反应器的设计需要考虑反应动力学",
        "传热传质是化工过程的重要环节",
        "催化剂的选择对反应效率至关重要"
    ]
    embeddings = service.encode_batch(test_texts)
    print(f"\n批量编码结果: {embeddings.shape}")
    
    # 测试相似度计算
    sim = service.calculate_similarity(embeddings[0], embeddings[1])
    print(f"文本1和文本2的相似度: {sim:.4f}")
    
    # 模型信息
    info = service.get_model_info()
    print(f"\n模型信息: {info}")