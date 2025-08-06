# -*- coding: utf-8 -*-
"""
vector_store.py
FAISS 向量库管理服务

功能：
1. 创建和管理 FAISS 索引
2. 向量的插入、保存、加载
3. 向量相似度搜索
4. 元数据管理和存储
5. 支持多文档的独立索引管理

作者：AI Assistant
日期：2025-08-07
"""

import os
import json
import logging
import pickle
import numpy as np
from typing import List, Dict, Any, Tuple, Optional
import faiss
from pathlib import Path

logger = logging.getLogger(__name__)


class VectorStore:
    """
    基于 FAISS 的向量存储服务
    
    支持向量的存储、检索和管理
    """
    
    def __init__(self, base_dir: str = None):
        """
        初始化向量存储服务
        
        Args:
            base_dir (str): 向量库基础目录，默认为 backend/vector_db
        """
        if base_dir is None:
            # 使用相对于当前文件的路径
            current_dir = os.path.dirname(os.path.abspath(__file__))
            self.base_dir = os.path.join(os.path.dirname(current_dir), 'vector_db')
        else:
            self.base_dir = base_dir
        
        # 确保目录存在
        os.makedirs(self.base_dir, exist_ok=True)
        
        # 索引缓存
        self.index_cache = {}
        self.metadata_cache = {}
        
        logger.info(f"向量存储服务初始化完成，存储目录: {self.base_dir}")
    
    def _get_index_path(self, file_id: str) -> str:
        """获取索引文件路径"""
        return os.path.join(self.base_dir, f"{file_id}.faiss")
    
    def _get_metadata_path(self, file_id: str) -> str:
        """获取元数据文件路径"""
        return os.path.join(self.base_dir, f"{file_id}_metadata.json")
    
    def _get_embeddings_path(self, file_id: str) -> str:
        """获取向量数据文件路径"""
        return os.path.join(self.base_dir, f"{file_id}_embeddings.pkl")
    
    def create_index(self, embedding_dim: int, metric: str = "cosine") -> faiss.Index:
        """
        创建 FAISS 索引
        
        Args:
            embedding_dim (int): 向量维度
            metric (str): 距离度量方式 ("cosine", "l2", "ip")
                        - cosine: 余弦相似度 (推荐)
                        - l2: 欧氏距离
                        - ip: 内积 (适用于归一化向量)
        
        Returns:
            faiss.Index: FAISS 索引对象
        """
        try:
            logger.info(f"创建 FAISS 索引，维度: {embedding_dim}, 度量: {metric}")
            
            if metric == "cosine":
                # 余弦相似度 = 归一化向量的内积
                index = faiss.IndexFlatIP(embedding_dim)
            elif metric == "l2":
                # 欧氏距离
                index = faiss.IndexFlatL2(embedding_dim)
            elif metric == "ip":
                # 内积
                index = faiss.IndexFlatIP(embedding_dim)
            else:
                raise ValueError(f"不支持的度量方式: {metric}")
            
            logger.info(f"FAISS 索引创建成功")
            return index
            
        except Exception as e:
            logger.error(f"创建 FAISS 索引失败: {str(e)}")
            raise Exception(f"Failed to create FAISS index: {str(e)}")
    
    def add_vectors(self, file_id: str, embeddings: np.ndarray, metadata: List[Dict[str, Any]]) -> bool:
        """
        添加向量到指定文件的索引中
        
        Args:
            file_id (str): 文件ID
            embeddings (np.ndarray): 向量矩阵 [n_vectors, embedding_dim]
            metadata (List[Dict]): 对应的元数据列表
            
        Returns:
            bool: 是否成功
        """
        try:
            if len(embeddings) != len(metadata):
                raise ValueError("向量数量与元数据数量不匹配")
            
            if len(embeddings) == 0:
                logger.warning(f"文件 {file_id} 没有向量数据")
                return True
            
            logger.info(f"为文件 {file_id} 添加 {len(embeddings)} 个向量")
            
            # 检查向量维度
            embedding_dim = embeddings.shape[1]
            
            # 创建或加载索引
            if file_id in self.index_cache:
                index = self.index_cache[file_id]
                existing_metadata = self.metadata_cache[file_id]
            else:
                # 尝试加载现有索引
                if self.index_exists(file_id):
                    index, existing_metadata = self.load_index(file_id)
                else:
                    # 创建新索引
                    index = self.create_index(embedding_dim)
                    existing_metadata = []
            
            # 添加向量到索引
            embeddings_f32 = embeddings.astype(np.float32)
            index.add(embeddings_f32)
            
            # 更新元数据
            updated_metadata = existing_metadata + metadata
            
            # 保存到缓存
            self.index_cache[file_id] = index
            self.metadata_cache[file_id] = updated_metadata
            
            # 保存到磁盘
            self.save_index(file_id, index, updated_metadata)
            
            logger.info(f"文件 {file_id} 的向量添加完成，总向量数: {index.ntotal}")
            return True
            
        except Exception as e:
            logger.error(f"添加向量失败: {str(e)}")
            return False
    
    def save_index(self, file_id: str, index: faiss.Index, metadata: List[Dict[str, Any]]) -> bool:
        """
        保存索引和元数据到磁盘
        
        Args:
            file_id (str): 文件ID
            index (faiss.Index): FAISS 索引
            metadata (List[Dict]): 元数据列表
            
        Returns:
            bool: 是否成功
        """
        try:
            # 保存 FAISS 索引
            index_path = self._get_index_path(file_id)
            faiss.write_index(index, index_path)
            
            # 保存元数据
            metadata_path = self._get_metadata_path(file_id)
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2, default=str)
            
            logger.info(f"索引和元数据保存成功: {file_id}")
            return True
            
        except Exception as e:
            logger.error(f"保存索引失败: {str(e)}")
            return False
    
    def load_index(self, file_id: str) -> Tuple[faiss.Index, List[Dict[str, Any]]]:
        """
        从磁盘加载索引和元数据
        
        Args:
            file_id (str): 文件ID
            
        Returns:
            Tuple[faiss.Index, List[Dict]]: 索引和元数据
        """
        try:
            # 加载 FAISS 索引
            index_path = self._get_index_path(file_id)
            if not os.path.exists(index_path):
                raise FileNotFoundError(f"索引文件不存在: {index_path}")
            
            index = faiss.read_index(index_path)
            
            # 加载元数据
            metadata_path = self._get_metadata_path(file_id)
            if os.path.exists(metadata_path):
                with open(metadata_path, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
            else:
                logger.warning(f"元数据文件不存在: {metadata_path}")
                metadata = []
            
            # 缓存到内存
            self.index_cache[file_id] = index
            self.metadata_cache[file_id] = metadata
            
            logger.info(f"索引加载成功: {file_id}, 向量数: {index.ntotal}")
            return index, metadata
            
        except Exception as e:
            logger.error(f"加载索引失败: {str(e)}")
            raise Exception(f"Failed to load index: {str(e)}")
    
    def search(self, file_id: str, query_vector: np.ndarray, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        在指定文件的索引中搜索相似向量
        
        Args:
            file_id (str): 文件ID
            query_vector (np.ndarray): 查询向量
            top_k (int): 返回的相似结果数量
            
        Returns:
            List[Dict]: 搜索结果列表，包含元数据和相似度分数
        """
        try:
            # 获取索引
            if file_id in self.index_cache:
                index = self.index_cache[file_id]
                metadata = self.metadata_cache[file_id]
            else:
                index, metadata = self.load_index(file_id)
            
            if index.ntotal == 0:
                logger.warning(f"文件 {file_id} 的索引为空")
                return []
            
            # 确保查询向量格式正确
            query_vector = query_vector.astype(np.float32).reshape(1, -1)
            
            # 搜索
            actual_k = min(top_k, index.ntotal)
            distances, indices = index.search(query_vector, actual_k)
            
            # 构建结果
            results = []
            for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
                if idx == -1:  # FAISS 返回 -1 表示无效索引
                    continue
                
                if idx >= len(metadata):
                    logger.warning(f"索引 {idx} 超出元数据范围")
                    continue
                
                result = {
                    'rank': i + 1,
                    'score': float(distance),
                    'similarity': float(distance),  # 对于余弦相似度，距离就是相似度
                    'metadata': metadata[idx]
                }
                results.append(result)
            
            logger.info(f"搜索完成，返回 {len(results)} 个结果")
            return results
            
        except Exception as e:
            logger.error(f"搜索失败: {str(e)}")
            return []
    
    def search_multiple_files(self, file_ids: List[str], query_vector: np.ndarray, 
                            top_k: int = 5) -> Dict[str, List[Dict[str, Any]]]:
        """
        在多个文件的索引中搜索相似向量
        
        Args:
            file_ids (List[str]): 文件ID列表
            query_vector (np.ndarray): 查询向量
            top_k (int): 每个文件返回的相似结果数量
            
        Returns:
            Dict[str, List[Dict]]: 按文件ID分组的搜索结果
        """
        results = {}
        
        for file_id in file_ids:
            try:
                if self.index_exists(file_id):
                    file_results = self.search(file_id, query_vector, top_k)
                    results[file_id] = file_results
                else:
                    logger.warning(f"文件 {file_id} 的索引不存在")
                    results[file_id] = []
            except Exception as e:
                logger.error(f"搜索文件 {file_id} 失败: {str(e)}")
                results[file_id] = []
        
        return results
    
    def index_exists(self, file_id: str) -> bool:
        """
        检查指定文件的索引是否存在
        
        Args:
            file_id (str): 文件ID
            
        Returns:
            bool: 索引是否存在
        """
        index_path = self._get_index_path(file_id)
        return os.path.exists(index_path)
    
    def delete_index(self, file_id: str) -> bool:
        """
        删除指定文件的索引和元数据
        
        Args:
            file_id (str): 文件ID
            
        Returns:
            bool: 是否成功
        """
        try:
            # 从缓存中移除
            if file_id in self.index_cache:
                del self.index_cache[file_id]
            if file_id in self.metadata_cache:
                del self.metadata_cache[file_id]
            
            # 删除文件
            files_to_delete = [
                self._get_index_path(file_id),
                self._get_metadata_path(file_id),
                self._get_embeddings_path(file_id)
            ]
            
            for file_path in files_to_delete:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    logger.info(f"删除文件: {file_path}")
            
            logger.info(f"索引删除成功: {file_id}")
            return True
            
        except Exception as e:
            logger.error(f"删除索引失败: {str(e)}")
            return False
    
    def get_index_info(self, file_id: str) -> Dict[str, Any]:
        """
        获取索引信息
        
        Args:
            file_id (str): 文件ID
            
        Returns:
            Dict[str, Any]: 索引信息
        """
        try:
            if not self.index_exists(file_id):
                return {'exists': False}
            
            # 加载索引
            if file_id in self.index_cache:
                index = self.index_cache[file_id]
                metadata = self.metadata_cache[file_id]
            else:
                index, metadata = self.load_index(file_id)
            
            info = {
                'exists': True,
                'file_id': file_id,
                'vector_count': index.ntotal,
                'embedding_dimension': index.d,
                'metadata_count': len(metadata),
                'index_path': self._get_index_path(file_id),
                'metadata_path': self._get_metadata_path(file_id),
                'index_size_mb': self._get_file_size_mb(self._get_index_path(file_id)),
                'metadata_size_mb': self._get_file_size_mb(self._get_metadata_path(file_id))
            }
            
            return info
            
        except Exception as e:
            logger.error(f"获取索引信息失败: {str(e)}")
            return {'exists': False, 'error': str(e)}
    
    def _get_file_size_mb(self, file_path: str) -> float:
        """获取文件大小（MB）"""
        try:
            if os.path.exists(file_path):
                size_bytes = os.path.getsize(file_path)
                return round(size_bytes / (1024 * 1024), 2)
            return 0.0
        except:
            return 0.0
    
    def list_all_indices(self) -> List[Dict[str, Any]]:
        """
        列出所有索引
        
        Returns:
            List[Dict]: 所有索引的信息列表
        """
        indices = []
        
        try:
            # 扫描目录中的 .faiss 文件
            for file in os.listdir(self.base_dir):
                if file.endswith('.faiss'):
                    file_id = file.replace('.faiss', '')
                    info = self.get_index_info(file_id)
                    if info.get('exists'):
                        indices.append(info)
            
            logger.info(f"发现 {len(indices)} 个索引")
            
        except Exception as e:
            logger.error(f"列出索引失败: {str(e)}")
        
        return indices
    
    def clear_cache(self):
        """清空内存缓存"""
        self.index_cache.clear()
        self.metadata_cache.clear()
        logger.info("向量存储缓存已清空")


# 全局单例实例
_vector_store = None


def get_vector_store() -> VectorStore:
    """
    获取向量存储服务单例
    
    Returns:
        VectorStore: 向量存储服务实例
    """
    global _vector_store
    
    if _vector_store is None:
        logger.info("初始化向量存储服务单例")
        _vector_store = VectorStore()
    
    return _vector_store


if __name__ == "__main__":
    # 测试代码
    logging.basicConfig(level=logging.INFO)
    
    # 初始化向量存储
    store = VectorStore()
    
    # 测试数据
    test_file_id = "test_file_001"
    test_embeddings = np.random.random((5, 384)).astype(np.float32)
    test_metadata = [
        {'segment_id': f'seg_{i}', 'text': f'测试文本 {i}', 'order': i}
        for i in range(5)
    ]
    
    # 添加向量
    success = store.add_vectors(test_file_id, test_embeddings, test_metadata)
    print(f"添加向量结果: {success}")
    
    # 获取索引信息
    info = store.get_index_info(test_file_id)
    print(f"索引信息: {info}")
    
    # 搜索测试
    query_vector = np.random.random(384).astype(np.float32)
    results = store.search(test_file_id, query_vector, top_k=3)
    print(f"搜索结果: {len(results)} 个")
    for i, result in enumerate(results):
        print(f"  {i+1}. 相似度: {result['similarity']:.4f}, 元数据: {result['metadata']['segment_id']}")
    
    # 列出所有索引
    all_indices = store.list_all_indices()
    print(f"所有索引: {len(all_indices)} 个")
    
    # 清理测试数据
    store.delete_index(test_file_id)
    print("测试数据清理完成")