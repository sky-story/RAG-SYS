/*
qa-api.js - 知识问答相关API接口
专门处理问答、历史记录管理等功能的API封装
更新为调用真实的RAG API
*/

const API_BASE_URL = "http://localhost:5001/api";

// 处理响应的通用函数
const handleResponse = async (response) => {
  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`HTTP ${response.status}: ${errorText}`);
  }
  
  const result = await response.json();
  return result;
};

// 提问接口 - 调用真实的 RAG API
export const askQuestion = async (question, tags = [], options = {}) => {
  try {
    console.log("发送问题到 RAG API:", question);
    
    // 构建请求数据
    const requestData = {
      question: question.trim(),
      // 可选参数
      top_k: options.top_k || 3,
      min_similarity: options.min_similarity || 0.0,
      use_openai_embedding: options.use_openai_embedding !== false, // 默认使用 OpenAI
      temperature: options.temperature || 0.1,
      max_tokens: options.max_tokens || 1000,
      // 如果有指定文件ID
      file_ids: options.file_ids || []
    };
    
    // 调用 RAG API
    const response = await fetch(`${API_BASE_URL}/qa/rag`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(requestData)
    });
    
    const result = await handleResponse(response);
    
    if (result.success) {
      const data = result.data;
      
      // 转换为前端期望的格式
      const qaRecord = {
        id: Date.now().toString(), // 临时ID，实际应该由后端生成
        question: data.question,
        answer: data.answer,
        tags: tags,
        timestamp: new Date().toISOString(),
        
        // RAG 相关信息
        responseType: data.response_type,
        totalTime: data.total_time,
        confidence: Math.round((data.quality_assessment?.quality_score || 50) * 1.2), // 转换为百分制
        
        // 检索结果
        retrievalResults: {
          totalSegments: data.retrieval_results?.total_segments || 0,
          usedSegments: data.retrieval_results?.used_segments || 0,
          searchTime: data.retrieval_results?.search_time || 0,
          citedSegments: data.retrieval_results?.cited_segments || []
        },
        
        // 生成结果
        generationResults: {
          model: data.generation_results?.model || 'unknown',
          generationTime: data.generation_results?.generation_time || 0,
          tokenUsage: data.generation_results?.token_usage || {},
          finishReason: data.generation_results?.finish_reason || 'unknown'
        },
        
        // 质量评估
        qualityAssessment: data.quality_assessment || {},
        
        // 上下文使用
        contextUsed: data.context_used || false
      };
      
      console.log("RAG 回答成功:", qaRecord);
      return { ok: true, data: qaRecord };
    } else {
      throw new Error(result.msg || 'RAG 问答失败');
    }
    
  } catch (error) {
    console.error("RAG 问答错误:", error);
    return { 
      ok: false, 
      error: error.message,
      // 返回一个错误记录
      data: {
        id: Date.now().toString(),
        question: question,
        answer: `抱歉，问答服务遇到错误：${error.message}`,
        tags: tags,
        timestamp: new Date().toISOString(),
        responseType: 'error',
        totalTime: 0,
        confidence: 0,
        retrievalResults: { totalSegments: 0, usedSegments: 0, citedSegments: [] },
        generationResults: { model: 'error', tokenUsage: {} },
        qualityAssessment: { quality_score: 0, assessment: 'error' },
        contextUsed: false
      }
    };
  }
};

// 获取问答历史 - 暂时使用本地存储模拟
export const fetchQAHistory = async () => {
  try {
    // 从 localStorage 获取历史记录
    const historyData = localStorage.getItem('qa_history');
    if (historyData) {
      const history = JSON.parse(historyData);
      return history.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
    }
    return [];
  } catch (error) {
    console.error("获取问答历史失败:", error);
    return [];
  }
};

// 保存问答记录到本地存储
export const saveQARecord = async (record) => {
  try {
    const history = await fetchQAHistory();
    const newHistory = [record, ...history.slice(0, 99)]; // 最多保存100条记录
    localStorage.setItem('qa_history', JSON.stringify(newHistory));
    return true;
  } catch (error) {
    console.error("保存问答记录失败:", error);
    return false;
  }
};

// 删除问答记录
export const deleteQARecord = async (id) => {
  try {
    const history = await fetchQAHistory();
    const filteredHistory = history.filter(record => record.id !== id);
    localStorage.setItem('qa_history', JSON.stringify(filteredHistory));
    return true;
  } catch (error) {
    console.error("删除问答记录失败:", error);
    return false;
  }
};

// 批量删除问答记录
export const batchDeleteQARecords = async (ids) => {
  try {
    const history = await fetchQAHistory();
    const filteredHistory = history.filter(record => !ids.includes(record.id));
    localStorage.setItem('qa_history', JSON.stringify(filteredHistory));
    return true;
  } catch (error) {
    console.error("批量删除问答记录失败:", error);
    return false;
  }
};

// 获取问答标签
export const getQATags = async () => {
  // 返回常用的化工标签
  return [
    "技术问题", "设备", "工艺", "安全", "材料", "反应", 
    "分离", "传热", "传质", "控制", "环保", "质量",
    "设计", "操作", "维护", "故障", "优化", "标准"
  ];
};

// 搜索问答历史
export const searchQAHistory = async (keyword, tags = []) => {
  try {
    const history = await fetchQAHistory();
    let filtered = history;
    
    // 关键词过滤
    if (keyword.trim()) {
      const lowerKeyword = keyword.toLowerCase();
      filtered = filtered.filter(record =>
        record.question.toLowerCase().includes(lowerKeyword) ||
        record.answer.toLowerCase().includes(lowerKeyword)
      );
    }
    
    // 标签过滤
    if (tags.length > 0) {
      filtered = filtered.filter(record =>
        tags.some(tag => record.tags.includes(tag))
      );
    }
    
    return filtered;
  } catch (error) {
    console.error("搜索问答历史失败:", error);
    return [];
  }
};

// 导出问答历史
export const exportQAHistory = async (format = 'json') => {
  try {
    const history = await fetchQAHistory();
    
    if (format === 'json') {
      const dataStr = JSON.stringify(history, null, 2);
      const dataBlob = new Blob([dataStr], { type: 'application/json' });
      const url = URL.createObjectURL(dataBlob);
      
      const link = document.createElement('a');
      link.href = url;
      link.download = `qa_history_${new Date().getTime()}.json`;
      link.click();
      
      URL.revokeObjectURL(url);
      return true;
    }
    
    // 其他格式可以在这里扩展
    return false;
  } catch (error) {
    console.error("导出问答历史失败:", error);
    return false;
  }
};

// 获取问答统计信息
export const getQAStats = async () => {
  try {
    const history = await fetchQAHistory();
    
    const stats = {
      totalQuestions: history.length,
      avgConfidence: history.length > 0 ? 
        Math.round(history.reduce((sum, record) => sum + (record.confidence || 0), 0) / history.length) : 0,
      tagDistribution: {},
      timeDistribution: {},
      responseTypeDistribution: {}
    };
    
    // 统计标签分布
    history.forEach(record => {
      record.tags.forEach(tag => {
        stats.tagDistribution[tag] = (stats.tagDistribution[tag] || 0) + 1;
      });
      
      // 统计响应类型分布
      const responseType = record.responseType || 'unknown';
      stats.responseTypeDistribution[responseType] = (stats.responseTypeDistribution[responseType] || 0) + 1;
    });
    
    return stats;
  } catch (error) {
    console.error("获取问答统计失败:", error);
    return {
      totalQuestions: 0,
      avgConfidence: 0,
      tagDistribution: {},
      timeDistribution: {},
      responseTypeDistribution: {}
    };
  }
};

// 健康检查 - 检查RAG服务状态
export const checkQAServiceHealth = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/qa/health`);
    const result = await handleResponse(response);
    return result;
  } catch (error) {
    console.error("QA服务健康检查失败:", error);
    return {
      success: false,
      error: error.message
    };
  }
};

// 获取可用文件列表
export const getAvailableFiles = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/qa/available-files`);
    const result = await handleResponse(response);
    return result;
  } catch (error) {
    console.error("获取可用文件列表失败:", error);
    return {
      success: false,
      error: error.message
    };
  }
};