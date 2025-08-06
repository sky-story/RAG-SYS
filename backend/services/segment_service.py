# segment_service.py - 文档分段服务
# 负责文档分段处理和标签推荐功能
# 包括文本分段算法、智能标签推荐、关键词提取等

import uuid
import re
import logging
from typing import List, Dict, Any, Tuple
from datetime import datetime

# 配置日志
logger = logging.getLogger(__name__)

class SegmentationService:
    """文档分段服务类"""
    
    def __init__(self):
        """初始化分段服务"""
        self.min_segment_length = 50   # 最小段落长度（增加）
        self.max_segment_length = 500  # 最大段落长度（大幅减少）
        self.target_segment_length = 300  # 目标段落长度
        self.overlap_length = 50       # 重叠长度
        
        # 化工领域关键词映射（用于标签推荐）
        self.keyword_tag_mapping = {
            # 实验相关
            "实验": ["实验方法", "操作"],
            "测试": ["实验方法", "检测"],
            "试验": ["实验方法", "操作"],
            "检测": ["检测", "分析"],
            "分析": ["分析", "检测"],
            "测量": ["检测", "测量"],
            
            # 安全相关
            "安全": ["安全", "注意事项"],
            "注意": ["注意事项", "安全"],
            "警告": ["安全", "警告"],
            "危险": ["安全", "危险"],
            "防护": ["安全", "防护"],
            "事故": ["安全", "事故预防"],
            
            # 工艺相关
            "工艺": ["工艺", "流程"],
            "流程": ["流程", "工艺"],
            "步骤": ["流程", "操作"],
            "操作": ["操作", "流程"],
            "控制": ["控制", "工艺"],
            "参数": ["参数", "控制"],
            
            # 设备相关
            "设备": ["设备", "装置"],
            "装置": ["装置", "设备"],
            "反应器": ["反应器", "设备"],
            "塔": ["分离设备", "设备"],
            "换热器": ["换热设备", "设备"],
            
            # 物料相关
            "原料": ["原料", "物料"],
            "产品": ["产品", "物料"],
            "催化剂": ["催化剂", "化学品"],
            "溶剂": ["溶剂", "化学品"],
            "化学品": ["化学品", "物料"],
            
            # 理论相关
            "理论": ["理论", "原理"],
            "原理": ["原理", "理论"],
            "机理": ["机理", "原理"],
            "动力学": ["动力学", "理论"],
            "热力学": ["热力学", "理论"],
            
            # 质量相关
            "质量": ["质量", "控制"],
            "标准": ["标准", "规范"],
            "规范": ["规范", "标准"],
            "检验": ["检验", "质量"],
            "合格": ["质量", "标准"],
            
            # 环保相关
            "环保": ["环保", "环境"],
            "环境": ["环境", "环保"],
            "污染": ["环保", "污染控制"],
            "废水": ["废水处理", "环保"],
            "废气": ["废气处理", "环保"],
            "废料": ["废料处理", "环保"],
        }
    
    def segment_document(self, file_id: str, text_content: str, file_name: str = "") -> List[Dict[str, Any]]:
        """
        将文档文本分段
        
        Args:
            file_id (str): 文件 ID
            text_content (str): 文档文本内容
            file_name (str): 文件名（可选）
        
        Returns:
            List[Dict]: 分段结果列表
        """
        try:
            # 清理文本
            cleaned_text = self._clean_text(text_content)
            
            # 执行分段
            segments = self._split_text_into_segments(cleaned_text)
            
            # 生成段落数据
            segment_data = []
            for i, segment_text in enumerate(segments):
                if len(segment_text.strip()) < self.min_segment_length:
                    continue  # 跳过过短的段落
                
                segment_id = f"{file_id}_{i+1}_{str(uuid.uuid4())[:8]}"
                
                segment_data.append({
                    "segment_id": segment_id,
                    "file_id": file_id,
                    "order": i + 1,
                    "text": segment_text.strip(),
                    "file_name": file_name,
                    "tags": [],  # 初始标签为空
                    "character_count": len(segment_text.strip()),
                    "word_count": len(segment_text.strip().split()),
                })
            
            logger.info(f"文档 {file_id} 分段完成，共生成 {len(segment_data)} 个段落")
            return segment_data
            
        except Exception as e:
            logger.error(f"文档分段失败: {str(e)}")
            return []
    
    def _clean_text(self, text: str) -> str:
        """
        清理文本内容
        
        Args:
            text (str): 原始文本
        
        Returns:
            str: 清理后的文本
        """
        # 去除过多的空白字符
        text = re.sub(r'\s+', ' ', text)
        
        # 规范化换行符
        text = re.sub(r'\r\n', '\n', text)
        text = re.sub(r'\r', '\n', text)
        
        # 去除首尾空白
        text = text.strip()
        
        return text
    
    def _split_text_into_segments(self, text: str) -> List[str]:
        """
        智能分割文本成段落
        
        Args:
            text (str): 清理后的文本
        
        Returns:
            List[str]: 段落列表
        """
        segments = []
        
        # 第一步：预处理 - 按自然段落分割
        natural_paragraphs = self._split_by_natural_paragraphs(text)
        
        # 第二步：智能分段 - 每个自然段落进一步细分
        for paragraph in natural_paragraphs:
            if len(paragraph) <= self.max_segment_length:
                # 段落长度合适，直接使用
                if len(paragraph) >= self.min_segment_length:
                    segments.append(paragraph)
            else:
                # 段落过长，需要细分
                sub_segments = self._intelligent_split_paragraph(paragraph)
                segments.extend(sub_segments)
        
        # 第三步：应用滑动窗口策略提高召回率
        enhanced_segments = self._add_overlapping_segments(segments)
        
        logger.info(f"智能分段完成: 原始段落 {len(segments)} 个, 增强后 {len(enhanced_segments)} 个")
        return enhanced_segments
    
    def _split_by_natural_paragraphs(self, text: str) -> List[str]:
        """按自然段落分割文本"""
        paragraphs = []
        
        # 方法1：双换行符分割
        parts = text.split('\n\n')
        for part in parts:
            part = part.strip()
            if len(part) >= self.min_segment_length:
                paragraphs.append(part)
        
        # 如果分割效果不好，尝试其他方法
        if len(paragraphs) <= 2:
            # 方法2：单换行符 + 段落标识符
            parts = re.split(r'\n(?=\d+\.|\d+、|[一二三四五六七八九十]+[、．]|[（【]\d+[）】])', text)
            for part in parts:
                part = part.strip()
                if len(part) >= self.min_segment_length:
                    paragraphs.append(part)
        
        # 如果还是分割效果不好，使用固定长度分割
        if len(paragraphs) <= 2:
            paragraphs = self._split_by_fixed_length(text, self.max_segment_length)
        
        return [p for p in paragraphs if len(p.strip()) >= self.min_segment_length]
    
    def _intelligent_split_paragraph(self, paragraph: str) -> List[str]:
        """智能分割长段落"""
        segments = []
        sentences = re.split(r'([。！？；]\s*)', paragraph)
        
        current_segment = ""
        current_length = 0
        
        i = 0
        while i < len(sentences):
            sentence = sentences[i]
            
            # 如果是标点符号，合并到前一个句子
            if i < len(sentences) - 1 and re.match(r'[。！？；]\s*', sentences[i+1]):
                sentence += sentences[i+1]
                i += 1
            
            sentence_length = len(sentence)
            
            # 检查是否应该开始新段落
            if (current_length + sentence_length > self.target_segment_length and 
                current_segment and 
                current_length >= self.min_segment_length):
                
                segments.append(current_segment.strip())
                current_segment = sentence
                current_length = sentence_length
            else:
                current_segment += sentence
                current_length += sentence_length
            
            i += 1
        
        # 添加最后一个段落
        if current_segment.strip() and len(current_segment.strip()) >= self.min_segment_length:
            segments.append(current_segment.strip())
        
        return segments
    
    def _split_by_fixed_length(self, text: str, max_length: int) -> List[str]:
        """按固定长度分割文本"""
        segments = []
        start = 0
        
        while start < len(text):
            end = start + max_length
            
            # 如果不是最后一段，尝试在句子边界分割
            if end < len(text):
                # 向前寻找句子结束符
                for i in range(min(end, len(text) - 1), start + max_length // 2, -1):
                    if text[i] in '。！？；\n':
                        end = i + 1
                        break
            
            segment = text[start:end].strip()
            if len(segment) >= self.min_segment_length:
                segments.append(segment)
            
            start = end
        
        return segments
    
    def _add_overlapping_segments(self, segments: List[str]) -> List[str]:
        """添加重叠段落以提高召回率"""
        if len(segments) <= 1:
            return segments
        
        enhanced_segments = []
        
        for i, segment in enumerate(segments):
            # 添加原始段落
            enhanced_segments.append(segment)
            
            # 添加与下一段的重叠段落（每隔一个段落添加，避免过多重叠）
            if i < len(segments) - 1 and i % 2 == 0:
                next_segment = segments[i + 1]
                
                # 取当前段落的后部分和下一段落的前部分
                overlap_start = max(0, len(segment) - self.overlap_length)
                overlap_end = min(len(next_segment), self.overlap_length)
                
                overlap_segment = segment[overlap_start:] + " " + next_segment[:overlap_end]
                
                if len(overlap_segment.strip()) >= self.min_segment_length:
                    enhanced_segments.append(overlap_segment.strip())
        
        return enhanced_segments
    
    def _split_long_paragraph(self, paragraph: str) -> List[str]:
        """
        分割过长的段落
        
        Args:
            paragraph (str): 长段落
        
        Returns:
            List[str]: 分割后的段落列表
        """
        segments = []
        
        # 按句子分割
        sentences = re.split(r'[。！？；]\s*', paragraph)
        
        current_segment = ""
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            # 如果添加这个句子会超过长度限制
            if len(current_segment) + len(sentence) > self.max_segment_length:
                if current_segment:
                    segments.append(current_segment.strip())
                current_segment = sentence
            else:
                if current_segment:
                    current_segment += "。" + sentence
                else:
                    current_segment = sentence
        
        # 添加最后一个段落
        if current_segment:
            segments.append(current_segment.strip())
        
        return segments
    
    def _split_by_sentences(self, text: str) -> List[str]:
        """
        按句子分段（备用方法）
        
        Args:
            text (str): 文本
        
        Returns:
            List[str]: 段落列表
        """
        # 按句号、感叹号、问号分割
        sentences = re.split(r'[。！？]\s*', text)
        
        segments = []
        current_segment = ""
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            if len(current_segment) + len(sentence) > self.max_segment_length:
                if current_segment:
                    segments.append(current_segment.strip())
                current_segment = sentence
            else:
                if current_segment:
                    current_segment += "。" + sentence
                else:
                    current_segment = sentence
        
        if current_segment:
            segments.append(current_segment.strip())
        
        return segments if segments else [text]
    
    def recommend_tags(self, segment_text: str, max_tags: int = 5) -> List[str]:
        """
        为段落推荐标签
        
        Args:
            segment_text (str): 段落文本
            max_tags (int): 最大推荐标签数
        
        Returns:
            List[str]: 推荐的标签列表
        """
        try:
            recommended_tags = set()
            text_lower = segment_text.lower()
            
            # 基于关键词映射推荐标签
            for keyword, tags in self.keyword_tag_mapping.items():
                if keyword in text_lower:
                    recommended_tags.update(tags)
            
            # 基于内容特征推荐标签
            feature_tags = self._extract_feature_tags(segment_text)
            recommended_tags.update(feature_tags)
            
            # 限制推荐数量
            result_tags = list(recommended_tags)[:max_tags]
            
            logger.debug(f"为段落推荐标签: {result_tags}")
            return result_tags
            
        except Exception as e:
            logger.error(f"标签推荐失败: {str(e)}")
            return []
    
    def _extract_feature_tags(self, text: str) -> List[str]:
        """
        基于文本特征提取标签
        
        Args:
            text (str): 段落文本
        
        Returns:
            List[str]: 特征标签列表
        """
        feature_tags = []
        
        # 数字特征
        if re.search(r'\d+[%℃°]', text):
            feature_tags.append("数据")
        
        # 公式特征
        if re.search(r'[A-Z][a-z]*\d*\+|→|=', text):
            feature_tags.append("化学反应")
        
        # 列表特征
        if re.search(r'[1-9]\.|①②③|[a-z]\)|•', text):
            feature_tags.append("列表")
        
        # 时间特征
        if re.search(r'\d+[分秒小时天]|时间|duration', text):
            feature_tags.append("时间")
        
        # 温度压力特征
        if re.search(r'\d+℃|\d+°C|\d+K|\d+Pa|\d+MPa', text):
            feature_tags.append("工艺条件")
        
        # 浓度特征
        if re.search(r'\d+%|\d+mol/L|\d+g/L|浓度|含量', text):
            feature_tags.append("浓度")
        
        # 设备特征
        if re.search(r'反应器|蒸馏塔|换热器|泵|阀门|管道', text):
            feature_tags.append("设备")
        
        return feature_tags
    
    def extract_keywords(self, text: str, max_keywords: int = 10) -> List[str]:
        """
        从文本中提取关键词
        
        Args:
            text (str): 文本内容
            max_keywords (int): 最大关键词数
        
        Returns:
            List[str]: 关键词列表
        """
        try:
            # 简单的关键词提取（基于频率和长度）
            # 去除标点符号
            cleaned_text = re.sub(r'[^\w\s]', ' ', text)
            
            # 分词（简单按空格分割）
            words = cleaned_text.split()
            
            # 过滤长度和重要性
            valid_words = []
            for word in words:
                word = word.strip()
                # 只保留长度>=2的中文词或长度>=3的英文词
                if len(word) >= 2 and not word.isdigit():
                    valid_words.append(word)
            
            # 统计词频
            word_freq = {}
            for word in valid_words:
                word_freq[word] = word_freq.get(word, 0) + 1
            
            # 按频率排序，取前N个
            sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
            keywords = [word for word, freq in sorted_words[:max_keywords]]
            
            return keywords
            
        except Exception as e:
            logger.error(f"关键词提取失败: {str(e)}")
            return []
    
    def calculate_segment_similarity(self, text1: str, text2: str) -> float:
        """
        计算两个段落的相似度
        
        Args:
            text1 (str): 段落1
            text2 (str): 段落2
        
        Returns:
            float: 相似度分数 (0-1)
        """
        try:
            # 简单的词汇重叠相似度
            words1 = set(text1.lower().split())
            words2 = set(text2.lower().split())
            
            if not words1 or not words2:
                return 0.0
            
            intersection = len(words1.intersection(words2))
            union = len(words1.union(words2))
            
            similarity = intersection / union if union > 0 else 0.0
            return similarity
            
        except Exception as e:
            logger.error(f"相似度计算失败: {str(e)}")
            return 0.0

# 创建全局服务实例
segmentation_service = SegmentationService()