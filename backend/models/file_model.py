"""
file_model.py - 文件数据模型定义
定义文件元数据的数据结构和MongoDB操作方法
"""

from datetime import datetime
from bson import ObjectId
from pymongo.errors import PyMongoError
import os

class FileModel:
    """文件模型类，处理文件元数据的数据库操作"""
    
    def __init__(self, db):
        """
        初始化文件模型
        :param db: MongoDB数据库实例
        """
        self.collection = db.files
        
    def create_file_record(self, file_data):
        """
        创建文件记录
        :param file_data: 文件数据字典
        :return: 插入的文档ID或None
        """
        try:
            # 设置默认字段
            document = {
                'name': file_data['name'],
                'original_name': file_data.get('original_name', file_data['name']),
                'path': file_data['path'],
                'type': file_data['type'],
                'size': file_data.get('size', 0),
                'upload_time': datetime.utcnow(),
                'status': file_data.get('status', 'uploaded'),
                'mime_type': file_data.get('mime_type', ''),
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
            
            result = self.collection.insert_one(document)
            return result.inserted_id
            
        except PyMongoError as e:
            print(f"Error creating file record: {e}")
            return None
    
    def get_all_files(self, skip=0, limit=100):
        """
        获取所有文件记录
        :param skip: 跳过的记录数
        :param limit: 限制返回的记录数
        :return: 文件记录列表
        """
        try:
            cursor = self.collection.find().sort('upload_time', -1).skip(skip).limit(limit)
            files = []
            
            for doc in cursor:
                file_info = {
                    'id': str(doc['_id']),
                    'name': doc['name'],
                    'original_name': doc.get('original_name', doc['name']),
                    'type': doc['type'],
                    'size': doc.get('size', 0),
                    'upload_time': doc['upload_time'].isoformat(),
                    'status': doc.get('status', 'uploaded'),
                    'mime_type': doc.get('mime_type', ''),
                    'createdAt': doc['upload_time'].isoformat()  # 前端兼容字段
                }
                files.append(file_info)
                
            return files
            
        except PyMongoError as e:
            print(f"Error getting files: {e}")
            return []
    
    def get_file_by_id(self, file_id):
        """
        根据ID获取文件记录
        :param file_id: 文件ID
        :return: 文件记录字典或None
        """
        try:
            if not ObjectId.is_valid(file_id):
                return None
                
            doc = self.collection.find_one({'_id': ObjectId(file_id)})
            
            if doc:
                return {
                    'id': str(doc['_id']),
                    'name': doc['name'],
                    'original_name': doc.get('original_name', doc['name']),
                    'path': doc['path'],
                    'type': doc['type'],
                    'size': doc.get('size', 0),
                    'upload_time': doc['upload_time'].isoformat(),
                    'status': doc.get('status', 'uploaded'),
                    'mime_type': doc.get('mime_type', '')
                }
            return None
            
        except PyMongoError as e:
            print(f"Error getting file by ID: {e}")
            return None
    
    def delete_file_record(self, file_id):
        """
        删除文件记录
        :param file_id: 文件ID
        :return: 是否删除成功
        """
        try:
            if not ObjectId.is_valid(file_id):
                return False
                
            result = self.collection.delete_one({'_id': ObjectId(file_id)})
            return result.deleted_count > 0
            
        except PyMongoError as e:
            print(f"Error deleting file record: {e}")
            return False
    
    def update_file_status(self, file_id, status):
        """
        更新文件状态
        :param file_id: 文件ID
        :param status: 新状态
        :return: 是否更新成功
        """
        try:
            if not ObjectId.is_valid(file_id):
                return False
                
            result = self.collection.update_one(
                {'_id': ObjectId(file_id)},
                {
                    '$set': {
                        'status': status,
                        'updated_at': datetime.utcnow()
                    }
                }
            )
            return result.modified_count > 0
            
        except PyMongoError as e:
            print(f"Error updating file status: {e}")
            return False
    
    def get_files_count(self):
        """
        获取文件总数
        :return: 文件数量
        """
        try:
            return self.collection.count_documents({})
        except PyMongoError as e:
            print(f"Error getting files count: {e}")
            return 0
    
    def get_files_by_type(self, file_type):
        """
        根据文件类型获取文件列表
        :param file_type: 文件类型
        :return: 文件记录列表
        """
        try:
            cursor = self.collection.find({'type': file_type}).sort('upload_time', -1)
            files = []
            
            for doc in cursor:
                file_info = {
                    'id': str(doc['_id']),
                    'name': doc['name'],
                    'type': doc['type'],
                    'upload_time': doc['upload_time'].isoformat(),
                    'size': doc.get('size', 0)
                }
                files.append(file_info)
                
            return files
            
        except PyMongoError as e:
            print(f"Error getting files by type: {e}")
            return []