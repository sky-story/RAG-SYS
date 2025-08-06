# parse_routes.py - 文档解析路由
# 定义文档解析相关的 API 端点
# 包括本地文件解析、数据库文件解析、历史查看、内容下载等接口

from flask import Blueprint, request, jsonify, send_file
from werkzeug.exceptions import RequestEntityTooLarge
import logging
import io

from controllers.parse_controller import parse_controller

# 配置日志
logger = logging.getLogger(__name__)

# 创建蓝图
parse_bp = Blueprint('parse', __name__, url_prefix='/api/parse')

@parse_bp.route('/local', methods=['POST'])
def parse_local_file():
    """
    解析本地上传文件
    
    接收 multipart/form-data 格式的文件上传
    
    Returns:
        JSON: 解析结果
    """
    try:
        # 检查是否有文件上传
        if 'file' not in request.files:
            return jsonify({
                "success": False,
                "error": "未找到文件字段"
            }), 400
        
        file = request.files['file']
        
        # 检查文件是否为空
        if file.filename == '':
            return jsonify({
                "success": False,
                "error": "未选择文件"
            }), 400
        
        # 调用控制器解析文件
        success, result = parse_controller.parse_uploaded_file(file)
        
        if success:
            return jsonify({
                "success": True,
                "data": result,
                "message": result.get("message", "文件解析成功")
            }), 200
        else:
            return jsonify({
                "success": False,
                "error": result.get("error", "解析失败")
            }), 400
            
    except RequestEntityTooLarge:
        return jsonify({
            "success": False,
            "error": "文件大小超过限制"
        }), 413
    except Exception as e:
        logger.error(f"解析本地文件API异常: {str(e)}")
        return jsonify({
            "success": False,
            "error": f"服务器内部错误: {str(e)}"
        }), 500

@parse_bp.route('/database/<file_id>', methods=['POST'])
def parse_database_file(file_id):
    """
    解析数据库中的已有文件
    
    Args:
        file_id (str): 文件 ID
    
    Returns:
        JSON: 解析结果
    """
    try:
        if not file_id:
            return jsonify({
                "success": False,
                "error": "文件 ID 不能为空"
            }), 400
        
        # 调用控制器解析文件
        success, result = parse_controller.parse_existing_file(file_id)
        
        if success:
            return jsonify({
                "success": True,
                "data": result,
                "message": result.get("message", "文件解析成功")
            }), 200
        else:
            return jsonify({
                "success": False,
                "error": result.get("error", "解析失败")
            }), 400
            
    except Exception as e:
        logger.error(f"解析数据库文件API异常: {str(e)}")
        return jsonify({
            "success": False,
            "error": f"服务器内部错误: {str(e)}"
        }), 500

@parse_bp.route('/history', methods=['GET'])
def get_parse_history():
    """
    获取解析历史记录
    
    Query Parameters:
        limit (int): 限制返回数量，默认100
        offset (int): 偏移量，默认0
    
    Returns:
        JSON: 解析历史记录列表
    """
    try:
        # 获取查询参数
        limit = request.args.get('limit', 100, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        # 参数验证
        if limit <= 0 or limit > 1000:
            limit = 100
        if offset < 0:
            offset = 0
        
        # 调用控制器获取历史记录
        success, result = parse_controller.get_parse_history(limit, offset)
        
        if success:
            return jsonify({
                "success": True,
                "data": result
            }), 200
        else:
            return jsonify({
                "success": False,
                "error": result.get("error", "获取历史记录失败")
            }), 400
            
    except Exception as e:
        logger.error(f"获取解析历史API异常: {str(e)}")
        return jsonify({
            "success": False,
            "error": f"服务器内部错误: {str(e)}"
        }), 500

@parse_bp.route('/<parse_id>', methods=['GET'])
def get_parsed_content(parse_id):
    """
    获取解析内容详情
    
    Args:
        parse_id (str): 解析记录 ID
    
    Returns:
        JSON: 解析内容详情
    """
    try:
        if not parse_id:
            return jsonify({
                "success": False,
                "error": "解析记录 ID 不能为空"
            }), 400
        
        # 调用控制器获取解析内容
        success, result = parse_controller.get_parsed_content(parse_id)
        
        if success:
            return jsonify({
                "success": True,
                "data": result
            }), 200
        else:
            return jsonify({
                "success": False,
                "error": result.get("error", "获取解析内容失败")
            }), 404
            
    except Exception as e:
        logger.error(f"获取解析内容API异常: {str(e)}")
        return jsonify({
            "success": False,
            "error": f"服务器内部错误: {str(e)}"
        }), 500

@parse_bp.route('/<parse_id>', methods=['DELETE'])
def delete_parse_record(parse_id):
    """
    删除解析记录
    
    Args:
        parse_id (str): 解析记录 ID
    
    Returns:
        JSON: 删除结果
    """
    try:
        if not parse_id:
            return jsonify({
                "success": False,
                "error": "解析记录 ID 不能为空"
            }), 400
        
        # 调用控制器删除记录
        success, result = parse_controller.delete_parse_record(parse_id)
        
        if success:
            return jsonify({
                "success": True,
                "message": result.get("message", "解析记录删除成功")
            }), 200
        else:
            return jsonify({
                "success": False,
                "error": result.get("error", "删除解析记录失败")
            }), 404
            
    except Exception as e:
        logger.error(f"删除解析记录API异常: {str(e)}")
        return jsonify({
            "success": False,
            "error": f"服务器内部错误: {str(e)}"
        }), 500

@parse_bp.route('/download/<parse_id>', methods=['GET'])
def download_parsed_text(parse_id):
    """
    下载解析文本
    
    Args:
        parse_id (str): 解析记录 ID
    
    Returns:
        File: 文本文件
    """
    try:
        if not parse_id:
            return jsonify({
                "success": False,
                "error": "解析记录 ID 不能为空"
            }), 400
        
        # 调用控制器获取文本内容
        success, result = parse_controller.download_parsed_text(parse_id)
        
        if success:
            # 创建内存文件对象
            file_data = io.BytesIO()
            file_data.write(result["content"].encode('utf-8'))
            file_data.seek(0)
            
            return send_file(
                file_data,
                mimetype=result["mimetype"],
                as_attachment=True,
                download_name=result["filename"]
            )
        else:
            return jsonify({
                "success": False,
                "error": result.get("error", "下载失败")
            }), 404
            
    except Exception as e:
        logger.error(f"下载解析文本API异常: {str(e)}")
        return jsonify({
            "success": False,
            "error": f"服务器内部错误: {str(e)}"
        }), 500

@parse_bp.route('/search', methods=['GET'])
def search_parsed_texts():
    """
    搜索解析文本
    
    Query Parameters:
        q (str): 搜索关键词
        limit (int): 限制返回数量，默认50
    
    Returns:
        JSON: 搜索结果
    """
    try:
        # 获取查询参数
        keyword = request.args.get('q', '').strip()
        limit = request.args.get('limit', 50, type=int)
        
        # 参数验证
        if not keyword:
            return jsonify({
                "success": False,
                "error": "搜索关键词不能为空"
            }), 400
        
        if limit <= 0 or limit > 200:
            limit = 50
        
        # 调用控制器搜索
        success, result = parse_controller.search_parsed_texts(keyword, limit)
        
        if success:
            return jsonify({
                "success": True,
                "data": result
            }), 200
        else:
            return jsonify({
                "success": False,
                "error": result.get("error", "搜索失败")
            }), 400
            
    except Exception as e:
        logger.error(f"搜索解析文本API异常: {str(e)}")
        return jsonify({
            "success": False,
            "error": f"服务器内部错误: {str(e)}"
        }), 500

# 错误处理器
@parse_bp.errorhandler(413)
def too_large(e):
    """处理文件过大错误"""
    return jsonify({
        "success": False,
        "error": "上传文件过大，请选择较小的文件"
    }), 413

@parse_bp.errorhandler(400)
def bad_request(e):
    """处理请求错误"""
    return jsonify({
        "success": False,
        "error": "请求格式错误"
    }), 400

@parse_bp.errorhandler(404)
def not_found(e):
    """处理资源不存在错误"""
    return jsonify({
        "success": False,
        "error": "请求的资源不存在"
    }), 404

@parse_bp.errorhandler(500)
def internal_error(e):
    """处理服务器内部错误"""
    return jsonify({
        "success": False,
        "error": "服务器内部错误，请稍后重试"
    }), 500