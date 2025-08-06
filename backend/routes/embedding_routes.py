# -*- coding: utf-8 -*-
"""
embedding_routes.py
Embedding 和向量库相关的 API 路由

提供以下接口：
1. POST /api/embed/:file_id - 为指定文件生成 embedding
2. GET /api/embed/info/:file_id - 获取索引信息
3. DELETE /api/embed/:file_id - 删除指定文件的索引
4. GET /api/embed/list - 列出所有索引
5. POST /api/embed/search/:file_id - 向量搜索

作者：AI Assistant
日期：2025-08-07
"""

import logging
from flask import Blueprint, request, jsonify
from typing import Dict, Any

# 导入业务逻辑控制器
from controllers.embedding_controller import EmbeddingController

logger = logging.getLogger(__name__)

# 创建 Blueprint
embedding_bp = Blueprint('embedding', __name__, url_prefix='/api/embed')

# 初始化控制器
embedding_controller = EmbeddingController()


@embedding_bp.route('/<file_id>', methods=['POST'])
def create_embeddings(file_id: str):
    """
    为指定文件的所有段落生成 embedding 并构建向量索引
    
    URL: POST /api/embed/<file_id>
    
    Args:
        file_id (str): 文件ID或解析记录ID
        
    Body (可选):
        {
            "recreate": false,     // 是否强制重新创建索引
            "batch_size": 32       // 批处理大小
        }
    
    Returns:
        {
            "success": true,
            "code": 200,
            "msg": "Embedding 创建成功",
            "data": {
                "file_id": "xxx",
                "embedded_count": 30,
                "embedding_dimension": 384,
                "processing_time": 12.5,
                "index_info": {...}
            }
        }
    """
    try:
        logger.info(f"创建 embedding API 被调用，文件ID: {file_id}")
        
        # 获取请求参数
        data = request.get_json() or {}
        recreate = data.get('recreate', False)
        batch_size = data.get('batch_size', 32)
        
        # 调用控制器处理
        result = embedding_controller.create_embeddings(
            file_id=file_id,
            recreate=recreate,
            batch_size=batch_size
        )
        
        if result['success']:
            return jsonify({
                "success": True,
                "code": 200,
                "msg": "Embedding 创建成功",
                "data": result['data']
            }), 200
        else:
            return jsonify({
                "success": False,
                "code": 400,
                "msg": result['error'],
                "data": None
            }), 400
            
    except Exception as e:
        logger.error(f"创建 embedding API 异常: {str(e)}")
        return jsonify({
            "success": False,
            "code": 500,
            "msg": f"服务器内部错误: {str(e)}",
            "data": None
        }), 500


@embedding_bp.route('/info/<file_id>', methods=['GET'])
def get_embedding_info(file_id: str):
    """
    获取指定文件的 embedding 索引信息
    
    URL: GET /api/embed/info/<file_id>
    
    Args:
        file_id (str): 文件ID
        
    Returns:
        {
            "success": true,
            "code": 200,
            "msg": "获取索引信息成功",
            "data": {
                "exists": true,
                "file_id": "xxx",
                "vector_count": 30,
                "embedding_dimension": 384,
                "index_size_mb": 1.2,
                "created_at": "2025-08-07T10:30:00"
            }
        }
    """
    try:
        logger.info(f"获取 embedding 信息API 被调用，文件ID: {file_id}")
        
        # 调用控制器处理
        result = embedding_controller.get_embedding_info(file_id)
        
        return jsonify({
            "success": True,
            "code": 200,
            "msg": "获取索引信息成功",
            "data": result
        }), 200
        
    except Exception as e:
        logger.error(f"获取 embedding 信息API 异常: {str(e)}")
        return jsonify({
            "success": False,
            "code": 500,
            "msg": f"服务器内部错误: {str(e)}",
            "data": None
        }), 500


@embedding_bp.route('/<file_id>', methods=['DELETE'])
def delete_embeddings(file_id: str):
    """
    删除指定文件的 embedding 索引
    
    URL: DELETE /api/embed/<file_id>
    
    Args:
        file_id (str): 文件ID
        
    Returns:
        {
            "success": true,
            "code": 200,
            "msg": "索引删除成功",
            "data": {
                "file_id": "xxx",
                "deleted": true
            }
        }
    """
    try:
        logger.info(f"删除 embedding API 被调用，文件ID: {file_id}")
        
        # 调用控制器处理
        result = embedding_controller.delete_embeddings(file_id)
        
        if result['success']:
            return jsonify({
                "success": True,
                "code": 200,
                "msg": "索引删除成功",
                "data": result['data']
            }), 200
        else:
            return jsonify({
                "success": False,
                "code": 400,
                "msg": result['error'],
                "data": None
            }), 400
            
    except Exception as e:
        logger.error(f"删除 embedding API 异常: {str(e)}")
        return jsonify({
            "success": False,
            "code": 500,
            "msg": f"服务器内部错误: {str(e)}",
            "data": None
        }), 500


@embedding_bp.route('/list', methods=['GET'])
def list_all_embeddings():
    """
    列出所有的 embedding 索引
    
    URL: GET /api/embed/list
    
    Returns:
        {
            "success": true,
            "code": 200,
            "msg": "获取索引列表成功",
            "data": {
                "total": 5,
                "indices": [
                    {
                        "file_id": "xxx",
                        "vector_count": 30,
                        "embedding_dimension": 384,
                        "index_size_mb": 1.2
                    },
                    ...
                ]
            }
        }
    """
    try:
        logger.info(f"列出所有 embedding API 被调用")
        
        # 调用控制器处理
        result = embedding_controller.list_all_embeddings()
        
        return jsonify({
            "success": True,
            "code": 200,
            "msg": "获取索引列表成功",
            "data": result
        }), 200
        
    except Exception as e:
        logger.error(f"列出所有 embedding API 异常: {str(e)}")
        return jsonify({
            "success": False,
            "code": 500,
            "msg": f"服务器内部错误: {str(e)}",
            "data": None
        }), 500


@embedding_bp.route('/search/<file_id>', methods=['POST'])
def search_embeddings(file_id: str):
    """
    在指定文件的向量索引中搜索相似内容
    
    URL: POST /api/embed/search/<file_id>
    
    Args:
        file_id (str): 文件ID
        
    Body:
        {
            "query": "化工反应的基本原理",    // 查询文本
            "top_k": 5,                    // 返回结果数量
            "min_score": 0.0               // 最小相似度阈值
        }
    
    Returns:
        {
            "success": true,
            "code": 200,
            "msg": "搜索完成",
            "data": {
                "query": "化工反应的基本原理",
                "file_id": "xxx",
                "total_results": 3,
                "search_time": 0.05,
                "results": [
                    {
                        "rank": 1,
                        "score": 0.89,
                        "similarity": 0.89,
                        "metadata": {
                            "segment_id": "xxx",
                            "text_preview": "化工反应...",
                            "file_name": "xxx.pdf",
                            "order": 1
                        }
                    },
                    ...
                ]
            }
        }
    """
    try:
        logger.info(f"搜索 embedding API 被调用，文件ID: {file_id}")
        
        # 验证请求数据
        data = request.get_json()
        if not data or 'query' not in data:
            return jsonify({
                "success": False,
                "code": 400,
                "msg": "缺少查询文本",
                "data": None
            }), 400
        
        query = data['query']
        top_k = data.get('top_k', 5)
        min_score = data.get('min_score', 0.0)
        
        # 验证参数
        if not query.strip():
            return jsonify({
                "success": False,
                "code": 400,
                "msg": "查询文本不能为空",
                "data": None
            }), 400
        
        if top_k <= 0 or top_k > 100:
            return jsonify({
                "success": False,
                "code": 400,
                "msg": "top_k 必须在 1-100 之间",
                "data": None
            }), 400
        
        # 调用控制器处理
        result = embedding_controller.search_embeddings(
            file_id=file_id,
            query=query,
            top_k=top_k,
            min_score=min_score
        )
        
        if result['success']:
            return jsonify({
                "success": True,
                "code": 200,
                "msg": "搜索完成",
                "data": result['data']
            }), 200
        else:
            return jsonify({
                "success": False,
                "code": 400,
                "msg": result['error'],
                "data": None
            }), 400
            
    except Exception as e:
        logger.error(f"搜索 embedding API 异常: {str(e)}")
        return jsonify({
            "success": False,
            "code": 500,
            "msg": f"服务器内部错误: {str(e)}",
            "data": None
        }), 500


@embedding_bp.route('/search/multi', methods=['POST'])
def search_multiple_files():
    """
    在多个文件的向量索引中搜索相似内容
    
    URL: POST /api/embed/search/multi
    
    Body:
        {
            "query": "化工反应的基本原理",      // 查询文本
            "file_ids": ["file1", "file2"],   // 文件ID列表
            "top_k": 5,                       // 每个文件返回结果数量
            "min_score": 0.0                  // 最小相似度阈值
        }
    
    Returns:
        {
            "success": true,
            "code": 200,
            "msg": "多文件搜索完成",
            "data": {
                "query": "化工反应的基本原理",
                "searched_files": 2,
                "total_results": 8,
                "search_time": 0.12,
                "results": {
                    "file1": [...],
                    "file2": [...]
                }
            }
        }
    """
    try:
        logger.info(f"多文件搜索 embedding API 被调用")
        
        # 验证请求数据
        data = request.get_json()
        if not data or 'query' not in data or 'file_ids' not in data:
            return jsonify({
                "success": False,
                "code": 400,
                "msg": "缺少查询文本或文件ID列表",
                "data": None
            }), 400
        
        query = data['query']
        file_ids = data['file_ids']
        top_k = data.get('top_k', 5)
        min_score = data.get('min_score', 0.0)
        
        # 验证参数
        if not query.strip():
            return jsonify({
                "success": False,
                "code": 400,
                "msg": "查询文本不能为空",
                "data": None
            }), 400
        
        if not isinstance(file_ids, list) or len(file_ids) == 0:
            return jsonify({
                "success": False,
                "code": 400,
                "msg": "文件ID列表不能为空",
                "data": None
            }), 400
        
        # 调用控制器处理
        result = embedding_controller.search_multiple_files(
            file_ids=file_ids,
            query=query,
            top_k=top_k,
            min_score=min_score
        )
        
        if result['success']:
            return jsonify({
                "success": True,
                "code": 200,
                "msg": "多文件搜索完成",
                "data": result['data']
            }), 200
        else:
            return jsonify({
                "success": False,
                "code": 400,
                "msg": result['error'],
                "data": None
            }), 400
            
    except Exception as e:
        logger.error(f"多文件搜索 embedding API 异常: {str(e)}")
        return jsonify({
            "success": False,
            "code": 500,
            "msg": f"服务器内部错误: {str(e)}",
            "data": None
        }), 500


@embedding_bp.route('/health', methods=['GET'])
def health_check():
    """
    健康检查接口
    
    URL: GET /api/embed/health
    
    Returns:
        {
            "success": true,
            "code": 200,
            "msg": "Embedding 服务正常",
            "data": {
                "service_status": "healthy",
                "model_loaded": true,
                "model_info": {...}
            }
        }
    """
    try:
        # 调用控制器处理
        result = embedding_controller.health_check()
        
        return jsonify({
            "success": True,
            "code": 200,
            "msg": "Embedding 服务正常",
            "data": result
        }), 200
        
    except Exception as e:
        logger.error(f"健康检查API 异常: {str(e)}")
        return jsonify({
            "success": False,
            "code": 500,
            "msg": f"服务器内部错误: {str(e)}",
            "data": None
        }), 500


# 错误处理
@embedding_bp.errorhandler(404)
def not_found(error):
    """处理 404 错误"""
    return jsonify({
        "success": False,
        "code": 404,
        "msg": "API 接口不存在",
        "data": None
    }), 404


@embedding_bp.errorhandler(405)
def method_not_allowed(error):
    """处理 405 错误"""
    return jsonify({
        "success": False,
        "code": 405,
        "msg": "HTTP 方法不允许",
        "data": None
    }), 405


@embedding_bp.errorhandler(500)
def internal_error(error):
    """处理 500 错误"""
    return jsonify({
        "success": False,
        "code": 500,
        "msg": "服务器内部错误",
        "data": None
    }), 500