"""
file_controller.py - 文件控制器
处理文件上传、下载、删除等业务逻辑
"""

import os
import uuid
import mimetypes
from datetime import datetime
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
from config import Config

class FileController:
    """文件控制器类，处理文件相关的业务逻辑"""
    
    def __init__(self, file_model):
        """
        初始化文件控制器
        :param file_model: 文件模型实例
        """
        self.file_model = file_model
        self.upload_folder = Config.UPLOAD_FOLDER
        self.allowed_extensions = Config.ALLOWED_EXTENSIONS
        self.max_file_size = Config.MAX_CONTENT_LENGTH
    
    def allowed_file(self, filename):
        """
        检查文件类型是否允许
        :param filename: 文件名
        :return: 是否允许
        """
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in self.allowed_extensions
    
    def generate_unique_filename(self, original_filename):
        """
        生成唯一的文件名
        :param original_filename: 原始文件名
        :return: 唯一文件名
        """
        # 获取文件扩展名
        file_ext = os.path.splitext(original_filename)[1].lower()
        
        # 生成UUID作为文件名
        unique_id = str(uuid.uuid4())
        
        # 添加时间戳确保唯一性
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        return f"{timestamp}_{unique_id}{file_ext}"
    
    def save_uploaded_file(self, file_storage, original_filename):
        """
        保存上传的文件到本地
        :param file_storage: 文件存储对象
        :param original_filename: 原始文件名
        :return: 保存后的文件信息字典或None
        """
        try:
            # 生成安全的文件名
            secure_name = secure_filename(original_filename)
            unique_filename = self.generate_unique_filename(secure_name)
            
            # 构建文件保存路径
            file_path = os.path.join(self.upload_folder, unique_filename)
            
            # 保存文件
            file_storage.save(file_path)
            
            # 获取文件信息
            file_size = os.path.getsize(file_path)
            # 从原始文件名中提取文件类型，确保正确性
            file_type = original_filename.rsplit('.', 1)[1].lower() if '.' in original_filename else ''
            mime_type, _ = mimetypes.guess_type(file_path)
            
            return {
                'name': unique_filename,
                'original_name': secure_name,
                'path': file_path,
                'type': file_type,
                'size': file_size,
                'mime_type': mime_type or ''
            }
            
        except Exception as e:
            print(f"Error saving file: {e}")
            # 如果保存失败，尝试删除已创建的文件
            if 'file_path' in locals() and os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except:
                    pass
            return None
    
    def upload_files(self, files):
        """
        处理多文件上传
        :param files: 文件列表
        :return: 上传结果字典
        """
        results = {
            'success': [],
            'failed': [],
            'total': len(files)
        }
        
        for file in files:
            if not isinstance(file, FileStorage) or file.filename == '':
                results['failed'].append({
                    'filename': getattr(file, 'filename', 'unknown'),
                    'error': 'Invalid file'
                })
                continue
            
            # 检查文件类型
            if not self.allowed_file(file.filename):
                results['failed'].append({
                    'filename': file.filename,
                    'error': f'File type not allowed. Supported types: {", ".join(self.allowed_extensions)}'
                })
                continue
            
            # 检查文件大小
            file.seek(0, os.SEEK_END)
            file_size = file.tell()
            file.seek(0)
            
            if file_size > self.max_file_size:
                results['failed'].append({
                    'filename': file.filename,
                    'error': f'File size exceeds limit ({self.max_file_size / 1024 / 1024:.1f}MB)'
                })
                continue
            
            # 保存文件
            file_info = self.save_uploaded_file(file, file.filename)
            if not file_info:
                results['failed'].append({
                    'filename': file.filename,
                    'error': 'Failed to save file to disk'
                })
                continue
            
            # 保存到数据库
            file_id = self.file_model.create_file_record(file_info)
            if not file_id:
                # 如果数据库保存失败，删除本地文件
                try:
                    os.remove(file_info['path'])
                except:
                    pass
                results['failed'].append({
                    'filename': file.filename,
                    'error': 'Failed to save file metadata to database'
                })
                continue
            
            # 添加文件ID到结果
            file_info['id'] = str(file_id)
            file_info['createdAt'] = datetime.utcnow().isoformat()
            
            results['success'].append({
                'id': str(file_id),
                'filename': file.filename,
                'saved_as': file_info['name'],
                'size': file_info['size'],
                'type': file_info['type']
            })
        
        return results
    
    def get_all_files(self, page=1, per_page=50):
        """
        获取所有文件列表
        :param page: 页码
        :param per_page: 每页数量
        :return: 文件列表和分页信息
        """
        skip = (page - 1) * per_page
        files = self.file_model.get_all_files(skip=skip, limit=per_page)
        total = self.file_model.get_files_count()
        
        return {
            'files': files,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'pages': (total + per_page - 1) // per_page
            }
        }
    
    def delete_file(self, file_id):
        """
        删除文件（数据库记录和本地文件）
        :param file_id: 文件ID
        :return: 删除结果字典
        """
        # 获取文件信息
        file_info = self.file_model.get_file_by_id(file_id)
        if not file_info:
            return {
                'success': False,
                'error': 'File not found'
            }
        
        # 删除本地文件
        file_path = file_info['path']
        file_deleted = False
        
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                file_deleted = True
            except Exception as e:
                print(f"Error deleting local file: {e}")
                # 继续删除数据库记录，即使本地文件删除失败
        else:
            file_deleted = True  # 文件不存在也算删除成功
        
        # 删除数据库记录
        db_deleted = self.file_model.delete_file_record(file_id)
        
        if db_deleted:
            return {
                'success': True,
                'message': 'File deleted successfully',
                'file_deleted': file_deleted
            }
        else:
            return {
                'success': False,
                'error': 'Failed to delete file record from database'
            }
    
    def get_file_for_download(self, file_id):
        """
        获取文件信息用于下载
        :param file_id: 文件ID
        :return: 文件信息字典或None
        """
        file_info = self.file_model.get_file_by_id(file_id)
        if not file_info:
            return None
        
        file_path = file_info['path']
        if not os.path.exists(file_path):
            return None
        
        return {
            'path': file_path,
            'filename': file_info['original_name'],
            'mime_type': file_info.get('mime_type', 'application/octet-stream')
        }
    
    def get_file_stats(self):
        """
        获取文件统计信息
        :return: 统计信息字典
        """
        total_files = self.file_model.get_files_count()
        
        # 按类型统计
        type_stats = {}
        for ext in self.allowed_extensions:
            files = self.file_model.get_files_by_type(ext)
            type_stats[ext] = len(files)
        
        return {
            'total_files': total_files,
            'by_type': type_stats,
            'upload_folder': self.upload_folder
        }