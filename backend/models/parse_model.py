# parse_model.py - 文档解析数据模型
# 负责解析记录的 MongoDB 数据库操作
# 包括保存解析结果、查询解析历史、删除解析记录等功能

from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime
import logging
from typing import Dict, List, Optional, Any

# 配置日志
logger = logging.getLogger(__name__)

class ParseModel:
    """解析记录数据模型类"""
    
    def __init__(self, mongo_uri: str, db_name: str):
        """
        初始化数据库连接
        
        Args:
            mongo_uri (str): MongoDB 连接字符串
            db_name (str): 数据库名称
        """
        try:
            self.client = MongoClient(mongo_uri)
            self.db = self.client[db_name]
            self.collection = self.db.parsed_texts  # 解析文本集合
            logger.info(f"成功连接到 MongoDB: {db_name}")
        except Exception as e:
            logger.error(f"MongoDB 连接失败: {str(e)}")
            raise
    
    def save_parsed_text(self, file_id: str, original_name: str, text_content: str, 
                        file_type: str, summary: str = "") -> Optional[str]:
        """
        保存解析后的文本内容
        
        Args:
            file_id (str): 原文件 ID
            original_name (str): 原文件名
            text_content (str): 解析的文本内容
            file_type (str): 文件类型
            summary (str): 文本摘要
        
        Returns:
            Optional[str]: 解析记录 ID，失败返回 None
        """
        try:
            document = {
                "file_id": file_id,
                "original_name": original_name,
                "text_content": text_content,
                "file_type": file_type,
                "summary": summary,
                "text_length": len(text_content),
                "parsed_at": datetime.utcnow(),
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "status": "completed"
            }
            
            result = self.collection.insert_one(document)
            logger.info(f"成功保存解析记录: {result.inserted_id}")
            return str(result.inserted_id)
            
        except Exception as e:
            logger.error(f"保存解析记录失败: {str(e)}")
            return None
    
    def get_parse_by_id(self, parse_id: str) -> Optional[Dict[str, Any]]:
        """
        根据 ID 获取解析记录
        
        Args:
            parse_id (str): 解析记录 ID
        
        Returns:
            Optional[Dict]: 解析记录，不存在返回 None
        """
        try:
            result = self.collection.find_one({"_id": ObjectId(parse_id)})
            if result:
                result["id"] = str(result["_id"])
                del result["_id"]
            return result
        except Exception as e:
            logger.error(f"查询解析记录失败: {str(e)}")
            return None
    
    def get_parse_by_file_id(self, file_id: str) -> Optional[Dict[str, Any]]:
        """
        根据文件 ID 获取最新的解析记录
        
        Args:
            file_id (str): 原文件 ID
        
        Returns:
            Optional[Dict]: 解析记录，不存在返回 None
        """
        try:
            result = self.collection.find_one(
                {"file_id": file_id}, 
                sort=[("parsed_at", -1)]  # 按解析时间降序
            )
            if result:
                result["id"] = str(result["_id"])
                del result["_id"]
            return result
        except Exception as e:
            logger.error(f"查询文件解析记录失败: {str(e)}")
            return None
    
    def get_all_parse_history(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """
        获取所有解析历史记录
        
        Args:
            limit (int): 限制返回数量
            offset (int): 偏移量
        
        Returns:
            List[Dict]: 解析历史记录列表
        """
        try:
            cursor = self.collection.find(
                {}, 
                {
                    "text_content": 0  # 不返回完整文本内容（太大）
                }
            ).sort("parsed_at", -1).skip(offset).limit(limit)
            
            results = []
            for doc in cursor:
                doc["id"] = str(doc["_id"])
                del doc["_id"]
                results.append(doc)
            
            logger.info(f"查询到 {len(results)} 条解析历史记录")
            return results
            
        except Exception as e:
            logger.error(f"查询解析历史失败: {str(e)}")
            return []
    
    def delete_parse_record(self, parse_id: str) -> bool:
        """
        删除解析记录
        
        Args:
            parse_id (str): 解析记录 ID
        
        Returns:
            bool: 是否删除成功
        """
        try:
            result = self.collection.delete_one({"_id": ObjectId(parse_id)})
            success = result.deleted_count > 0
            
            if success:
                logger.info(f"成功删除解析记录: {parse_id}")
            else:
                logger.warning(f"解析记录不存在: {parse_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"删除解析记录失败: {str(e)}")
            return False
    
    def get_parse_stats(self) -> Dict[str, Any]:
        """
        获取解析统计信息
        
        Returns:
            Dict: 统计信息
        """
        try:
            total_count = self.collection.count_documents({})
            
            # 按文件类型统计
            type_stats = list(self.collection.aggregate([
                {"$group": {
                    "_id": "$file_type",
                    "count": {"$sum": 1},
                    "total_length": {"$sum": "$text_length"}
                }},
                {"$sort": {"count": -1}}
            ]))
            
            # 最近解析记录
            recent_parse = self.collection.find_one(
                {}, 
                sort=[("parsed_at", -1)]
            )
            
            stats = {
                "total_parsed": total_count,
                "by_file_type": type_stats,
                "last_parsed_at": recent_parse["parsed_at"] if recent_parse else None
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"获取解析统计失败: {str(e)}")
            return {
                "total_parsed": 0,
                "by_file_type": [],
                "last_parsed_at": None
            }
    
    def search_parsed_texts(self, keyword: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        搜索解析文本内容
        
        Args:
            keyword (str): 搜索关键词
            limit (int): 限制返回数量
        
        Returns:
            List[Dict]: 匹配的解析记录
        """
        try:
            # 使用文本搜索
            cursor = self.collection.find(
                {
                    "$or": [
                        {"original_name": {"$regex": keyword, "$options": "i"}},
                        {"text_content": {"$regex": keyword, "$options": "i"}},
                        {"summary": {"$regex": keyword, "$options": "i"}}
                    ]
                },
                {
                    "text_content": 0  # 不返回完整文本
                }
            ).sort("parsed_at", -1).limit(limit)
            
            results = []
            for doc in cursor:
                doc["id"] = str(doc["_id"])
                del doc["_id"]
                results.append(doc)
            
            return results
            
        except Exception as e:
            logger.error(f"搜索解析文本失败: {str(e)}")
            return []
    
    def update_parse_status(self, parse_id: str, status: str) -> bool:
        """
        更新解析记录状态
        
        Args:
            parse_id (str): 解析记录 ID
            status (str): 新状态
        
        Returns:
            bool: 是否更新成功
        """
        try:
            result = self.collection.update_one(
                {"_id": ObjectId(parse_id)},
                {
                    "$set": {
                        "status": status,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            success = result.modified_count > 0
            if success:
                logger.info(f"成功更新解析记录状态: {parse_id} -> {status}")
            
            return success
            
        except Exception as e:
            logger.error(f"更新解析记录状态失败: {str(e)}")
            return False