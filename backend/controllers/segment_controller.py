# segment_controller.py - 文档分段控制器
# 负责处理文档分段的业务逻辑
# 连接分段服务和数据模型，处理分段、标签管理、搜索等功能

import logging
from typing import Dict, List, Any, Tuple
from datetime import datetime

from models.segment_model import SegmentModel
from models.parse_model import ParseModel
from services.segment_service import segmentation_service
from config import Config

# 配置日志
logger = logging.getLogger(__name__)

class SegmentController:
    """文档分段控制器类"""
    
    def __init__(self):
        """初始化控制器"""
        self.segment_model = SegmentModel(Config.MONGO_URI, Config.MONGO_DB_NAME)
        self.parse_model = ParseModel(Config.MONGO_URI, Config.MONGO_DB_NAME)
    
    def _serialize_datetime(self, obj: Any) -> Any:
        """
        递归处理对象中的datetime和ObjectId序列化
        
        Args:
            obj: 需要处理的对象
        
        Returns:
            序列化后的对象
        """
        from bson.objectid import ObjectId
        
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, ObjectId):
            return str(obj)
        elif isinstance(obj, dict):
            return {key: self._serialize_datetime(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._serialize_datetime(item) for item in obj]
        else:
            return obj
    
    def create_segments_from_file(self, file_id: str) -> Tuple[bool, Dict[str, Any]]:
        """
        从解析文件创建分段
        
        Args:
            file_id (str): 文件 ID
        
        Returns:
            Tuple[bool, Dict]: (是否成功, 响应数据)
        """
        try:
            # 尝试获取解析记录，支持文件ID或解析记录ID
            parse_record = self.parse_model.get_parse_by_file_id(file_id)
            
            # 如果通过文件ID找不到，尝试通过解析记录ID查找
            if not parse_record:
                parse_record = self.parse_model.get_parse_by_id(file_id)
                if parse_record:
                    # 如果找到了，更新file_id为实际的文件ID
                    file_id = parse_record.get("file_id", file_id)
            
            if not parse_record:
                return False, {
                    "code": 404,
                    "msg": f"ID {file_id} 对应的解析记录不存在，请确保文档已成功解析",
                    "data": None
                }
            
            # 序列化解析记录中的datetime对象
            parse_record = self._serialize_datetime(parse_record)
            
            # 检查是否已经分段（临时允许重新分段以测试新算法）
            existing_segments = self.segment_model.get_segments_by_file_id(file_id)
            if existing_segments:
                logger.info(f"文件 {file_id} 已经分段，但允许重新分段以测试新算法")
                # 删除现有分段以重新分段
                self.segment_model.delete_segments_by_file_id(file_id)
                logger.info(f"已删除文件 {file_id} 的现有分段，准备重新分段")
            
            # 执行分段
            text_content = parse_record["text_content"]
            file_name = parse_record["original_name"]
            
            segments_data = segmentation_service.segment_document(
                file_id=file_id,
                text_content=text_content,
                file_name=file_name
            )
            
            if not segments_data:
                return False, {
                    "code": 400,
                    "msg": "文档分段失败，可能文档内容为空或格式不支持",
                    "data": None
                }
            
            # 保存分段到数据库
            if not self.segment_model.save_segments(segments_data):
                return False, {
                    "code": 500,
                    "msg": "保存分段数据到数据库失败",
                    "data": None
                }
            
            logger.info(f"成功为文件 {file_id} 创建 {len(segments_data)} 个分段")
            # 序列化日期时间对象
            serialized_segments = self._serialize_datetime(segments_data)
            return True, {
                "code": 200,
                "msg": "文档分段成功",
                "data": {
                    "file_id": file_id,
                    "file_name": file_name,
                    "segment_count": len(segments_data),
                    "segments": serialized_segments
                }
            }
            
        except Exception as e:
            logger.error(f"创建分段失败: {str(e)}")
            return False, {
                "code": 500,
                "msg": f"分段处理失败: {str(e)}",
                "data": None
            }
    
    def get_file_segments(self, file_id: str) -> Tuple[bool, Dict[str, Any]]:
        """
        获取文件的所有分段，支持文件ID或解析记录ID
        
        Args:
            file_id (str): 文件 ID 或解析记录 ID
        
        Returns:
            Tuple[bool, Dict]: (是否成功, 响应数据)
        """
        try:
            # 尝试直接通过文件ID查找分段
            segments = self.segment_model.get_segments_by_file_id(file_id)
            actual_file_id = file_id
            
            # 如果没有找到分段，尝试通过解析记录ID查找
            if not segments:
                parse_record = self.parse_model.get_parse_by_id(file_id)
                if parse_record:
                    actual_file_id = parse_record.get("file_id", file_id)
                    segments = self.segment_model.get_segments_by_file_id(actual_file_id)
            
            # 序列化日期时间对象
            serialized_segments = self._serialize_datetime(segments)
            
            return True, {
                "code": 200,
                "msg": "获取分段成功",
                "data": {
                    "file_id": actual_file_id,
                    "segment_count": len(segments),
                    "segments": serialized_segments
                }
            }
            
        except Exception as e:
            logger.error(f"获取文件分段失败: {str(e)}")
            return False, {
                "code": 500,
                "msg": f"获取分段失败: {str(e)}",
                "data": None
            }
    
    def update_segment_tags(self, segment_id: str, tags: List[str]) -> Tuple[bool, Dict[str, Any]]:
        """
        更新段落标签
        
        Args:
            segment_id (str): 段落 ID
            tags (List[str]): 标签列表
        
        Returns:
            Tuple[bool, Dict]: (是否成功, 响应数据)
        """
        try:
            # 验证输入
            if not segment_id:
                return False, {
                    "code": 400,
                    "msg": "段落 ID 不能为空",
                    "data": None
                }
            
            if not isinstance(tags, list):
                return False, {
                    "code": 400,
                    "msg": "标签必须为数组格式",
                    "data": None
                }
            
            # 清理和验证标签
            cleaned_tags = [tag.strip() for tag in tags if tag.strip()]
            
            # 更新标签
            success = self.segment_model.update_segment_tags(segment_id, cleaned_tags)
            
            if success:
                return True, {
                    "code": 200,
                    "msg": "标签更新成功",
                    "data": {
                        "segment_id": segment_id,
                        "tags": cleaned_tags
                    }
                }
            else:
                return False, {
                    "code": 404,
                    "msg": f"段落 {segment_id} 不存在",
                    "data": None
                }
                
        except Exception as e:
            logger.error(f"更新段落标签失败: {str(e)}")
            return False, {
                "code": 500,
                "msg": f"更新标签失败: {str(e)}",
                "data": None
            }
    
    def batch_update_tags(self, tag_updates: List[Dict[str, Any]]) -> Tuple[bool, Dict[str, Any]]:
        """
        批量更新段落标签
        
        Args:
            tag_updates (List[Dict]): 更新列表
        
        Returns:
            Tuple[bool, Dict]: (是否成功, 响应数据)
        """
        try:
            if not tag_updates:
                return False, {
                    "code": 400,
                    "msg": "更新列表不能为空",
                    "data": None
                }
            
            # 验证更新数据格式
            validated_updates = []
            for update in tag_updates:
                if not isinstance(update, dict):
                    continue
                
                segment_id = update.get("segment_id", "").strip()
                tags = update.get("tags", [])
                
                if segment_id and isinstance(tags, list):
                    validated_updates.append({
                        "segment_id": segment_id,
                        "tags": [tag.strip() for tag in tags if tag.strip()]
                    })
            
            if not validated_updates:
                return False, {
                    "code": 400,
                    "msg": "没有有效的更新数据",
                    "data": None
                }
            
            # 执行批量更新
            result = self.segment_model.batch_update_tags(validated_updates)
            
            return True, {
                "code": 200,
                "msg": f"批量更新完成",
                "data": {
                    "total": result["total"],
                    "updated": result["updated"],
                    "failed": result["failed"],
                    "success_rate": f"{result['updated']/result['total']*100:.1f}%" if result["total"] > 0 else "0%"
                }
            }
            
        except Exception as e:
            logger.error(f"批量更新标签失败: {str(e)}")
            return False, {
                "code": 500,
                "msg": f"批量更新失败: {str(e)}",
                "data": None
            }
    
    def recommend_tags_for_segment(self, segment_id: str) -> Tuple[bool, Dict[str, Any]]:
        """
        为段落推荐标签
        
        Args:
            segment_id (str): 段落 ID
        
        Returns:
            Tuple[bool, Dict]: (是否成功, 响应数据)
        """
        try:
            # 获取段落信息
            segment = self.segment_model.get_segment_by_id(segment_id)
            if not segment:
                return False, {
                    "code": 404,
                    "msg": f"段落 {segment_id} 不存在",
                    "data": None
                }
            
            # 推荐标签
            recommended_tags = segmentation_service.recommend_tags(segment["text"])
            
            # 提取关键词
            keywords = segmentation_service.extract_keywords(segment["text"])
            
            return True, {
                "code": 200,
                "msg": "标签推荐成功",
                "data": {
                    "segment_id": segment_id,
                    "current_tags": segment.get("tags", []),
                    "recommended_tags": recommended_tags,
                    "keywords": keywords,
                    "text_preview": segment["text"][:100] + "..." if len(segment["text"]) > 100 else segment["text"]
                }
            }
            
        except Exception as e:
            logger.error(f"标签推荐失败: {str(e)}")
            return False, {
                "code": 500,
                "msg": f"推荐失败: {str(e)}",
                "data": None
            }
    
    def search_segments(self, keyword: str, limit: int = 50) -> Tuple[bool, Dict[str, Any]]:
        """
        搜索段落
        
        Args:
            keyword (str): 搜索关键词
            limit (int): 限制返回数量
        
        Returns:
            Tuple[bool, Dict]: (是否成功, 响应数据)
        """
        try:
            if not keyword or not keyword.strip():
                return False, {
                    "code": 400,
                    "msg": "搜索关键词不能为空",
                    "data": None
                }
            
            keyword = keyword.strip()
            
            # 参数验证
            if limit <= 0 or limit > 200:
                limit = 50
            
            # 执行搜索
            segments = self.segment_model.search_segments_by_keyword(keyword, limit)
            # 序列化日期时间对象
            serialized_segments = self._serialize_datetime(segments)
            
            return True, {
                "code": 200,
                "msg": "搜索完成",
                "data": {
                    "keyword": keyword,
                    "total_found": len(segments),
                    "limit": limit,
                    "segments": serialized_segments
                }
            }
            
        except Exception as e:
            logger.error(f"搜索段落失败: {str(e)}")
            return False, {
                "code": 500,
                "msg": f"搜索失败: {str(e)}",
                "data": None
            }
    
    def get_segments_by_tags(self, tags: List[str], limit: int = 50) -> Tuple[bool, Dict[str, Any]]:
        """
        根据标签查询段落
        
        Args:
            tags (List[str]): 标签列表
            limit (int): 限制返回数量
        
        Returns:
            Tuple[bool, Dict]: (是否成功, 响应数据)
        """
        try:
            if not tags:
                return False, {
                    "code": 400,
                    "msg": "标签列表不能为空",
                    "data": None
                }
            
            # 清理标签
            cleaned_tags = [tag.strip() for tag in tags if tag.strip()]
            if not cleaned_tags:
                return False, {
                    "code": 400,
                    "msg": "没有有效的标签",
                    "data": None
                }
            
            # 参数验证
            if limit <= 0 or limit > 200:
                limit = 50
            
            # 查询段落
            segments = self.segment_model.get_segments_by_tags(cleaned_tags, limit)
            # 序列化日期时间对象
            serialized_segments = self._serialize_datetime(segments)
            
            return True, {
                "code": 200,
                "msg": "按标签查询完成",
                "data": {
                    "tags": cleaned_tags,
                    "total_found": len(segments),
                    "limit": limit,
                    "segments": serialized_segments
                }
            }
            
        except Exception as e:
            logger.error(f"按标签查询段落失败: {str(e)}")
            return False, {
                "code": 500,
                "msg": f"查询失败: {str(e)}",
                "data": None
            }
    
    def get_segment_stats(self) -> Tuple[bool, Dict[str, Any]]:
        """
        获取分段统计信息
        
        Returns:
            Tuple[bool, Dict]: (是否成功, 响应数据)
        """
        try:
            stats = self.segment_model.get_segment_stats()
            # 序列化日期时间对象
            serialized_stats = self._serialize_datetime(stats)
            
            return True, {
                "code": 200,
                "msg": "获取统计信息成功",
                "data": serialized_stats
            }
            
        except Exception as e:
            logger.error(f"获取统计信息失败: {str(e)}")
            return False, {
                "code": 500,
                "msg": f"获取统计失败: {str(e)}",
                "data": None
            }
    
    def delete_file_segments(self, file_id: str) -> Tuple[bool, Dict[str, Any]]:
        """
        删除文件的所有分段
        
        Args:
            file_id (str): 文件 ID
        
        Returns:
            Tuple[bool, Dict]: (是否成功, 响应数据)
        """
        try:
            deleted_count = self.segment_model.delete_segments_by_file_id(file_id)
            
            return True, {
                "code": 200,
                "msg": f"成功删除 {deleted_count} 个分段",
                "data": {
                    "file_id": file_id,
                    "deleted_count": deleted_count
                }
            }
            
        except Exception as e:
            logger.error(f"删除文件分段失败: {str(e)}")
            return False, {
                "code": 500,
                "msg": f"删除失败: {str(e)}",
                "data": None
            }

# 创建全局控制器实例
segment_controller = SegmentController()