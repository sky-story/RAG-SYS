# segment_model.py - 文档分段数据模型
# 负责文档段落的 MongoDB 数据库操作
# 包括保存段落、查询段落、更新标签、搜索等功能

from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime
import logging
from typing import Dict, List, Optional, Any

# 配置日志
logger = logging.getLogger(__name__)

class SegmentModel:
    """段落数据模型类"""
    
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
            self.collection = self.db.segments  # 段落集合
            
            # 创建索引以提高查询性能
            self._create_indexes()
            logger.info(f"成功连接到 MongoDB segments 集合: {db_name}")
        except Exception as e:
            logger.error(f"MongoDB 连接失败: {str(e)}")
            raise
    
    def _create_indexes(self):
        """创建数据库索引"""
        try:
            # 为常用查询字段创建索引
            self.collection.create_index("file_id")
            self.collection.create_index("segment_id")
            self.collection.create_index([("file_id", 1), ("order", 1)])
            self.collection.create_index([("text", "text")])  # 全文搜索索引
            self.collection.create_index("tags")
        except Exception as e:
            logger.warning(f"创建索引失败: {str(e)}")
    
    def save_segments(self, segments_data: List[Dict[str, Any]]) -> bool:
        """
        批量保存段落数据
        
        Args:
            segments_data (List[Dict]): 段落数据列表
        
        Returns:
            bool: 是否保存成功
        """
        try:
            if not segments_data:
                return True
            
            # 添加时间戳
            for segment in segments_data:
                segment["created_at"] = datetime.utcnow()
                segment["updated_at"] = datetime.utcnow()
            
            result = self.collection.insert_many(segments_data)
            logger.info(f"成功保存 {len(result.inserted_ids)} 个段落")
            return True
            
        except Exception as e:
            logger.error(f"保存段落失败: {str(e)}")
            return False
    
    def get_segments_by_file_id(self, file_id: str) -> List[Dict[str, Any]]:
        """
        根据文件 ID 获取所有段落
        
        Args:
            file_id (str): 文件 ID
        
        Returns:
            List[Dict]: 段落列表，按顺序排序
        """
        try:
            cursor = self.collection.find(
                {"file_id": file_id}
            ).sort("order", 1)
            
            segments = []
            for doc in cursor:
                doc["id"] = str(doc["_id"])
                del doc["_id"]
                segments.append(doc)
            
            logger.info(f"查询到文件 {file_id} 的 {len(segments)} 个段落")
            return segments
            
        except Exception as e:
            logger.error(f"查询段落失败: {str(e)}")
            return []
    
    def get_segment_by_id(self, segment_id: str) -> Optional[Dict[str, Any]]:
        """
        根据段落 ID 获取段落详情
        
        Args:
            segment_id (str): 段落 ID
        
        Returns:
            Optional[Dict]: 段落信息，不存在返回 None
        """
        try:
            result = self.collection.find_one({"segment_id": segment_id})
            if result:
                result["id"] = str(result["_id"])
                del result["_id"]
            return result
        except Exception as e:
            logger.error(f"查询段落失败: {str(e)}")
            return None
    
    def update_segment_tags(self, segment_id: str, tags: List[str]) -> bool:
        """
        更新段落的标签
        
        Args:
            segment_id (str): 段落 ID
            tags (List[str]): 标签列表
        
        Returns:
            bool: 是否更新成功
        """
        try:
            result = self.collection.update_one(
                {"segment_id": segment_id},
                {
                    "$set": {
                        "tags": tags,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            success = result.modified_count > 0
            if success:
                logger.info(f"成功更新段落 {segment_id} 的标签: {tags}")
            else:
                logger.warning(f"段落 {segment_id} 不存在或标签未改变")
            
            return success
            
        except Exception as e:
            logger.error(f"更新段落标签失败: {str(e)}")
            return False
    
    def batch_update_tags(self, tag_updates: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        批量更新段落标签
        
        Args:
            tag_updates (List[Dict]): 更新列表，格式：[{"segment_id": "...", "tags": [...]}]
        
        Returns:
            Dict[str, int]: 更新结果统计
        """
        try:
            updated_count = 0
            failed_count = 0
            
            for update in tag_updates:
                segment_id = update.get("segment_id")
                tags = update.get("tags", [])
                
                if self.update_segment_tags(segment_id, tags):
                    updated_count += 1
                else:
                    failed_count += 1
            
            logger.info(f"批量更新完成: 成功 {updated_count}, 失败 {failed_count}")
            return {
                "updated": updated_count,
                "failed": failed_count,
                "total": len(tag_updates)
            }
            
        except Exception as e:
            logger.error(f"批量更新标签失败: {str(e)}")
            return {"updated": 0, "failed": len(tag_updates), "total": len(tag_updates)}
    
    def search_segments_by_keyword(self, keyword: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        根据关键词搜索段落
        
        Args:
            keyword (str): 搜索关键词
            limit (int): 限制返回数量
        
        Returns:
            List[Dict]: 匹配的段落列表
        """
        try:
            # 使用正则表达式搜索
            cursor = self.collection.find(
                {
                    "$or": [
                        {"text": {"$regex": keyword, "$options": "i"}},
                        {"tags": {"$regex": keyword, "$options": "i"}}
                    ]
                }
            ).limit(limit).sort("updated_at", -1)
            
            segments = []
            for doc in cursor:
                doc["id"] = str(doc["_id"])
                del doc["_id"]
                segments.append(doc)
            
            logger.info(f"关键词 '{keyword}' 搜索到 {len(segments)} 个段落")
            return segments
            
        except Exception as e:
            logger.error(f"搜索段落失败: {str(e)}")
            return []
    
    def get_segments_by_tags(self, tags: List[str], limit: int = 50) -> List[Dict[str, Any]]:
        """
        根据标签查询段落
        
        Args:
            tags (List[str]): 标签列表
            limit (int): 限制返回数量
        
        Returns:
            List[Dict]: 匹配的段落列表
        """
        try:
            cursor = self.collection.find(
                {"tags": {"$in": tags}}
            ).limit(limit).sort("updated_at", -1)
            
            segments = []
            for doc in cursor:
                doc["id"] = str(doc["_id"])
                del doc["_id"]
                segments.append(doc)
            
            logger.info(f"标签 {tags} 查询到 {len(segments)} 个段落")
            return segments
            
        except Exception as e:
            logger.error(f"按标签查询段落失败: {str(e)}")
            return []
    
    def delete_segments_by_file_id(self, file_id: str) -> int:
        """
        删除指定文件的所有段落
        
        Args:
            file_id (str): 文件 ID
        
        Returns:
            int: 删除的段落数量
        """
        try:
            result = self.collection.delete_many({"file_id": file_id})
            deleted_count = result.deleted_count
            logger.info(f"删除文件 {file_id} 的 {deleted_count} 个段落")
            return deleted_count
            
        except Exception as e:
            logger.error(f"删除段落失败: {str(e)}")
            return 0
    
    def get_segment_stats(self) -> Dict[str, Any]:
        """
        获取段落统计信息
        
        Returns:
            Dict: 统计信息
        """
        try:
            total_segments = self.collection.count_documents({})
            
            # 统计各文件的段落数
            file_stats = list(self.collection.aggregate([
                {"$group": {
                    "_id": "$file_id",
                    "segment_count": {"$sum": 1},
                    "avg_length": {"$avg": {"$strLenCP": "$text"}}
                }},
                {"$sort": {"segment_count": -1}},
                {"$limit": 10}
            ]))
            
            # 统计标签使用情况
            tag_stats = list(self.collection.aggregate([
                {"$unwind": "$tags"},
                {"$group": {"_id": "$tags", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}},
                {"$limit": 20}
            ]))
            
            return {
                "total_segments": total_segments,
                "file_stats": file_stats,
                "tag_stats": tag_stats
            }
            
        except Exception as e:
            logger.error(f"获取段落统计失败: {str(e)}")
            return {
                "total_segments": 0,
                "file_stats": [],
                "tag_stats": []
            }