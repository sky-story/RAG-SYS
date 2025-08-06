# 化工行业大模型知识库 - 后端

基于 Flask + MongoDB 的文档管理和 RAG 问答系统后端服务。

## 🚀 快速开始

### 环境要求

- Python 3.8+
- MongoDB 4.4+
- 推荐使用虚拟环境

### 安装依赖

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 配置环境

1. 确保 MongoDB 服务正在运行
2. 根据需要修改 `config.py` 中的配置项：
   - `MONGO_URI`: MongoDB 连接字符串
   - `UPLOAD_FOLDER`: 文件上传目录
   - `MAX_CONTENT_LENGTH`: 最大文件大小限制

### 启动服务

```bash
python app.py
```

服务将在 `http://localhost:5000` 启动。

## 📁 项目结构

```
backend/
├── app.py                 # Flask 应用入口
├── config.py             # 配置文件
├── requirements.txt      # Python 依赖
├── models/              # 数据模型
│   ├── __init__.py
│   └── file_model.py    # 文件模型
├── controllers/         # 业务逻辑控制器
│   ├── __init__.py
│   └── file_controller.py # 文件控制器
├── routes/              # API 路由
│   ├── upload_routes.py # 文件上传路由
│   ├── parse_routes.py  # 文档解析路由（待实现）
│   ├── segment_routes.py # 文档分段路由（待实现）
│   └── qa_routes.py     # 问答路由（待实现）
└── services/            # 服务层（待实现）
```

## 🔗 API 接口

### 文件上传模块

#### 1. 上传文件
- **POST** `/api/upload`
- **描述**: 上传单个或多个文件
- **支持格式**: PDF, DOCX, DOC, TXT
- **文件大小限制**: 100MB

**请求示例**:
```bash
curl -X POST -F "file=@document.pdf" http://localhost:5000/api/upload
```

**响应示例**:
```json
{
  "success": true,
  "message": "Successfully uploaded 1 files",
  "data": {
    "uploaded": [
      {
        "id": "64f1234567890abcdef12345",
        "filename": "document.pdf",
        "saved_as": "20231201_143022_uuid.pdf",
        "size": 1048576,
        "type": "pdf"
      }
    ],
    "failed": [],
    "total": 1
  }
}
```

#### 2. 获取文件列表
- **GET** `/api/files`
- **描述**: 获取所有上传文件的元数据
- **参数**: 
  - `page`: 页码（默认 1）
  - `per_page`: 每页数量（默认 50，最大 100）

**响应示例**:
```json
{
  "success": true,
  "data": [
    {
      "id": "64f1234567890abcdef12345",
      "name": "20231201_143022_uuid.pdf",
      "original_name": "document.pdf",
      "type": "pdf",
      "size": 1048576,
      "upload_time": "2023-12-01T14:30:22.123Z",
      "status": "uploaded"
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 50,
    "total": 1,
    "pages": 1
  }
}
```

#### 3. 删除文件
- **DELETE** `/api/files/{file_id}`
- **描述**: 删除指定文件（本地文件和数据库记录）

**响应示例**:
```json
{
  "success": true,
  "message": "File deleted successfully"
}
```

#### 4. 下载文件
- **GET** `/api/files/download/{file_id}`
- **描述**: 下载指定文件
- **响应**: 直接返回文件内容

#### 5. 文件统计
- **GET** `/api/files/stats`
- **描述**: 获取文件统计信息

**响应示例**:
```json
{
  "success": true,
  "data": {
    "total_files": 5,
    "by_type": {
      "pdf": 3,
      "docx": 1,
      "txt": 1
    },
    "upload_folder": "/path/to/data"
  }
}
```

## 🗄️ 数据库设计

### files 集合

```javascript
{
  "_id": ObjectId,
  "name": "20231201_143022_uuid.pdf",           // 存储的文件名
  "original_name": "document.pdf",              // 原始文件名
  "path": "/path/to/data/20231201_143022_uuid.pdf", // 文件路径
  "type": "pdf",                               // 文件类型
  "size": 1048576,                             // 文件大小（字节）
  "upload_time": ISODate("2023-12-01T14:30:22.123Z"), // 上传时间
  "status": "uploaded",                        // 文件状态
  "mime_type": "application/pdf",              // MIME 类型
  "created_at": ISODate("2023-12-01T14:30:22.123Z"),  // 创建时间
  "updated_at": ISODate("2023-12-01T14:30:22.123Z")   // 更新时间
}
```

## 🛠️ 开发说明

### 错误处理

所有 API 接口返回统一的错误格式：

```json
{
  "success": false,
  "error": "错误描述信息"
}
```

### 文件存储策略

- 文件使用 UUID + 时间戳命名，避免重名冲突
- 原始文件名保存在数据库中，用于下载时显示
- 文件存储在 `data/` 目录下

### 安全考虑

- 文件类型白名单验证
- 文件大小限制
- 文件名安全处理
- 路径遍历攻击防护

## 🔄 下一步开发

1. **文档解析模块** (`parse_routes.py`)
   - PDF/DOCX 文本提取
   - 文档预处理和清洗

2. **文档分段模块** (`segment_routes.py`)
   - 智能分段算法
   - 段落标签管理

3. **问答模块** (`qa_routes.py`)
   - 向量化和嵌入
   - RAG 检索和生成

4. **用户管理模块**
   - 用户认证和授权
   - 访问权限控制

## 📞 问题反馈

如遇到问题，请检查：
1. MongoDB 服务是否正常运行
2. 上传目录是否有写入权限
3. 依赖包是否正确安装
4. 配置文件是否正确设置