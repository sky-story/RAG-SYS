# -*- coding: utf-8 -*-
"""
generator.py
OpenAI 文本生成服务

功能：
1. 使用 OpenAI Chat Completion API 生成回答
2. 基于检索到的上下文构建 RAG prompt
3. 支持流式响应和批量响应
4. 提供化工领域专业的问答能力
5. 管理 token 使用和成本控制

作者：AI Assistant
日期：2025-08-07
"""

import logging
import openai
import tiktoken
from typing import List, Dict, Any, Optional, Iterator, Tuple
from config import Config
from datetime import datetime

logger = logging.getLogger(__name__)


class GeneratorService:
    """
    OpenAI 文本生成服务类
    
    负责使用 OpenAI 模型基于检索上下文生成回答
    """
    
    def __init__(self):
        """初始化生成服务"""
        self.openai_client = openai.OpenAI(api_key=Config.OPENAI_API_KEY)
        self.chat_model = Config.OPENAI_CHAT_MODEL
        self.max_context_length = Config.RAG_MAX_CONTEXT_LENGTH
        
        # 初始化 tokenizer
        try:
            self.tokenizer = tiktoken.encoding_for_model(self.chat_model)
        except KeyError:
            # 如果模型不支持，使用默认的 tokenizer
            self.tokenizer = tiktoken.get_encoding("cl100k_base")
        
        logger.info(f"GeneratorService 初始化完成，使用模型: {self.chat_model}")
    
    def count_tokens(self, text: str) -> int:
        """
        计算文本的 token 数量
        
        Args:
            text (str): 待计算的文本
            
        Returns:
            int: token 数量
        """
        try:
            return len(self.tokenizer.encode(text))
        except Exception as e:
            logger.warning(f"Token 计算失败: {str(e)}，使用估算方式")
            # 粗略估算：平均每个 token 约 4 个字符
            return len(text) // 4
    
    def build_rag_prompt(self, question: str, context: str, 
                        cited_segments: List[Dict[str, Any]] = None) -> str:
        """
        构建 RAG 提示词
        
        Args:
            question (str): 用户问题
            context (str): 检索到的上下文
            cited_segments (List[Dict]): 被引用的段落信息
            
        Returns:
            str: 格式化的提示词
        """
        try:
            # 基础的 RAG 提示词模板
            prompt_template = """你是一个化工领域的专家，请根据以下提供的资料内容回答用户的问题。

## 资料内容：
{context}

## 回答要求：
1. 请基于上述资料内容进行回答，确保答案的准确性和专业性
2. 如果资料中没有明确的答案，请明确说明"根据提供的资料无法确定"
3. 可以适当结合化工领域的专业知识进行解释
4. 回答应该条理清晰，逻辑性强
5. 如果涉及数据或具体数值，请注明来源

## 用户提问：
{question}

## 专业回答："""

            # 格式化提示词
            formatted_prompt = prompt_template.format(
                context=context,
                question=question
            )
            
            # 计算 token 数量
            token_count = self.count_tokens(formatted_prompt)
            logger.info(f"构建 RAG 提示词完成，token 数量: {token_count}")
            
            # 如果 token 数量过多，尝试截断上下文
            max_prompt_tokens = 3000  # 为回答预留 token
            if token_count > max_prompt_tokens:
                logger.warning(f"提示词过长 ({token_count} tokens)，尝试截断上下文")
                # 简单的截断策略
                context_tokens = self.count_tokens(context)
                reduction_ratio = (max_prompt_tokens - 500) / token_count  # 预留安全边距
                
                if reduction_ratio > 0:
                    target_context_length = int(len(context) * reduction_ratio)
                    truncated_context = context[:target_context_length] + "\\n\\n[内容已截断...]"
                    
                    formatted_prompt = prompt_template.format(
                        context=truncated_context,
                        question=question
                    )
                    logger.info(f"上下文截断后，token 数量: {self.count_tokens(formatted_prompt)}")
            
            return formatted_prompt
            
        except Exception as e:
            logger.error(f"构建 RAG 提示词失败: {str(e)}")
            # 返回简化版本
            return f"请回答以下化工领域问题：\\n\\n{question}"
    
    def generate_answer(self, question: str, context: str = "", 
                       cited_segments: List[Dict[str, Any]] = None,
                       temperature: float = 0.1, max_tokens: int = 1000) -> Dict[str, Any]:
        """
        生成问答回答
        
        Args:
            question (str): 用户问题
            context (str): 检索到的上下文
            cited_segments (List[Dict]): 被引用的段落信息
            temperature (float): 温度参数，控制回答的创造性
            max_tokens (int): 最大生成 token 数
            
        Returns:
            Dict[str, Any]: 生成结果
        """
        try:
            start_time = datetime.now()
            
            # 构建提示词
            if context.strip():
                prompt = self.build_rag_prompt(question, context, cited_segments)
                response_type = "rag_based"
            else:
                # 如果没有上下文，直接回答
                prompt = f"作为化工领域专家，请回答以下问题：\\n\\n{question}"
                response_type = "direct_answer"
            
            logger.info(f"开始生成回答，类型: {response_type}")
            
            # 构建消息
            messages = [
                {
                    "role": "system",
                    "content": "你是一个专业的化工领域专家，具有丰富的理论知识和实践经验。请提供准确、专业、有用的回答。"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
            
            # 调用 OpenAI API
            response = self.openai_client.chat.completions.create(
                model=self.chat_model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=0.9,
                frequency_penalty=0.0,
                presence_penalty=0.0
            )
            
            # 提取回答
            answer = response.choices[0].message.content
            finish_reason = response.choices[0].finish_reason
            
            # 计算耗时
            generation_time = (datetime.now() - start_time).total_seconds()
            
            # 计算 token 使用量
            usage = response.usage
            prompt_tokens = usage.prompt_tokens
            completion_tokens = usage.completion_tokens
            total_tokens = usage.total_tokens
            
            logger.info(f"回答生成完成，耗时: {generation_time:.2f}s, tokens: {total_tokens}")
            
            return {
                'success': True,
                'answer': answer,
                'response_type': response_type,
                'finish_reason': finish_reason,
                'generation_time': generation_time,
                'token_usage': {
                    'prompt_tokens': prompt_tokens,
                    'completion_tokens': completion_tokens,
                    'total_tokens': total_tokens
                },
                'model': self.chat_model,
                'cited_segments': cited_segments or [],
                'context_used': bool(context.strip())
            }
            
        except Exception as e:
            logger.error(f"生成回答失败: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'answer': f"抱歉，回答生成时遇到错误：{str(e)}",
                'response_type': 'error',
                'generation_time': 0,
                'token_usage': {},
                'model': self.chat_model,
                'cited_segments': [],
                'context_used': False
            }
    
    def generate_answer_stream(self, question: str, context: str = "", 
                             cited_segments: List[Dict[str, Any]] = None,
                             temperature: float = 0.1, max_tokens: int = 1000) -> Iterator[Dict[str, Any]]:
        """
        流式生成问答回答
        
        Args:
            question (str): 用户问题
            context (str): 检索到的上下文
            cited_segments (List[Dict]): 被引用的段落信息
            temperature (float): 温度参数
            max_tokens (int): 最大生成 token 数
            
        Yields:
            Dict[str, Any]: 流式生成的内容
        """
        try:
            start_time = datetime.now()
            
            # 构建提示词
            if context.strip():
                prompt = self.build_rag_prompt(question, context, cited_segments)
                response_type = "rag_based"
            else:
                prompt = f"作为化工领域专家，请回答以下问题：\\n\\n{question}"
                response_type = "direct_answer"
            
            logger.info(f"开始流式生成回答，类型: {response_type}")
            
            # 构建消息
            messages = [
                {
                    "role": "system",
                    "content": "你是一个专业的化工领域专家，具有丰富的理论知识和实践经验。请提供准确、专业、有用的回答。"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
            
            # 发送初始状态
            yield {
                'type': 'start',
                'response_type': response_type,
                'context_used': bool(context.strip()),
                'cited_segments': cited_segments or []
            }
            
            # 调用 OpenAI 流式 API
            stream = self.openai_client.chat.completions.create(
                model=self.chat_model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True
            )
            
            # 流式输出
            full_answer = ""
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    content = chunk.choices[0].delta.content
                    full_answer += content
                    
                    yield {
                        'type': 'content',
                        'content': content,
                        'accumulated': full_answer
                    }
            
            # 发送完成状态
            generation_time = (datetime.now() - start_time).total_seconds()
            
            yield {
                'type': 'end',
                'full_answer': full_answer,
                'generation_time': generation_time,
                'model': self.chat_model
            }
            
        except Exception as e:
            logger.error(f"流式生成失败: {str(e)}")
            yield {
                'type': 'error',
                'error': str(e),
                'model': self.chat_model
            }
    
    def evaluate_answer_quality(self, question: str, answer: str, 
                               context: str = "") -> Dict[str, Any]:
        """
        评估回答质量
        
        Args:
            question (str): 原始问题
            answer (str): 生成的回答
            context (str): 使用的上下文
            
        Returns:
            Dict[str, Any]: 质量评估结果
        """
        try:
            # 基础质量指标
            answer_length = len(answer)
            answer_tokens = self.count_tokens(answer)
            
            # 检查回答是否包含关键元素
            has_technical_terms = any(term in answer.lower() for term in [
                '化工', '反应', '催化', '工艺', '温度', '压力', '分离', '纯化'
            ])
            
            has_quantitative_info = any(char in answer for char in ['%', '℃', 'MPa', 'mol', 'kg'])
            
            # 检查是否明确说明了不确定性
            acknowledges_uncertainty = any(phrase in answer for phrase in [
                '无法确定', '资料中没有', '需要进一步', '不够明确'
            ])
            
            # 基于上下文的回答
            context_based = bool(context.strip())
            
            # 计算质量分数（简单的启发式评估）
            quality_score = 0
            if answer_length > 50:  # 回答有一定长度
                quality_score += 20
            if has_technical_terms:  # 包含技术术语
                quality_score += 30
            if has_quantitative_info:  # 包含定量信息
                quality_score += 25
            if context_based:  # 基于上下文
                quality_score += 25
            
            # 归一化分数
            quality_score = min(100, quality_score)
            
            return {
                'quality_score': quality_score,
                'answer_length': answer_length,
                'answer_tokens': answer_tokens,
                'has_technical_terms': has_technical_terms,
                'has_quantitative_info': has_quantitative_info,
                'acknowledges_uncertainty': acknowledges_uncertainty,
                'context_based': context_based,
                'assessment': 'good' if quality_score >= 70 else 'fair' if quality_score >= 40 else 'poor'
            }
            
        except Exception as e:
            logger.error(f"回答质量评估失败: {str(e)}")
            return {
                'quality_score': 0,
                'assessment': 'error',
                'error': str(e)
            }
    
    def get_service_status(self) -> Dict[str, Any]:
        """
        获取生成服务状态
        
        Returns:
            Dict[str, Any]: 服务状态信息
        """
        try:
            # 检查 OpenAI 连接
            openai_available = bool(Config.OPENAI_API_KEY)
            
            # 测试 API 连接（可选）
            api_accessible = False
            if openai_available:
                try:
                    # 发送一个简单的测试请求
                    test_response = self.openai_client.chat.completions.create(
                        model=self.chat_model,
                        messages=[{"role": "user", "content": "测试"}],
                        max_tokens=1
                    )
                    api_accessible = True
                except:
                    api_accessible = False
            
            return {
                'service_status': 'healthy' if openai_available else 'limited',
                'openai_available': openai_available,
                'api_accessible': api_accessible,
                'chat_model': self.chat_model,
                'max_context_length': self.max_context_length,
                'tokenizer_available': self.tokenizer is not None
            }
            
        except Exception as e:
            logger.error(f"获取生成服务状态失败: {str(e)}")
            return {
                'service_status': 'unhealthy',
                'error': str(e)
            }


# 全局单例实例
_generator_service = None


def get_generator_service() -> GeneratorService:
    """
    获取生成服务单例
    
    Returns:
        GeneratorService: 生成服务实例
    """
    global _generator_service
    
    if _generator_service is None:
        logger.info("初始化生成服务单例")
        _generator_service = GeneratorService()
    
    return _generator_service


if __name__ == "__main__":
    # 测试代码
    import logging
    logging.basicConfig(level=logging.INFO)
    
    generator = GeneratorService()
    
    # 测试问题和上下文
    test_question = "化工反应器设计需要考虑哪些因素？"
    test_context = """1. 化工反应器设计需要考虑反应动力学、传热传质、流体力学等多个方面。
2. 温度控制是关键因素，需要根据反应特性选择合适的温度范围。
3. 压力条件会影响反应速率和产物选择性。"""
    
    try:
        print("测试回答生成:")
        result = generator.generate_answer(test_question, test_context)
        
        if result['success']:
            print(f"生成成功:")
            print(f"回答: {result['answer']}")
            print(f"类型: {result['response_type']}")
            print(f"耗时: {result['generation_time']:.2f}s")
            print(f"Token 使用: {result['token_usage']}")
            
            # 测试质量评估
            print("\\n测试质量评估:")
            quality = generator.evaluate_answer_quality(
                test_question, result['answer'], test_context
            )
            print(f"质量评估: {quality}")
        else:
            print(f"生成失败: {result['error']}")
        
        # 测试服务状态
        print("\\n服务状态:")
        status = generator.get_service_status()
        print(f"状态: {status}")
        
    except Exception as e:
        print(f"测试失败: {e}")