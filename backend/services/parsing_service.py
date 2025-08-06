# parsing_service.py - 文档解析服务
# 负责处理不同格式文档的文本解析功能
# 支持 PDF (PyMuPDF)、DOCX (python-docx)、TXT (直接读取)

import fitz  # PyMuPDF
from docx import Document
import os
import logging
from typing import Tuple, Optional

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DocumentParsingService:
    """文档解析服务类"""
    
    def __init__(self):
        """初始化解析服务"""
        self.supported_types = {'pdf', 'docx', 'doc', 'txt'}
    
    def parse_document(self, file_path: str, file_type: str) -> Tuple[bool, str]:
        """
        解析文档并提取文本内容
        
        Args:
            file_path (str): 文件路径
            file_type (str): 文件类型 (pdf, docx, txt)
        
        Returns:
            Tuple[bool, str]: (是否成功, 解析的文本内容或错误信息)
        """
        try:
            # 检查文件是否存在
            if not os.path.exists(file_path):
                return False, f"文件不存在: {file_path}"
            
            # 检查文件类型
            file_type = file_type.lower()
            if file_type not in self.supported_types:
                return False, f"不支持的文件类型: {file_type}"
            
            # 根据文件类型调用相应的解析方法
            if file_type == 'pdf':
                return self._parse_pdf(file_path)
            elif file_type in ['docx', 'doc']:
                return self._parse_docx(file_path)
            elif file_type == 'txt':
                return self._parse_txt(file_path)
            else:
                return False, f"未实现的文件类型: {file_type}"
                
        except Exception as e:
            logger.error(f"文档解析异常: {str(e)}")
            return False, f"解析失败: {str(e)}"
    
    def _parse_pdf(self, file_path: str) -> Tuple[bool, str]:
        """
        解析 PDF 文件
        
        Args:
            file_path (str): PDF 文件路径
        
        Returns:
            Tuple[bool, str]: (是否成功, 文本内容或错误信息)
        """
        doc = None
        try:
            # 验证文件是否为有效的PDF
            with open(file_path, 'rb') as f:
                header = f.read(4)
                if header != b'%PDF':
                    return False, "文件不是有效的PDF格式"
            
            # 尝试打开PDF文档
            doc = fitz.open(file_path)
            
            # 检查文档是否有效
            if doc.is_closed:
                return False, "PDF文档无法打开或已损坏"
            
            # 获取页数并验证
            try:
                page_count = doc.page_count
                if page_count <= 0:
                    return False, "PDF文档没有可读取的页面"
            except Exception as e:
                return False, f"无法读取PDF页数: {str(e)}"
            
            text_content = []
            
            # 遍历每一页
            for page_num in range(page_count):
                try:
                    page = doc.load_page(page_num)
                    text = page.get_text()
                    
                    if text.strip():  # 只添加非空文本
                        text_content.append(f"=== 第 {page_num + 1} 页 ===\n{text}")
                except Exception as e:
                    logger.warning(f"读取PDF第{page_num + 1}页失败: {str(e)}")
                    continue
            
            if not text_content:
                return False, "PDF文件中未找到可解析的文本内容（可能是扫描版或图像PDF）"
            
            full_text = "\n\n".join(text_content)
            logger.info(f"成功解析 PDF 文件: {file_path}, 共 {page_count} 页")
            return True, full_text
            
        except fitz.FileDataError:
            return False, "PDF文件数据损坏或格式不正确"
        except fitz.FileNotFoundError:
            return False, f"PDF文件不存在: {file_path}"
        except Exception as e:
            logger.error(f"PDF 解析失败: {str(e)}")
            return False, f"PDF解析失败: {str(e)}"
        finally:
            # 确保文档被正确关闭
            if doc and not doc.is_closed:
                try:
                    doc.close()
                except:
                    pass
    
    def _parse_docx(self, file_path: str) -> Tuple[bool, str]:
        """
        解析 DOCX/DOC 文件
        
        Args:
            file_path (str): DOCX 文件路径
        
        Returns:
            Tuple[bool, str]: (是否成功, 文本内容或错误信息)
        """
        try:
            doc = Document(file_path)
            text_content = []
            
            # 提取所有段落
            for i, paragraph in enumerate(doc.paragraphs):
                text = paragraph.text.strip()
                if text:  # 只添加非空段落
                    text_content.append(text)
            
            if not text_content:
                return False, "DOCX 文件中未找到可解析的文本内容"
            
            # 合并所有段落，用双换行分隔
            full_text = "\n\n".join(text_content)
            logger.info(f"成功解析 DOCX 文件: {file_path}, 共 {len(text_content)} 个段落")
            return True, full_text
            
        except Exception as e:
            logger.error(f"DOCX 解析失败: {str(e)}")
            return False, f"DOCX 解析失败: {str(e)}"
    
    def _parse_txt(self, file_path: str) -> Tuple[bool, str]:
        """
        解析 TXT 文件
        
        Args:
            file_path (str): TXT 文件路径
        
        Returns:
            Tuple[bool, str]: (是否成功, 文本内容或错误信息)
        """
        try:
            # 尝试多种编码格式
            encodings = ['utf-8', 'gbk', 'gb2312', 'latin-1']
            
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as file:
                        content = file.read()
                        
                    if content.strip():
                        logger.info(f"成功解析 TXT 文件: {file_path} (编码: {encoding})")
                        return True, content
                    else:
                        return False, "TXT 文件为空"
                        
                except UnicodeDecodeError:
                    continue
            
            return False, f"无法使用支持的编码格式读取 TXT 文件: {encodings}"
            
        except Exception as e:
            logger.error(f"TXT 解析失败: {str(e)}")
            return False, f"TXT 解析失败: {str(e)}"
    
    def get_text_summary(self, text: str, max_length: int = 200) -> str:
        """
        生成文本摘要
        
        Args:
            text (str): 完整文本
            max_length (int): 摘要最大长度
        
        Returns:
            str: 文本摘要
        """
        if not text:
            return ""
        
        # 清理文本
        clean_text = text.replace('\n', ' ').replace('\r', ' ')
        clean_text = ' '.join(clean_text.split())  # 去除多余空格
        
        # 截取摘要
        if len(clean_text) <= max_length:
            return clean_text
        else:
            return clean_text[:max_length] + "..."

# 创建全局服务实例
parsing_service = DocumentParsingService()