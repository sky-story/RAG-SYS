"""
upload_routes.py - 文档上传相关的 API 接口路由
提供文件上传、文件列表、文件删除、文件下载等接口
"""

from flask import Blueprint, request, jsonify, send_file, current_app
from werkzeug.exceptions import RequestEntityTooLarge
from pymongo import MongoClient
from pymongo.errors import PyMongoError
import os

# 导入模型和控制器
from models.file_model import FileModel
from controllers.file_controller import FileController
from config import Config

# 创建蓝图
upload_bp = Blueprint("upload", __name__, url_prefix="/api")

# 全局变量，用于存储数据库连接和控制器实例
_db = None
_file_controller = None

def get_file_controller():
    """获取文件控制器实例（单例模式）"""
    global _db, _file_controller
    
    if _file_controller is None:
        try:
            # 创建MongoDB连接
            client = MongoClient(Config.MONGO_URI)
            _db = client[Config.MONGO_DB_NAME]
            
            # 创建文件模型和控制器实例
            file_model = FileModel(_db)
            _file_controller = FileController(file_model)
            
        except Exception as e:
            print(f"Error initializing file controller: {e}")
            return None
    
    return _file_controller

@upload_bp.route('/upload', methods=['POST'])
def upload_files():
    """
    文件上传接口
    支持单个或多个文件上传
    """
    try:
        # 获取文件控制器
        controller = get_file_controller()
        if not controller:
            return jsonify({
                'success': False,
                'error': 'Service unavailable'
            }), 500
        
        # 检查是否有文件上传
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file part in the request'
            }), 400
        
        files = request.files.getlist('file')
        
        if not files or all(file.filename == '' for file in files):
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400
        
        # 处理文件上传
        results = controller.upload_files(files)
        
        # 判断上传结果
        if results['success']:
            status_code = 200 if not results['failed'] else 207  # 207 Multi-Status
            return jsonify({
                'success': True,
                'message': f"Successfully uploaded {len(results['success'])} files",
                'data': {
                    'uploaded': results['success'],
                    'failed': results['failed'],
                    'total': results['total']
                }
            }), status_code
        else:
            return jsonify({
                'success': False,
                'error': 'All files failed to upload',
                'data': {
                    'failed': results['failed'],
                    'total': results['total']
                }
            }), 400
    
    except RequestEntityTooLarge:
        return jsonify({
            'success': False,
            'error': f'File too large. Maximum size is {Config.MAX_CONTENT_LENGTH / 1024 / 1024:.1f}MB'
        }), 413
    
    except Exception as e:
        print(f"Upload error: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error during file upload'
        }), 500

@upload_bp.route('/files', methods=['GET'])
def get_files():
    """
    获取所有上传文件的列表
    支持分页查询
    """
    try:
        # 获取文件控制器
        controller = get_file_controller()
        if not controller:
            return jsonify({
                'success': False,
                'error': 'Service unavailable'
            }), 500
        
        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 50, type=int), 100)  # 限制最大每页数量
        
        # 获取文件列表
        result = controller.get_all_files(page=page, per_page=per_page)
        
        return jsonify({
            'success': True,
            'data': result['files'],
            'pagination': result['pagination']
        }), 200
    
    except Exception as e:
        print(f"Get files error: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error while fetching files'
        }), 500

@upload_bp.route('/files/<file_id>', methods=['DELETE'])
def delete_file(file_id):
    """
    删除指定文件
    同时删除本地文件和数据库记录
    """
    try:
        # 获取文件控制器
        controller = get_file_controller()
        if not controller:
            return jsonify({
                'success': False,
                'error': 'Service unavailable'
            }), 500
        
        # 删除文件
        result = controller.delete_file(file_id)
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': result['message']
            }), 200
        else:
            status_code = 404 if 'not found' in result['error'].lower() else 500
            return jsonify({
                'success': False,
                'error': result['error']
            }), status_code
    
    except Exception as e:
        print(f"Delete file error: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error while deleting file'
        }), 500

@upload_bp.route('/files/download/<file_id>', methods=['GET'])
def download_file(file_id):
    """
    下载指定文件
    返回文件内容作为下载响应
    """
    try:
        # 获取文件控制器
        controller = get_file_controller()
        if not controller:
            return jsonify({
                'success': False,
                'error': 'Service unavailable'
            }), 500
        
        # 获取文件信息
        file_info = controller.get_file_for_download(file_id)
        
        if not file_info:
            return jsonify({
                'success': False,
                'error': 'File not found or file does not exist on disk'
            }), 404
        
        # 返回文件
        return send_file(
            file_info['path'],
            as_attachment=True,
            download_name=file_info['filename'],
            mimetype=file_info['mime_type']
        )
    
    except Exception as e:
        print(f"Download file error: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error while downloading file'
        }), 500

@upload_bp.route('/files/stats', methods=['GET'])
def get_file_stats():
    """
    获取文件统计信息
    返回文件总数、按类型分布等统计数据
    """
    try:
        # 获取文件控制器
        controller = get_file_controller()
        if not controller:
            return jsonify({
                'success': False,
                'error': 'Service unavailable'
            }), 500
        
        # 获取统计信息
        stats = controller.get_file_stats()
        
        return jsonify({
            'success': True,
            'data': stats
        }), 200
    
    except Exception as e:
        print(f"Get stats error: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error while fetching statistics'
        }), 500

# 错误处理器
@upload_bp.errorhandler(413)
def too_large(e):
    """处理文件过大错误"""
    return jsonify({
        'success': False,
        'error': f'File too large. Maximum size is {Config.MAX_CONTENT_LENGTH / 1024 / 1024:.1f}MB'
    }), 413

@upload_bp.errorhandler(500)
def internal_error(e):
    """处理内部服务器错误"""
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500
