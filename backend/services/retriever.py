# -*- coding: utf-8 -*-
"""
retriever.py
向量检索服务

功能：
1. 使用 OpenAI embedding 将查询文本向量化
2. 在 FAISS 向量库中检索相似文档段落
3. 返回最相关的文档片段用于 RAG 生成
4. 支持多文件检索和相似度过滤

作者：AI Assistant
日期：2025-08-07
"""

import logging
import openai
import numpy as np
from typing import List, Dict, Any, Tuple, Optional
from config import Config
from services.vector_store import get_vector_store
from services.embedding_service import get_embedding_service

logger = logging.getLogger(__name__)


class RetrieverService:
    """
    向量检索服务类
    
    负责将用户查询转换为向量，并在向量库中检索相关文档段落
    """
    
    def __init__(self):
        """初始化检索服务"""
        self.openai_client = openai.OpenAI(api_key=Config.OPENAI_API_KEY)
        self.vector_store = get_vector_store()
        self.embedding_service = get_embedding_service()
        
        # 配置参数
        self.embedding_model = Config.OPENAI_EMBEDDING_MODEL
        self.top_k = Config.RAG_TOP_K
        self.min_similarity = Config.RAG_MIN_SIMILARITY
        
        logger.info(f"RetrieverService 初始化完成，使用模型: {self.embedding_model}")
    
    def encode_query_openai(self, query: str) -> np.ndarray:
        """
        使用 OpenAI embedding API 将查询文本向量化
        
        Args:
            query (str): 查询文本
            
        Returns:
            np.ndarray: 查询向量
        """
        try:
            logger.info(f"使用 OpenAI 模型 {self.embedding_model} 编码查询: '{query[:50]}...'")
            
            # 调用 OpenAI embedding API
            response = self.openai_client.embeddings.create(
                model=self.embedding_model,
                input=query,
                encoding_format="float"
            )
            
            # 提取向量
            embedding = np.array(response.data[0].embedding, dtype=np.float32)
            
            logger.info(f"OpenAI 查询向量化完成，维度: {embedding.shape}")
            
            # 检查维度兼容性
            # 如果 OpenAI 向量维度与现有索引不匹配，降级使用本地模型
            if embedding.shape[0] != 384:  # 现有索引是 384 维
                logger.warning(f"OpenAI 向量维度 {embedding.shape[0]} 与现有索引维度 384 不匹配，降级使用本地模型")
                return self.encode_query_local(query)
            
            return embedding
            
        except Exception as e:
            logger.error(f"OpenAI 查询向量化失败: {str(e)}")
            # 降级使用本地 embedding 服务
            logger.info("降级使用本地 embedding 服务")
            return self.encode_query_local(query)
    
    def encode_query_local(self, query: str) -> np.ndarray:
        """
        使用本地 embedding 模型将查询文本向量化
        
        Args:
            query (str): 查询文本
            
        Returns:
            np.ndarray: 查询向量
        """
        try:
            logger.info(f"使用本地模型编码查询: '{query[:50]}...'")
            embedding = self.embedding_service.encode_text(query)
            logger.info(f"本地查询向量化完成，维度: {embedding.shape}")
            return embedding
            
        except Exception as e:
            logger.error(f"本地查询向量化失败: {str(e)}")
            raise Exception(f"查询向量化失败: {str(e)}")
    
    def retrieve_from_file(self, query: str, file_id: str, top_k: int = None, 
                          min_similarity: float = None, use_openai: bool = True) -> List[Dict[str, Any]]:
        """
        从指定文件的向量库中检索相关段落
        
        Args:
            query (str): 查询文本
            file_id (str): 文件ID
            top_k (int): 返回的最相关结果数量
            min_similarity (float): 最小相似度阈值
            use_openai (bool): 是否使用 OpenAI embedding
            
        Returns:
            List[Dict[str, Any]]: 检索结果列表
        """
        try:
            # 使用默认参数
            if top_k is None:
                top_k = self.top_k
            if min_similarity is None:
                min_similarity = self.min_similarity
            
            logger.info(f"从文件 {file_id} 检索相关段落，top_k={top_k}")
            
            # 检查索引是否存在
            index_info = self.vector_store.get_index_info(file_id)
            if not index_info.get('exists', False):
                logger.warning(f"文件 {file_id} 的向量索引不存在")
                return []
            
            # 将查询向量化
            if use_openai and Config.OPENAI_API_KEY:
                query_vector = self.encode_query_openai(query)
            else:
                query_vector = self.encode_query_local(query)
            
            # 在向量库中搜索
            results = self.vector_store.search(file_id, query_vector, top_k)
            
            # 过滤低相似度结果
            filtered_results = []
            for result in results:
                similarity = result.get('similarity', 0)
                if similarity >= min_similarity:
                    # 添加查询信息到结果中
                    result['query'] = query
                    result['file_id'] = file_id
                    filtered_results.append(result)
            
            logger.info(f"检索完成，返回 {len(filtered_results)} 个相关段落")
            return filtered_results
            
        except Exception as e:
            logger.error(f"文件检索失败: {str(e)}")
            return []
    
    def retrieve_from_multiple_files(self, query: str, file_ids: List[str], 
                                   top_k_per_file: int = None, min_similarity: float = None,
                                   use_openai: bool = True) -> Dict[str, List[Dict[str, Any]]]:
        """
        从多个文件的向量库中检索相关段落
        
        Args:
            query (str): 查询文本
            file_ids (List[str]): 文件ID列表
            top_k_per_file (int): 每个文件返回的最相关结果数量
            min_similarity (float): 最小相似度阈值
            use_openai (bool): 是否使用 OpenAI embedding
            
        Returns:
            Dict[str, List[Dict[str, Any]]]: 按文件ID分组的检索结果
        """
        try:
            # 使用默认参数
            if top_k_per_file is None:
                top_k_per_file = self.top_k
            if min_similarity is None:
                min_similarity = self.min_similarity
            
            logger.info(f"从 {len(file_ids)} 个文件检索相关段落")
            
            # 将查询向量化（只需要做一次）
            if use_openai and Config.OPENAI_API_KEY:
                query_vector = self.encode_query_openai(query)
            else:
                query_vector = self.encode_query_local(query)
            
            # 在多个文件中搜索
            all_results = {}
            for file_id in file_ids:
                try:
                    results = self.vector_store.search(file_id, query_vector, top_k_per_file)
                    all_results[file_id] = results
                except Exception as e:
                    logger.error(f"搜索文件 {file_id} 失败: {str(e)}")
                    all_results[file_id] = []
            
            # 过滤低相似度结果并添加查询信息
            filtered_results = {}
            total_results = 0
            
            for file_id, results in all_results.items():
                filtered = []
                for result in results:
                    similarity = result.get('similarity', 0)
                    if similarity >= min_similarity:
                        result['query'] = query
                        result['file_id'] = file_id
                        filtered.append(result)
                
                filtered_results[file_id] = filtered
                total_results += len(filtered)
            
            logger.info(f"多文件检索完成，总共返回 {total_results} 个相关段落")
            return filtered_results
            
        except Exception as e:
            logger.error(f"多文件检索失败: {str(e)}")
            return {}
    
    def retrieve_all_available(self, query: str, top_k_total: int = None, 
                             min_similarity: float = None, use_openai: bool = True) -> List[Dict[str, Any]]:
        """
        从所有可用的向量库中检索相关段落
        
        Args:
            query (str): 查询文本
            top_k_total (int): 总共返回的最相关结果数量
            min_similarity (float): 最小相似度阈值
            use_openai (bool): 是否使用 OpenAI embedding
            
        Returns:
            List[Dict[str, Any]]: 所有检索结果，按相似度排序
        """
        try:
            # 使用默认参数
            if top_k_total is None:
                top_k_total = self.top_k * 2  # 从所有文件检索时适当增加数量
            if min_similarity is None:
                min_similarity = self.min_similarity
            
            logger.info(f"从所有可用文件检索相关段落，top_k={top_k_total}")
            
            # 获取所有可用的索引
            all_indices = self.vector_store.list_all_indices()
            if not all_indices:
                logger.warning("没有可用的向量索引")
                return []
            
            file_ids = [idx['file_id'] for idx in all_indices]
            logger.info(f"发现 {len(file_ids)} 个可用索引")
            
            # 从所有文件检索
            per_file_top_k = max(1, top_k_total // len(file_ids))  # 平均分配
            multi_results = self.retrieve_from_multiple_files(
                query, file_ids, per_file_top_k, min_similarity, use_openai
            )
            
            # 合并所有结果
            all_results = []
            for file_id, results in multi_results.items():
                all_results.extend(results)
            
            # 按相似度排序
            all_results.sort(key=lambda x: x.get('similarity', 0), reverse=True)
            
            # 过滤低质量内容
            quality_filtered_results = []
            for result in all_results:
                metadata = result.get('metadata', {})
                text = metadata.get('text_preview', '') or metadata.get('text', '')
                similarity = result.get('similarity', 0)
                
                # 跳过明显的低质量内容
                is_journal_header = ('===' in text and 'ISSN' in text and len(text) < 500)
                is_too_short = len(text.strip()) < 20
                is_low_similarity = similarity < 0.02  # 相似度过低（放宽标准）
                
                if is_journal_header or is_too_short or is_low_similarity:
                    logger.debug(f"跳过低质量内容: 相似度={similarity:.3f}, 长度={len(text)}")
                    continue
                
                quality_filtered_results.append(result)
            
            # 截取 top_k_total 个结果
            final_results = quality_filtered_results[:top_k_total]
            
            logger.info(f"全局检索完成，返回 {len(final_results)} 个最相关段落")
            return final_results
            
        except Exception as e:
            logger.error(f"全局检索失败: {str(e)}")
            return []
    
    def format_context_for_rag(self, retrieval_results: List[Dict[str, Any]], 
                              max_length: int = None) -> Tuple[str, List[Dict[str, Any]]]:
        """
        将检索结果格式化为 RAG 上下文
        
        Args:
            retrieval_results (List[Dict[str, Any]]): 检索结果
            max_length (int): 最大上下文长度
            
        Returns:
            Tuple[str, List[Dict[str, Any]]]: (格式化的上下文, 被引用的段落信息)
        """
        try:
            if max_length is None:
                max_length = Config.RAG_MAX_CONTEXT_LENGTH
            
            if not retrieval_results:
                return "没有找到相关资料。", []
            
            context_parts = []
            cited_segments = []
            current_length = 0
            
            for i, result in enumerate(retrieval_results):
                metadata = result.get('metadata', {})
                text = metadata.get('text_preview', '') or metadata.get('text', '')
                file_name = metadata.get('file_name', '未知文档')
                segment_id = metadata.get('segment_id', f'段落{i+1}')
                similarity = result.get('similarity', 0)
                
                # 格式化段落信息
                segment_info = {
                    'index': i + 1,
                    'text': text,
                    'file_name': file_name,
                    'segment_id': segment_id,
                    'similarity': similarity
                }
                
                # 构建上下文文本
                context_text = f"{i+1}. {text}"
                
                # 检查长度限制
                if current_length + len(context_text) > max_length:
                    logger.info(f"达到上下文长度限制 {max_length}，截止到第 {i} 个段落")
                    break
                
                context_parts.append(context_text)
                cited_segments.append(segment_info)
                current_length += len(context_text)
            
            # 组合最终上下文
            formatted_context = "\\n\\n".join(context_parts)
            
            logger.info(f"上下文格式化完成，包含 {len(cited_segments)} 个段落，总长度: {len(formatted_context)}")
            return formatted_context, cited_segments
            
        except Exception as e:
            logger.error(f"上下文格式化失败: {str(e)}")
            return "资料处理出现错误。", []
    
    def get_service_status(self) -> Dict[str, Any]:
        """
        获取检索服务状态
        
        Returns:
            Dict[str, Any]: 服务状态信息
        """
        try:
            # 检查 OpenAI 连接
            openai_available = bool(Config.OPENAI_API_KEY)
            
            # 检查本地 embedding 服务
            local_embedding_available = True
            try:
                model_info = self.embedding_service.get_model_info()
                local_embedding_available = model_info.get('is_loaded', False)
            except:
                local_embedding_available = False
            
            # 检查向量库
            all_indices = self.vector_store.list_all_indices()
            
            return {
                'service_status': 'healthy',
                'openai_available': openai_available,
                'local_embedding_available': local_embedding_available,
                'embedding_model': self.embedding_model,
                'total_indices': len(all_indices),
                'available_files': [idx['file_id'] for idx in all_indices],
                'config': {
                    'top_k': self.top_k,
                    'min_similarity': self.min_similarity,
                    'max_context_length': Config.RAG_MAX_CONTEXT_LENGTH
                }
            }
            
        except Exception as e:
            logger.error(f"获取服务状态失败: {str(e)}")
            return {
                'service_status': 'unhealthy',
                'error': str(e)
            }


# 全局单例实例
_retriever_service = None


def get_retriever_service() -> RetrieverService:
    """
    获取检索服务单例
    
    Returns:
        RetrieverService: 检索服务实例
    """
    global _retriever_service
    
    if _retriever_service is None:
        logger.info("初始化检索服务单例")
        _retriever_service = RetrieverService()
    
    return _retriever_service


if __name__ == "__main__":
    # 测试代码
    import logging
    logging.basicConfig(level=logging.INFO)
    
    retriever = RetrieverService()
    
    # 测试查询向量化
    test_query = "化工反应的基本原理是什么？"
    
    try:
        # 测试 OpenAI embedding
        print("测试 OpenAI embedding:")
        openai_vector = retriever.encode_query_openai(test_query)
        print(f"OpenAI 向量维度: {openai_vector.shape}")
        
        # 测试本地 embedding
        print("\\n测试本地 embedding:")
        local_vector = retriever.encode_query_local(test_query)
        print(f"本地向量维度: {local_vector.shape}")
        
        # 测试服务状态
        print("\\n服务状态:")
        status = retriever.get_service_status()
        print(f"状态: {status}")
        
    except Exception as e:
        print(f"测试失败: {e}")