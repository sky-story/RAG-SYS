# parse_controller.py - 文档解析控制器
# 负责处理文档解析的业务逻辑
# 连接解析服务和数据模型，处理文件解析、历史管理等功能

import os
import tempfile
import logging
from typing import Dict, List, Any, Tuple, Optional
from werkzeug.datastructures import FileStorage

from models.parse_model import ParseModel
from models.file_model import FileModel
from services.parsing_service import parsing_service
from config import Config

# 配置日志
logger = logging.getLogger(__name__)

class ParseController:
    """文档解析控制器类"""
    
    def __init__(self):
        """初始化控制器"""
        from pymongo import MongoClient
        
        # 创建数据库连接
        client = MongoClient(Config.MONGO_URI)
        db = client[Config.MONGO_DB_NAME]
        
        # 初始化模型
        self.parse_model = ParseModel(Config.MONGO_URI, Config.MONGO_DB_NAME)
        self.file_model = FileModel(db)
    
    def parse_uploaded_file(self, file: FileStorage) -> Tuple[bool, Dict[str, Any]]:
        """
        解析上传的文件
        
        Args:
            file (FileStorage): 上传的文件对象
        
        Returns:
            Tuple[bool, Dict]: (是否成功, 响应数据)
        """
        try:
            # 验证文件
            if not file or not file.filename:
                return False, {"error": "未提供文件"}
            
            # 获取文件扩展名
            file_ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
            if file_ext not in Config.ALLOWED_EXTENSIONS:
                return False, {"error": f"不支持的文件类型: {file_ext}"}
            
            # 创建临时文件保存上传的文件
            with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{file_ext}') as temp_file:
                file.save(temp_file.name)
                temp_file_path = temp_file.name
            
            try:
                # 解析文档
                success, result = parsing_service.parse_document(temp_file_path, file_ext)
                
                if not success:
                    return False, {"error": result}
                
                # 生成摘要
                summary = parsing_service.get_text_summary(result, 200)
                
                # 保存解析结果到数据库
                parse_id = self.parse_model.save_parsed_text(
                    file_id="temp_upload",  # 临时上传文件没有文件ID
                    original_name=file.filename,
                    text_content=result,
                    file_type=file_ext,
                    summary=summary
                )
                
                if not parse_id:
                    return False, {"error": "保存解析结果失败"}
                
                # 返回解析结果
                response_data = {
                    "parse_id": parse_id,
                    "original_name": file.filename,
                    "file_type": file_ext,
                    "text_content": result,
                    "summary": summary,
                    "text_length": len(result),
                    "message": "文件解析成功"
                }
                
                logger.info(f"成功解析上传文件: {file.filename}")
                return True, response_data
                
            finally:
                # 清理临时文件
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                    
        except Exception as e:
            logger.error(f"解析上传文件失败: {str(e)}")
            return False, {"error": f"解析失败: {str(e)}"}
    
    def parse_existing_file(self, file_id: str) -> Tuple[bool, Dict[str, Any]]:
        """
        解析数据库中已存在的文件
        
        Args:
            file_id (str): 文件 ID
        
        Returns:
            Tuple[bool, Dict]: (是否成功, 响应数据)
        """
        try:
            # 检查是否已经解析过
            existing_parse = self.parse_model.get_parse_by_file_id(file_id)
            if existing_parse:
                logger.info(f"文件 {file_id} 已有解析记录，返回现有结果")
                return True, {
                    "parse_id": existing_parse["id"],
                    "original_name": existing_parse["original_name"],
                    "file_type": existing_parse["file_type"],
                    "text_content": existing_parse["text_content"],
                    "summary": existing_parse["summary"],
                    "text_length": existing_parse["text_length"],
                    "parsed_at": existing_parse["parsed_at"].isoformat(),
                    "message": "返回已有解析结果"
                }
            
            # 获取文件信息
            file_info = self.file_model.get_file_by_id(file_id)
            if not file_info:
                return False, {"error": f"文件不存在: {file_id}"}
            
            # 检查文件是否存在于磁盘
            file_path = file_info["path"]
            if not os.path.exists(file_path):
                return False, {"error": f"物理文件不存在: {file_path}"}
            
            # 检查文件类型，如果数据库中为空则从文件名推断
            file_type = file_info["type"]
            if not file_type:
                # 从原始文件名或文件路径推断文件类型
                original_name = file_info.get("original_name", "")
                if '.' in original_name:
                    file_type = original_name.rsplit('.', 1)[1].lower()
                elif '.' in file_path:
                    file_type = file_path.rsplit('.', 1)[1].lower()
                else:
                    return False, {"error": "无法确定文件类型"}
            
            # 解析文档
            success, result = parsing_service.parse_document(file_path, file_type)
            
            if not success:
                return False, {"error": result}
            
            # 生成摘要
            summary = parsing_service.get_text_summary(result, 200)
            
            # 保存解析结果到数据库
            parse_id = self.parse_model.save_parsed_text(
                file_id=file_id,
                original_name=file_info["original_name"],
                text_content=result,
                file_type=file_info["type"],
                summary=summary
            )
            
            if not parse_id:
                return False, {"error": "保存解析结果失败"}
            
            # 返回解析结果
            response_data = {
                "parse_id": parse_id,
                "file_id": file_id,
                "original_name": file_info["original_name"],
                "file_type": file_info["type"],
                "text_content": result,
                "summary": summary,
                "text_length": len(result),
                "message": "文件解析成功"
            }
            
            logger.info(f"成功解析数据库文件: {file_info['original_name']}")
            return True, response_data
            
        except Exception as e:
            logger.error(f"解析数据库文件失败: {str(e)}")
            return False, {"error": f"解析失败: {str(e)}"}
    
    def get_parse_history(self, limit: int = 100, offset: int = 0) -> Tuple[bool, Dict[str, Any]]:
        """
        获取解析历史记录
        
        Args:
            limit (int): 限制返回数量
            offset (int): 偏移量
        
        Returns:
            Tuple[bool, Dict]: (是否成功, 响应数据)
        """
        try:
            history = self.parse_model.get_all_parse_history(limit, offset)
            stats = self.parse_model.get_parse_stats()
            
            # 格式化历史记录
            formatted_history = []
            for record in history:
                formatted_record = {
                    "id": record["id"],
                    "file_id": record.get("file_id"),
                    "original_name": record["original_name"],
                    "file_type": record["file_type"],
                    "summary": record["summary"],
                    "text_length": record["text_length"],
                    "parsed_at": record["parsed_at"].isoformat(),
                    "status": record["status"]
                }
                formatted_history.append(formatted_record)
            
            response_data = {
                "history": formatted_history,
                "total_count": stats["total_parsed"],
                "stats": stats,
                "pagination": {
                    "limit": limit,
                    "offset": offset,
                    "returned": len(formatted_history)
                }
            }
            
            return True, response_data
            
        except Exception as e:
            logger.error(f"获取解析历史失败: {str(e)}")
            return False, {"error": f"获取解析历史失败: {str(e)}"}
    
    def get_parsed_content(self, parse_id: str) -> Tuple[bool, Dict[str, Any]]:
        """
        获取解析内容详情
        
        Args:
            parse_id (str): 解析记录 ID
        
        Returns:
            Tuple[bool, Dict]: (是否成功, 响应数据)
        """
        try:
            parse_record = self.parse_model.get_parse_by_id(parse_id)
            if not parse_record:
                return False, {"error": f"解析记录不存在: {parse_id}"}
            
            response_data = {
                "parse_id": parse_record["id"],
                "file_id": parse_record.get("file_id"),
                "original_name": parse_record["original_name"],
                "file_type": parse_record["file_type"],
                "text_content": parse_record["text_content"],
                "summary": parse_record["summary"],
                "text_length": parse_record["text_length"],
                "parsed_at": parse_record["parsed_at"].isoformat(),
                "status": parse_record["status"]
            }
            
            return True, response_data
            
        except Exception as e:
            logger.error(f"获取解析内容失败: {str(e)}")
            return False, {"error": f"获取解析内容失败: {str(e)}"}
    
    def delete_parse_record(self, parse_id: str) -> Tuple[bool, Dict[str, Any]]:
        """
        删除解析记录
        
        Args:
            parse_id (str): 解析记录 ID
        
        Returns:
            Tuple[bool, Dict]: (是否成功, 响应数据)
        """
        try:
            success = self.parse_model.delete_parse_record(parse_id)
            
            if success:
                return True, {"message": "解析记录删除成功"}
            else:
                return False, {"error": "解析记录不存在或删除失败"}
                
        except Exception as e:
            logger.error(f"删除解析记录失败: {str(e)}")
            return False, {"error": f"删除失败: {str(e)}"}
    
    def download_parsed_text(self, parse_id: str) -> Tuple[bool, Any]:
        """
        下载解析文本
        
        Args:
            parse_id (str): 解析记录 ID
        
        Returns:
            Tuple[bool, Any]: (是否成功, 文件数据或错误信息)
        """
        try:
            parse_record = self.parse_model.get_parse_by_id(parse_id)
            if not parse_record:
                return False, {"error": f"解析记录不存在: {parse_id}"}
            
            # 生成文本文件内容
            content = f"文件名: {parse_record['original_name']}\n"
            content += f"解析时间: {parse_record['parsed_at'].isoformat()}\n"
            content += f"文件类型: {parse_record['file_type']}\n"
            content += f"文本长度: {parse_record['text_length']} 字符\n"
            content += "=" * 50 + "\n\n"
            content += parse_record['text_content']
            
            # 生成文件名
            safe_name = parse_record['original_name'].replace(' ', '_')
            if '.' in safe_name:
                safe_name = safe_name.rsplit('.', 1)[0]
            filename = f"{safe_name}_解析结果.txt"
            
            return True, {
                "content": content,
                "filename": filename,
                "mimetype": "text/plain; charset=utf-8"
            }
            
        except Exception as e:
            logger.error(f"下载解析文本失败: {str(e)}")
            return False, {"error": f"下载失败: {str(e)}"}
    
    def search_parsed_texts(self, keyword: str, limit: int = 50) -> Tuple[bool, Dict[str, Any]]:
        """
        搜索解析文本
        
        Args:
            keyword (str): 搜索关键词
            limit (int): 限制返回数量
        
        Returns:
            Tuple[bool, Dict]: (是否成功, 响应数据)
        """
        try:
            if not keyword.strip():
                return False, {"error": "搜索关键词不能为空"}
            
            results = self.parse_model.search_parsed_texts(keyword, limit)
            
            # 格式化搜索结果
            formatted_results = []
            for record in results:
                formatted_record = {
                    "id": record["id"],
                    "file_id": record.get("file_id"),
                    "original_name": record["original_name"],
                    "file_type": record["file_type"],
                    "summary": record["summary"],
                    "text_length": record["text_length"],
                    "parsed_at": record["parsed_at"].isoformat(),
                    "status": record["status"]
                }
                formatted_results.append(formatted_record)
            
            response_data = {
                "keyword": keyword,
                "results": formatted_results,
                "total_found": len(formatted_results),
                "limit": limit
            }
            
            return True, response_data
            
        except Exception as e:
            logger.error(f"搜索解析文本失败: {str(e)}")
            return False, {"error": f"搜索失败: {str(e)}"}

# 创建全局控制器实例
parse_controller = ParseController()