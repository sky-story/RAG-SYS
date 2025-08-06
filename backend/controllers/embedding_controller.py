# -*- coding: utf-8 -*-
"""
embedding_controller.py
Embedding 业务逻辑控制器

功能：
1. 协调 segment 数据获取、embedding 生成和向量存储
2. 处理文件ID和解析ID的转换
3. 提供完整的 embedding 工作流程
4. 错误处理和日志记录

作者：AI Assistant
日期：2025-08-07
"""

import time
import logging
from typing import Dict, Any, List
from datetime import datetime

# 导入模型和服务
from models.segment_model import SegmentModel
from models.parse_model import ParseModel
from services.embedding_service import get_embedding_service
from services.vector_store import get_vector_store

logger = logging.getLogger(__name__)


class EmbeddingController:
    """
    Embedding 业务逻辑控制器
    """
    
    def __init__(self):
        """初始化控制器"""
        from config import Config
        
        self.segment_model = SegmentModel(Config.MONGO_URI, Config.MONGO_DB_NAME)
        self.parse_model = ParseModel(Config.MONGO_URI, Config.MONGO_DB_NAME)
        self.embedding_service = get_embedding_service()
        self.vector_store = get_vector_store()
        
        logger.info("EmbeddingController 初始化完成")
    
    def _serialize_datetime(self, obj):
        """
        递归处理对象中的 datetime 和 ObjectId 类型
        """
        from bson import ObjectId
        from datetime import datetime
        
        if isinstance(obj, dict):
            return {key: self._serialize_datetime(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._serialize_datetime(item) for item in obj]
        elif isinstance(obj, ObjectId):
            return str(obj)
        elif isinstance(obj, datetime):
            return obj.isoformat()
        else:
            return obj
    
    def _resolve_file_id(self, file_id: str) -> str:
        """
        解析文件ID，支持传入解析记录ID或文件ID
        
        Args:
            file_id (str): 文件ID或解析记录ID
            
        Returns:
            str: 实际的文件ID，用于段落查询
        """
        try:
            # 首先尝试作为文件ID直接查询段落
            segments = self.segment_model.get_segments_by_file_id(file_id)
            if segments:
                logger.info(f"直接使用文件ID查询到段落: {file_id}")
                return file_id
            
            # 如果没有找到，尝试作为解析记录ID查询
            parse_record = self.parse_model.get_parse_by_id(file_id)
            if parse_record:
                actual_file_id = parse_record.get('file_id', file_id)
                logger.info(f"通过解析记录ID {file_id} 找到文件ID: {actual_file_id}")
                return actual_file_id
            
            # 最后尝试通过文件ID查找解析记录
            parse_record = self.parse_model.get_parse_by_file_id(file_id)
            if parse_record:
                logger.info(f"通过文件ID找到解析记录: {file_id}")
                return file_id
            
            logger.warning(f"无法解析文件ID: {file_id}")
            return file_id
            
        except Exception as e:
            logger.error(f"解析文件ID失败: {str(e)}")
            return file_id
    
    def create_embeddings(self, file_id: str, recreate: bool = False, 
                         batch_size: int = 32) -> Dict[str, Any]:
        """
        为指定文件创建 embedding 索引
        
        Args:
            file_id (str): 文件ID或解析记录ID
            recreate (bool): 是否强制重新创建索引
            batch_size (int): 批处理大小
            
        Returns:
            Dict[str, Any]: 处理结果
        """
        start_time = time.time()
        
        try:
            logger.info(f"开始为文件 {file_id} 创建 embedding，重新创建: {recreate}")
            
            # 解析实际的文件ID
            actual_file_id = self._resolve_file_id(file_id)
            
            # 检查是否已存在索引
            if not recreate and self.vector_store.index_exists(actual_file_id):
                index_info = self.vector_store.get_index_info(actual_file_id)
                logger.info(f"文件 {actual_file_id} 的索引已存在")
                
                processing_time = time.time() - start_time
                return {
                    'success': True,
                    'data': {
                        'file_id': actual_file_id,
                        'embedded_count': index_info.get('vector_count', 0),
                        'embedding_dimension': index_info.get('embedding_dimension', 0),
                        'processing_time': round(processing_time, 2),
                        'index_info': index_info,
                        'message': '索引已存在，无需重新创建'
                    }
                }
            
            # 获取段落数据
            logger.info(f"获取文件 {actual_file_id} 的段落数据")
            segments = self.segment_model.get_segments_by_file_id(actual_file_id)
            
            if not segments:
                return {
                    'success': False,
                    'error': f'文件 {actual_file_id} 没有可用的段落数据，请先进行文档分段'
                }
            
            logger.info(f"找到 {len(segments)} 个段落，开始生成 embedding")
            
            # 序列化段落数据
            serialized_segments = [self._serialize_datetime(segment) for segment in segments]
            
            # 生成 embedding
            embeddings, metadata = self.embedding_service.encode_segments(serialized_segments)
            
            if embeddings.size == 0:
                return {
                    'success': False,
                    'error': '向量生成失败，请检查段落文本内容'
                }
            
            # 如果需要重新创建，先删除现有索引
            if recreate:
                self.vector_store.delete_index(actual_file_id)
            
            # 存储到向量库
            logger.info(f"将 {len(embeddings)} 个向量存储到向量库")
            success = self.vector_store.add_vectors(actual_file_id, embeddings, metadata)
            
            if not success:
                return {
                    'success': False,
                    'error': '向量存储失败'
                }
            
            # 获取索引信息
            index_info = self.vector_store.get_index_info(actual_file_id)
            
            processing_time = time.time() - start_time
            
            logger.info(f"文件 {actual_file_id} 的 embedding 创建完成，耗时 {processing_time:.2f}s")
            
            return {
                'success': True,
                'data': {
                    'file_id': actual_file_id,
                    'embedded_count': len(embeddings),
                    'embedding_dimension': embeddings.shape[1] if embeddings.size > 0 else 0,
                    'processing_time': round(processing_time, 2),
                    'index_info': index_info
                }
            }
            
        except Exception as e:
            logger.error(f"创建 embedding 失败: {str(e)}")
            return {
                'success': False,
                'error': f'创建 embedding 失败: {str(e)}'
            }
    
    def get_embedding_info(self, file_id: str) -> Dict[str, Any]:
        """
        获取指定文件的 embedding 信息
        
        Args:
            file_id (str): 文件ID
            
        Returns:
            Dict[str, Any]: 索引信息
        """
        try:
            # 解析实际的文件ID
            actual_file_id = self._resolve_file_id(file_id)
            
            # 获取索引信息
            info = self.vector_store.get_index_info(actual_file_id)
            
            if info.get('exists'):
                # 添加创建时间信息
                try:
                    # 尝试从文件修改时间获取创建时间
                    import os
                    index_path = info.get('index_path')
                    if index_path and os.path.exists(index_path):
                        created_timestamp = os.path.getmtime(index_path)
                        info['created_at'] = datetime.fromtimestamp(created_timestamp).isoformat()
                except:
                    info['created_at'] = None
            
            return info
            
        except Exception as e:
            logger.error(f"获取 embedding 信息失败: {str(e)}")
            return {
                'exists': False,
                'error': str(e)
            }
    
    def delete_embeddings(self, file_id: str) -> Dict[str, Any]:
        """
        删除指定文件的 embedding 索引
        
        Args:
            file_id (str): 文件ID
            
        Returns:
            Dict[str, Any]: 删除结果
        """
        try:
            # 解析实际的文件ID
            actual_file_id = self._resolve_file_id(file_id)
            
            # 检查索引是否存在
            if not self.vector_store.index_exists(actual_file_id):
                return {
                    'success': False,
                    'error': f'文件 {actual_file_id} 的索引不存在'
                }
            
            # 删除索引
            success = self.vector_store.delete_index(actual_file_id)
            
            if success:
                logger.info(f"文件 {actual_file_id} 的索引删除成功")
                return {
                    'success': True,
                    'data': {
                        'file_id': actual_file_id,
                        'deleted': True
                    }
                }
            else:
                return {
                    'success': False,
                    'error': '索引删除失败'
                }
                
        except Exception as e:
            logger.error(f"删除 embedding 失败: {str(e)}")
            return {
                'success': False,
                'error': f'删除 embedding 失败: {str(e)}'
            }
    
    def list_all_embeddings(self) -> Dict[str, Any]:
        """
        列出所有的 embedding 索引
        
        Returns:
            Dict[str, Any]: 索引列表
        """
        try:
            indices = self.vector_store.list_all_indices()
            
            # 添加额外信息
            for index_info in indices:
                try:
                    file_id = index_info.get('file_id')
                    if file_id:
                        # 尝试获取段落数量
                        segments = self.segment_model.get_segments_by_file_id(file_id)
                        index_info['segment_count'] = len(segments) if segments else 0
                        
                        # 尝试获取文件名
                        if segments:
                            index_info['file_name'] = segments[0].get('file_name', 'Unknown')
                except:
                    pass
            
            return {
                'total': len(indices),
                'indices': indices
            }
            
        except Exception as e:
            logger.error(f"列出 embedding 索引失败: {str(e)}")
            return {
                'total': 0,
                'indices': [],
                'error': str(e)
            }
    
    def search_embeddings(self, file_id: str, query: str, top_k: int = 5, 
                         min_score: float = 0.0) -> Dict[str, Any]:
        """
        在指定文件的向量索引中搜索
        
        Args:
            file_id (str): 文件ID
            query (str): 查询文本
            top_k (int): 返回结果数量
            min_score (float): 最小相似度阈值
            
        Returns:
            Dict[str, Any]: 搜索结果
        """
        start_time = time.time()
        
        try:
            logger.info(f"搜索文件 {file_id}，查询: '{query[:50]}...'")
            
            # 解析实际的文件ID
            actual_file_id = self._resolve_file_id(file_id)
            
            # 检查索引是否存在
            if not self.vector_store.index_exists(actual_file_id):
                return {
                    'success': False,
                    'error': f'文件 {actual_file_id} 的索引不存在，请先创建 embedding'
                }
            
            # 将查询文本转换为向量
            query_vector = self.embedding_service.encode_text(query)
            
            # 在向量库中搜索
            results = self.vector_store.search(actual_file_id, query_vector, top_k)
            
            # 过滤低分结果
            filtered_results = [
                result for result in results 
                if result.get('similarity', 0) >= min_score
            ]
            
            search_time = time.time() - start_time
            
            logger.info(f"搜索完成，返回 {len(filtered_results)} 个结果，耗时 {search_time:.3f}s")
            
            return {
                'success': True,
                'data': {
                    'query': query,
                    'file_id': actual_file_id,
                    'total_results': len(filtered_results),
                    'search_time': round(search_time, 3),
                    'results': filtered_results
                }
            }
            
        except Exception as e:
            logger.error(f"搜索 embedding 失败: {str(e)}")
            return {
                'success': False,
                'error': f'搜索失败: {str(e)}'
            }
    
    def search_multiple_files(self, file_ids: List[str], query: str, 
                            top_k: int = 5, min_score: float = 0.0) -> Dict[str, Any]:
        """
        在多个文件的向量索引中搜索
        
        Args:
            file_ids (List[str]): 文件ID列表
            query (str): 查询文本
            top_k (int): 每个文件返回结果数量
            min_score (float): 最小相似度阈值
            
        Returns:
            Dict[str, Any]: 搜索结果
        """
        start_time = time.time()
        
        try:
            logger.info(f"多文件搜索，文件数: {len(file_ids)}，查询: '{query[:50]}...'")
            
            # 解析实际的文件ID列表
            actual_file_ids = [self._resolve_file_id(fid) for fid in file_ids]
            
            # 将查询文本转换为向量
            query_vector = self.embedding_service.encode_text(query)
            
            # 在向量库中搜索
            all_results = self.vector_store.search_multiple_files(
                actual_file_ids, query_vector, top_k
            )
            
            # 过滤低分结果
            filtered_results = {}
            total_results = 0
            
            for file_id, results in all_results.items():
                filtered = [
                    result for result in results 
                    if result.get('similarity', 0) >= min_score
                ]
                filtered_results[file_id] = filtered
                total_results += len(filtered)
            
            search_time = time.time() - start_time
            
            logger.info(f"多文件搜索完成，总结果数: {total_results}，耗时 {search_time:.3f}s")
            
            return {
                'success': True,
                'data': {
                    'query': query,
                    'searched_files': len(actual_file_ids),
                    'total_results': total_results,
                    'search_time': round(search_time, 3),
                    'results': filtered_results
                }
            }
            
        except Exception as e:
            logger.error(f"多文件搜索失败: {str(e)}")
            return {
                'success': False,
                'error': f'多文件搜索失败: {str(e)}'
            }
    
    def health_check(self) -> Dict[str, Any]:
        """
        健康检查
        
        Returns:
            Dict[str, Any]: 服务状态
        """
        try:
            # 检查 embedding 服务
            model_info = self.embedding_service.get_model_info()
            
            # 检查向量存储
            all_indices = self.vector_store.list_all_indices()
            
            return {
                'service_status': 'healthy',
                'model_loaded': model_info.get('is_loaded', False),
                'model_info': model_info,
                'total_indices': len(all_indices),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"健康检查失败: {str(e)}")
            return {
                'service_status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }