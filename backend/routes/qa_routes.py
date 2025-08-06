# -*- coding: utf-8 -*-
"""
qa_routes.py
基于检索增强生成（RAG）的问答 API 路由

提供以下接口：
1. POST /api/qa/rag - RAG 问答接口
2. GET /api/qa/health - 问答服务健康检查
3. GET /api/qa/available-files - 获取可用于问答的文件列表

作者：AI Assistant
日期：2025-08-07
"""

import logging
from flask import Blueprint, request, jsonify
from typing import Dict, Any, List
import time

# 导入业务逻辑服务
from services.retriever import get_retriever_service
from services.generator import get_generator_service

logger = logging.getLogger(__name__)

# 创建 Blueprint
qa_bp = Blueprint('qa', __name__, url_prefix='/api/qa')

# 初始化服务
retriever_service = get_retriever_service()
generator_service = get_generator_service()


@qa_bp.route('/rag', methods=['POST'])
def rag_qa():
    """
    基于检索增强生成的问答接口
    
    URL: POST /api/qa/rag
    
    Body:
        {
            "question": "化工反应器设计需要考虑哪些因素？",  // 必需：用户问题
            "file_ids": ["file1", "file2"],                  // 可选：指定搜索的文件ID列表
            "top_k": 3,                                      // 可选：检索的段落数量，默认3
            "min_similarity": 0.0,                          // 可选：最小相似度阈值，默认0.0
            "use_openai_embedding": true,                    // 可选：是否使用OpenAI embedding，默认true
            "temperature": 0.1,                             // 可选：生成温度，默认0.1
            "max_tokens": 1000                              // 可选：最大生成token数，默认1000
        }
    
    Returns:
        {
            "success": true,
            "code": 200,
            "msg": "RAG 问答成功",
            "data": {
                "question": "化工反应器设计需要考虑哪些因素？",
                "answer": "根据提供的资料...",
                "response_type": "rag_based",
                "generation_time": 2.35,
                "retrieval_results": {...},
                "generation_results": {...},
                "quality_assessment": {...}
            }
        }
    """
    try:
        start_time = time.time()
        logger.info("RAG 问答 API 被调用")
        
        # 验证请求数据
        data = request.get_json()
        if not data or 'question' not in data:
            return jsonify({
                "success": False,
                "code": 400,
                "msg": "缺少必需参数 'question'",
                "data": None
            }), 400
        
        question = data['question'].strip()
        if not question:
            return jsonify({
                "success": False,
                "code": 400,
                "msg": "问题内容不能为空",
                "data": None
            }), 400
        
        # 获取可选参数
        file_ids = data.get('file_ids', [])
        top_k = data.get('top_k', 3)
        min_similarity = data.get('min_similarity', 0.0)
        use_openai_embedding = data.get('use_openai_embedding', True)
        temperature = data.get('temperature', 0.1)
        max_tokens = data.get('max_tokens', 1000)
        
        # 参数验证
        if top_k <= 0 or top_k > 20:
            return jsonify({
                "success": False,
                "code": 400,
                "msg": "top_k 必须在 1-20 之间",
                "data": None
            }), 400
        
        logger.info(f"处理问题: '{question[:50]}...'")
        
        # 步骤1: 检索相关文档段落
        retrieval_start_time = time.time()
        
        if file_ids:
            # 从指定文件检索
            logger.info(f"从指定的 {len(file_ids)} 个文件检索")
            retrieval_results = retriever_service.retrieve_from_multiple_files(
                query=question,
                file_ids=file_ids,
                top_k_per_file=max(1, top_k // len(file_ids)),
                min_similarity=min_similarity,
                use_openai=use_openai_embedding
            )
            
            # 合并多文件结果
            all_segments = []
            for file_id, segments in retrieval_results.items():
                all_segments.extend(segments)
            
            # 按相似度排序并取 top_k
            all_segments.sort(key=lambda x: x.get('similarity', 0), reverse=True)
            final_segments = all_segments[:top_k]
        else:
            # 从所有可用文件检索
            logger.info("从所有可用文件检索")
            final_segments = retriever_service.retrieve_all_available(
                query=question,
                top_k_total=top_k,
                min_similarity=min_similarity,
                use_openai=use_openai_embedding
            )
        
        retrieval_time = time.time() - retrieval_start_time
        
        # 步骤2: 格式化检索上下文
        context, cited_segments = retriever_service.format_context_for_rag(final_segments)
        
        logger.info(f"检索完成，找到 {len(cited_segments)} 个相关段落，耗时 {retrieval_time:.3f}s")
        
        # 步骤3: 使用 OpenAI 生成回答
        generation_result = generator_service.generate_answer(
            question=question,
            context=context,
            cited_segments=cited_segments,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        if not generation_result['success']:
            return jsonify({
                "success": False,
                "code": 500,
                "msg": f"回答生成失败: {generation_result['error']}",
                "data": None
            }), 500
        
        # 步骤4: 评估回答质量
        quality_assessment = generator_service.evaluate_answer_quality(
            question=question,
            answer=generation_result['answer'],
            context=context
        )
        
        # 步骤5: 构建响应数据
        total_time = time.time() - start_time
        
        response_data = {
            "question": question,
            "answer": generation_result['answer'],
            "response_type": generation_result['response_type'],
            "total_time": round(total_time, 3),
            "retrieval_results": {
                "total_segments": len(final_segments),
                "used_segments": len(cited_segments),
                "search_time": round(retrieval_time, 3),
                "min_similarity": min_similarity,
                "cited_segments": cited_segments
            },
            "generation_results": {
                "model": generation_result['model'],
                "generation_time": round(generation_result['generation_time'], 3),
                "token_usage": generation_result['token_usage'],
                "finish_reason": generation_result.get('finish_reason', 'unknown'),
                "temperature": temperature,
                "max_tokens": max_tokens
            },
            "quality_assessment": quality_assessment,
            "context_used": generation_result['context_used']
        }
        
        logger.info(f"RAG 问答完成，总耗时: {total_time:.3f}s")
        
        return jsonify({
            "success": True,
            "code": 200,
            "msg": "RAG 问答成功",
            "data": response_data
        }), 200
        
    except Exception as e:
        logger.error(f"RAG 问答 API 异常: {str(e)}")
        return jsonify({
            "success": False,
            "code": 500,
            "msg": f"服务器内部错误: {str(e)}",
            "data": None
        }), 500


@qa_bp.route('/health', methods=['GET'])
def qa_health_check():
    """
    问答服务健康检查
    
    URL: GET /api/qa/health
    """
    try:
        logger.info("问答服务健康检查")
        
        # 检查检索服务状态
        retriever_status = retriever_service.get_service_status()
        
        # 检查生成服务状态
        generator_status = generator_service.get_service_status()
        
        # 获取可用文件列表
        all_indices = retriever_service.vector_store.list_all_indices()
        available_files = [
            {
                'file_id': idx['file_id'],
                'vector_count': idx.get('vector_count', 0),
                'file_name': idx.get('file_name', 'Unknown')
            }
            for idx in all_indices
        ]
        
        # 综合服务状态
        overall_status = "healthy"
        if retriever_status.get('service_status') != 'healthy':
            overall_status = "degraded"
        if generator_status.get('service_status') != 'healthy':
            overall_status = "degraded" if overall_status == "healthy" else "unhealthy"
        
        return jsonify({
            "success": True,
            "code": 200,
            "msg": "问答服务状态检查完成",
            "data": {
                "service_status": overall_status,
                "retriever_status": retriever_status,
                "generator_status": generator_status,
                "available_files": available_files,
                "total_available_files": len(available_files)
            }
        }), 200
        
    except Exception as e:
        logger.error(f"问答服务健康检查异常: {str(e)}")
        return jsonify({
            "success": False,
            "code": 500,
            "msg": f"服务器内部错误: {str(e)}",
            "data": None
        }), 500


@qa_bp.route('/available-files', methods=['GET'])
def get_available_files():
    """
    获取可用于问答的文件列表
    
    URL: GET /api/qa/available-files
    """
    try:
        logger.info("获取可用文件列表")
        
        # 获取所有向量索引
        all_indices = retriever_service.vector_store.list_all_indices()
        
        return jsonify({
            "success": True,
            "code": 200,
            "msg": "获取文件列表成功",
            "data": {
                "total_files": len(all_indices),
                "files": all_indices
            }
        }), 200
        
    except Exception as e:
        logger.error(f"获取文件列表异常: {str(e)}")
        return jsonify({
            "success": False,
            "code": 500,
            "msg": f"服务器内部错误: {str(e)}",
            "data": None
        }), 500