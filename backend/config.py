"""
config.py - 后端配置文件，存放全局配置（如数据库 URI 等）
可通过环境变量覆盖默认值。
"""

import os

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/chem_knowledge_base")
DEBUG = bool(os.getenv("DEBUG", True))
