"""
config.py - 后端配置文件，存放全局配置（如数据库 URI、文件路径等）
包含数据库连接、文件存储路径、上传限制等配置常量
"""

import os
from datetime import timedelta
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 基础配置
class Config:
    # Flask配置
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-for-development")
    DEBUG = bool(os.getenv("DEBUG", True))
    
    # 数据库配置
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/chem_knowledge_base")
    MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "chem_knowledge_base")
    
    # 文件上传配置
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB
    ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt', 'doc'}
    
    # 确保上传目录存在
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    
    # CORS配置
    CORS_ORIGINS = ["http://localhost:5173", "http://localhost:3000"]
    
    # 接口配置
    API_PREFIX = "/api"
    
    # OpenAI 配置
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_CHAT_MODEL = os.getenv("OPENAI_CHAT_MODEL", "gpt-3.5-turbo")
    OPENAI_EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
    
    # RAG 配置
    RAG_TOP_K = int(os.getenv("RAG_TOP_K", "3"))
    RAG_MIN_SIMILARITY = float(os.getenv("RAG_MIN_SIMILARITY", "0.0"))
    RAG_MAX_CONTEXT_LENGTH = int(os.getenv("RAG_MAX_CONTEXT_LENGTH", "4000"))
    
    # 文件存储相关配置
    FILENAME_MAX_LENGTH = 255
    SUPPORTED_FILE_TYPES = {
        'pdf': 'application/pdf',
        'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'doc': 'application/msword',
        'txt': 'text/plain'
    }

# 生产环境配置（可根据需要扩展）
class ProductionConfig(Config):
    DEBUG = False
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/chem_knowledge_base_prod")

# 开发环境配置
class DevelopmentConfig(Config):
    DEBUG = True

# 测试环境配置
class TestingConfig(Config):
    TESTING = True
    MONGO_DB_NAME = "chem_knowledge_base_test"

# 配置字典
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}