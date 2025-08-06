# segment_routes.py - 文档分段路由
# 定义文档分段相关的 API 端点
# 包括文档分段、标签管理、推荐、搜索等接口

from flask import Blueprint, request, jsonify
import logging

from controllers.segment_controller import segment_controller

# 配置日志
logger = logging.getLogger(__name__)

# 创建蓝图
segment_bp = Blueprint('segment', __name__, url_prefix='/api/segment')

@segment_bp.route('/create/<file_id>', methods=['POST'])
def create_segments(file_id):
    """
    为指定文件创建分段
    
    Args:
        file_id (str): 文件 ID
    
    Returns:
        JSON: 分段结果
    """
    try:
        if not file_id:
            return jsonify({
                "code": 400,
                "msg": "文件 ID 不能为空",
                "data": None
            }), 400
        
        success, result = segment_controller.create_segments_from_file(file_id)
        
        if success:
            return jsonify(result), 200
        else:
            status_code = result.get("code", 500)
            return jsonify(result), status_code
            
    except Exception as e:
        logger.error(f"创建分段API异常: {str(e)}")
        return jsonify({
            "code": 500,
            "msg": f"服务器内部错误: {str(e)}",
            "data": None
        }), 500

@segment_bp.route('/file/<file_id>', methods=['GET'])
def get_file_segments(file_id):
    """
    获取文件的所有分段
    
    Args:
        file_id (str): 文件 ID
    
    Returns:
        JSON: 分段列表
    """
    try:
        if not file_id:
            return jsonify({
                "code": 400,
                "msg": "文件 ID 不能为空",
                "data": None
            }), 400
        
        success, result = segment_controller.get_file_segments(file_id)
        
        if success:
            return jsonify(result), 200
        else:
            status_code = result.get("code", 500)
            return jsonify(result), status_code
            
    except Exception as e:
        logger.error(f"获取文件分段API异常: {str(e)}")
        return jsonify({
            "code": 500,
            "msg": f"服务器内部错误: {str(e)}",
            "data": None
        }), 500

@segment_bp.route('/tag', methods=['POST'])
def update_segment_tags():
    """
    更新段落标签
    
    Request Body:
        {
            "segment_id": "段落ID",
            "tags": ["标签1", "标签2"]
        }
    
    Returns:
        JSON: 更新结果
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                "code": 400,
                "msg": "请求体不能为空",
                "data": None
            }), 400
        
        segment_id = data.get("segment_id", "").strip()
        tags = data.get("tags", [])
        
        success, result = segment_controller.update_segment_tags(segment_id, tags)
        
        if success:
            return jsonify(result), 200
        else:
            status_code = result.get("code", 400)
            return jsonify(result), status_code
            
    except Exception as e:
        logger.error(f"更新段落标签API异常: {str(e)}")
        return jsonify({
            "code": 500,
            "msg": f"服务器内部错误: {str(e)}",
            "data": None
        }), 500

@segment_bp.route('/tag/batch', methods=['POST'])
def batch_update_tags():
    """
    批量更新段落标签
    
    Request Body:
        {
            "updates": [
                {"segment_id": "段落ID1", "tags": ["标签1", "标签2"]},
                {"segment_id": "段落ID2", "tags": ["标签3", "标签4"]}
            ]
        }
    
    Returns:
        JSON: 批量更新结果
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                "code": 400,
                "msg": "请求体不能为空",
                "data": None
            }), 400
        
        updates = data.get("updates", [])
        
        success, result = segment_controller.batch_update_tags(updates)
        
        if success:
            return jsonify(result), 200
        else:
            status_code = result.get("code", 400)
            return jsonify(result), status_code
            
    except Exception as e:
        logger.error(f"批量更新标签API异常: {str(e)}")
        return jsonify({
            "code": 500,
            "msg": f"服务器内部错误: {str(e)}",
            "data": None
        }), 500

@segment_bp.route('/recommend/<segment_id>', methods=['GET'])
def recommend_tags(segment_id):
    """
    为段落推荐标签
    
    Args:
        segment_id (str): 段落 ID
    
    Returns:
        JSON: 推荐标签列表
    """
    try:
        if not segment_id:
            return jsonify({
                "code": 400,
                "msg": "段落 ID 不能为空",
                "data": None
            }), 400
        
        success, result = segment_controller.recommend_tags_for_segment(segment_id)
        
        if success:
            return jsonify(result), 200
        else:
            status_code = result.get("code", 404)
            return jsonify(result), status_code
            
    except Exception as e:
        logger.error(f"标签推荐API异常: {str(e)}")
        return jsonify({
            "code": 500,
            "msg": f"服务器内部错误: {str(e)}",
            "data": None
        }), 500

@segment_bp.route('/search', methods=['GET'])
def search_segments():
    """
    搜索段落
    
    Query Parameters:
        keyword (str): 搜索关键词
        limit (int): 限制返回数量，默认50
    
    Returns:
        JSON: 搜索结果
    """
    try:
        keyword = request.args.get('keyword', '').strip()
        limit = request.args.get('limit', 50, type=int)
        
        success, result = segment_controller.search_segments(keyword, limit)
        
        if success:
            return jsonify(result), 200
        else:
            status_code = result.get("code", 400)
            return jsonify(result), status_code
            
    except Exception as e:
        logger.error(f"搜索段落API异常: {str(e)}")
        return jsonify({
            "code": 500,
            "msg": f"服务器内部错误: {str(e)}",
            "data": None
        }), 500

@segment_bp.route('/tags', methods=['GET'])
def get_segments_by_tags():
    """
    根据标签查询段落
    
    Query Parameters:
        tags (str): 标签列表，用逗号分隔，如: "实验,安全,工艺"
        limit (int): 限制返回数量，默认50
    
    Returns:
        JSON: 查询结果
    """
    try:
        tags_str = request.args.get('tags', '').strip()
        limit = request.args.get('limit', 50, type=int)
        
        if not tags_str:
            return jsonify({
                "code": 400,
                "msg": "标签参数不能为空",
                "data": None
            }), 400
        
        # 解析标签列表
        tags = [tag.strip() for tag in tags_str.split(',') if tag.strip()]
        
        success, result = segment_controller.get_segments_by_tags(tags, limit)
        
        if success:
            return jsonify(result), 200
        else:
            status_code = result.get("code", 400)
            return jsonify(result), status_code
            
    except Exception as e:
        logger.error(f"按标签查询段落API异常: {str(e)}")
        return jsonify({
            "code": 500,
            "msg": f"服务器内部错误: {str(e)}",
            "data": None
        }), 500

@segment_bp.route('/stats', methods=['GET'])
def get_segment_stats():
    """
    获取分段统计信息
    
    Returns:
        JSON: 统计信息
    """
    try:
        success, result = segment_controller.get_segment_stats()
        
        if success:
            return jsonify(result), 200
        else:
            status_code = result.get("code", 500)
            return jsonify(result), status_code
            
    except Exception as e:
        logger.error(f"获取统计信息API异常: {str(e)}")
        return jsonify({
            "code": 500,
            "msg": f"服务器内部错误: {str(e)}",
            "data": None
        }), 500

@segment_bp.route('/file/<file_id>', methods=['DELETE'])
def delete_file_segments(file_id):
    """
    删除文件的所有分段
    
    Args:
        file_id (str): 文件 ID
    
    Returns:
        JSON: 删除结果
    """
    try:
        if not file_id:
            return jsonify({
                "code": 400,
                "msg": "文件 ID 不能为空",
                "data": None
            }), 400
        
        success, result = segment_controller.delete_file_segments(file_id)
        
        if success:
            return jsonify(result), 200
        else:
            status_code = result.get("code", 500)
            return jsonify(result), status_code
            
    except Exception as e:
        logger.error(f"删除文件分段API异常: {str(e)}")
        return jsonify({
            "code": 500,
            "msg": f"服务器内部错误: {str(e)}",
            "data": None
        }), 500

# 错误处理器
@segment_bp.errorhandler(400)
def bad_request(e):
    """处理请求错误"""
    return jsonify({
        "code": 400,
        "msg": "请求格式错误",
        "data": None
    }), 400

@segment_bp.errorhandler(404)
def not_found(e):
    """处理资源不存在错误"""
    return jsonify({
        "code": 404,
        "msg": "请求的资源不存在",
        "data": None
    }), 404

@segment_bp.errorhandler(500)
def internal_error(e):
    """处理服务器内部错误"""
    return jsonify({
        "code": 500,
        "msg": "服务器内部错误，请稍后重试",
        "data": None
    }), 500