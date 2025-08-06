"""
app.py - Flask 主服务入口
负责创建 Flask 应用并注册各模块蓝图。
配置 CORS、文件上传限制等中间件
"""

from flask import Flask, jsonify
from flask_cors import CORS
from config import Config
import os

def create_app(config_name='development'):
    """
    应用工厂函数
    :param config_name: 配置名称
    :return: Flask应用实例
    """
    app = Flask(__name__)
    
    # 加载配置
    from config import config
    app.config.from_object(config[config_name])
    
    # 配置CORS
    CORS(app, origins=Config.CORS_ORIGINS, supports_credentials=True)
    
    # 设置文件上传限制
    app.config['MAX_CONTENT_LENGTH'] = Config.MAX_CONTENT_LENGTH
    
    # 注册蓝图
    from routes.upload_routes import upload_bp
    from routes.parse_routes import parse_bp
    
    app.register_blueprint(upload_bp)
    app.register_blueprint(parse_bp)
    
    # 根路由 - API信息
    @app.route('/')
    def index():
        return jsonify({
            'service': 'Chemical Industry LLM Knowledge Base Backend',
            'version': '1.0.0',
            'status': 'running',
            'endpoints': {
                'upload': '/api/upload',
                'files': '/api/files',
                'delete': '/api/files/<id>',
                'download': '/api/files/download/<id>',
                'stats': '/api/files/stats',
                'parse_local': '/api/parse/local',
                'parse_database': '/api/parse/database/<file_id>',
                'parse_history': '/api/parse/history',
                'parse_content': '/api/parse/<parse_id>',
                'parse_download': '/api/parse/download/<parse_id>',
                'parse_search': '/api/parse/search'
            }
        })
    
    # 健康检查接口
    @app.route('/health')
    def health_check():
        return jsonify({
            'status': 'healthy',
            'service': 'chem-knowledge-base-backend'
        })
    
    # 全局错误处理器
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 'Endpoint not found'
        }), 404
    
    @app.errorhandler(413)
    def too_large(error):
        return jsonify({
            'success': False,
            'error': f'Request entity too large. Maximum file size is {Config.MAX_CONTENT_LENGTH / 1024 / 1024:.1f}MB'
        }), 413
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500
    
    return app

# 创建应用实例
app = create_app()

if __name__ == "__main__":
    # 确保上传目录存在
    if not os.path.exists(Config.UPLOAD_FOLDER):
        os.makedirs(Config.UPLOAD_FOLDER)
        print(f"Created upload directory: {Config.UPLOAD_FOLDER}")
    
    print(f"Starting Chemical Industry LLM Knowledge Base Backend...")
    print(f"Upload folder: {Config.UPLOAD_FOLDER}")
    print(f"Max file size: {Config.MAX_CONTENT_LENGTH / 1024 / 1024:.1f}MB")
    print(f"Allowed extensions: {', '.join(Config.ALLOWED_EXTENSIONS)}")
    print(f"MongoDB URI: {Config.MONGO_URI}")
    
    # 启动开发服务器
    app.run(
        debug=Config.DEBUG,
        host="0.0.0.0",
        port=5001
    )
