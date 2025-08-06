/*
segment-api.js - 文档分段相关API接口
专门处理文档分段、标签管理等功能的API封装
*/

// API 基础配置
const API_BASE_URL = 'http://localhost:5001/api';

// 处理API响应的通用函数
const handleResponse = async (response) => {
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ error: 'Network error' }));
    throw new Error(errorData.msg || errorData.error || `HTTP error! status: ${response.status}`);
  }
  return response.json();
};

// 创建文档分段
export const createDocumentSegments = async (fileId) => {
  try {
    const response = await fetch(`${API_BASE_URL}/segment/create/${fileId}`, {
      method: 'POST',
    });
    
    const result = await handleResponse(response);
    
    if (result.code === 200) {
      return {
        ok: true,
        data: result.data
      };
    } else {
      return {
        ok: false,
        error: result.msg || '创建分段失败'
      };
    }
  } catch (error) {
    console.error('Create segments failed:', error);
    return {
      ok: false,
      error: error.message
    };
  }
};

// 获取文档分段内容
export const getDocumentSegments = async (fileId) => {
  try {
    const response = await fetch(`${API_BASE_URL}/segment/file/${fileId}`);
    
    const result = await handleResponse(response);
    
    if (result.code === 200) {
      // 转换后端数据格式为前端期望的格式
      const segments = result.data.segments.map((segment, index) => ({
        id: segment.segment_id,
        text: segment.text,  // 统一使用text字段
        content: segment.text,  // 保持兼容性
        order: segment.order,
        tags: segment.tags || [],
        characterCount: segment.character_count,
        wordCount: segment.word_count,
        createdAt: segment.created_at,
        updatedAt: segment.updated_at
      }));

      return {
        ok: true,
        data: {
          fileId: result.data.file_id,
          segmentCount: result.data.segment_count,
          segments: segments
        }
      };
    } else {
      return {
        ok: false,
        error: result.msg || '获取分段失败'
      };
    }
  } catch (error) {
    console.error('Get segments failed:', error);
    return {
      ok: false,
      error: error.message
    };
  }
};

// 保存段落标签
export const saveSegmentTags = async (segmentId, tags) => {
  try {
    const response = await fetch(`${API_BASE_URL}/segment/tag`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        segment_id: segmentId,
        tags: tags
      }),
    });
    
    const result = await handleResponse(response);
    
    if (result.code === 200) {
      return {
        ok: true,
        data: result.data
      };
    } else {
      return {
        ok: false,
        error: result.msg || '保存标签失败'
      };
    }
  } catch (error) {
    console.error('Save segment tags failed:', error);
    return {
      ok: false,
      error: error.message
    };
  }
};

// 批量保存段落标签
export const batchSaveSegmentTags = async (updates) => {
  try {
    const response = await fetch(`${API_BASE_URL}/segment/tag/batch`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        updates: updates
      }),
    });
    
    const result = await handleResponse(response);
    
    if (result.code === 200) {
      return {
        ok: true,
        data: result.data
      };
    } else {
      return {
        ok: false,
        error: result.msg || '批量保存标签失败'
      };
    }
  } catch (error) {
    console.error('Batch save segment tags failed:', error);
    return {
      ok: false,
      error: error.message
    };
  }
};

// 获取段落推荐标签
export const getRecommendedTags = async (segmentId) => {
  try {
    const response = await fetch(`${API_BASE_URL}/segment/recommend/${segmentId}`);
    
    const result = await handleResponse(response);
    
    if (result.code === 200) {
      return {
        ok: true,
        data: {
          segmentId: result.data.segment_id,
          currentTags: result.data.current_tags,
          recommendedTags: result.data.recommended_tags,
          keywords: result.data.keywords,
          textPreview: result.data.text_preview
        }
      };
    } else {
      return {
        ok: false,
        error: result.msg || '获取推荐标签失败'
      };
    }
  } catch (error) {
    console.error('Get recommended tags failed:', error);
    return {
      ok: false,
      error: error.message
    };
  }
};

// 搜索段落
export const searchSegments = async (keyword, limit = 50) => {
  try {
    const response = await fetch(`${API_BASE_URL}/segment/search?keyword=${encodeURIComponent(keyword)}&limit=${limit}`);
    
    const result = await handleResponse(response);
    
    if (result.code === 200) {
      return {
        ok: true,
        data: {
          keyword: result.data.keyword,
          totalFound: result.data.total_found,
          segments: result.data.segments
        }
      };
    } else {
      return {
        ok: false,
        error: result.msg || '搜索失败'
      };
    }
  } catch (error) {
    console.error('Search segments failed:', error);
    return {
      ok: false,
      error: error.message
    };
  }
};

// 按标签查询段落
export const getSegmentsByTags = async (tags, limit = 50) => {
  try {
    const tagsParam = Array.isArray(tags) ? tags.join(',') : tags;
    const response = await fetch(`${API_BASE_URL}/segment/tags?tags=${encodeURIComponent(tagsParam)}&limit=${limit}`);
    
    const result = await handleResponse(response);
    
    if (result.code === 200) {
      return {
        ok: true,
        data: {
          tags: result.data.tags,
          totalFound: result.data.total_found,
          segments: result.data.segments
        }
      };
    } else {
      return {
        ok: false,
        error: result.msg || '按标签查询失败'
      };
    }
  } catch (error) {
    console.error('Get segments by tags failed:', error);
    return {
      ok: false,
      error: error.message
    };
  }
};

// 获取分段统计信息
export const getSegmentStats = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/segment/stats`);
    
    const result = await handleResponse(response);
    
    if (result.code === 200) {
      return {
        ok: true,
        data: result.data
      };
    } else {
      return {
        ok: false,
        error: result.msg || '获取统计信息失败'
      };
    }
  } catch (error) {
    console.error('Get segment stats failed:', error);
    return {
      ok: false,
      error: error.message
    };
  }
};

// 删除文件的所有分段
export const deleteFileSegments = async (fileId) => {
  try {
    const response = await fetch(`${API_BASE_URL}/segment/file/${fileId}`, {
      method: 'DELETE',
    });
    
    const result = await handleResponse(response);
    
    if (result.code === 200) {
      return {
        ok: true,
        data: result.data
      };
    } else {
      return {
        ok: false,
        error: result.msg || '删除分段失败'
      };
    }
  } catch (error) {
    console.error('Delete file segments failed:', error);
    return {
      ok: false,
      error: error.message
    };
  }
};