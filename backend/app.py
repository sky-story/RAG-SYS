"""
app.py - Flask 主服务入口
负责创建 Flask 应用并注册各模块蓝图。
"""

from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# TODO: 在此处注册各路由蓝图
# from routes.upload_routes import upload_bp
# app.register_blueprint(upload_bp)


if __name__ == "__main__":
    # 默认监听 0.0.0.0:5000，方便 Docker 或远程调用
    app.run(debug=True, host="0.0.0.0", port=5000)
