/*
api.js - 与后端接口通信的工具封装（真实 API 版本）
此文件统一封装 fetch 请求，连接到 Flask 后端服务
*/

// API 基础配置
const API_BASE_URL = 'http://localhost:5001/api';

// 通用错误处理
const handleResponse = async (response) => {
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ error: 'Network error' }));
    throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
  }
  return response.json();
};

// 上传文件，接收 FormData，返回 Promise<{ok: boolean}>
export const uploadFiles = async (formData) => {
  try {
    const response = await fetch(`${API_BASE_URL}/upload`, {
      method: 'POST',
      body: formData,
    });
    
    const result = await handleResponse(response);
    return {
      ok: result.success,
      data: result.data,
      message: result.message
    };
  } catch (error) {
    console.error('Upload failed:', error);
    return {
      ok: false,
      error: error.message
    };
  }
};

// 获取上传记录列表，返回 Promise<UploadRecord[]>
export const getUploadRecords = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/files`);
    const result = await handleResponse(response);
    
    // 转换数据格式以适应前端组件
    return result.data.map(file => ({
      id: file.id,
      name: file.original_name || file.name,
      createdAt: file.upload_time,
      size: file.size,
      type: file.type,
      status: file.status
    }));
  } catch (error) {
    console.error('Failed to fetch upload records:', error);
    return [];
  }
};

// 删除文件
export const deleteFile = async (id) => {
  try {
    const response = await fetch(`${API_BASE_URL}/files/${id}`, {
      method: 'DELETE',
    });
    
    const result = await handleResponse(response);
    return {
      ok: result.success,
      message: result.message
    };
  } catch (error) {
    console.error('Delete failed:', error);
    throw error;
  }
};

// 下载文件
export const downloadFile = async (record) => {
  try {
    // 如果有原始文件对象（新上传的文件），直接下载
    if (record.fileObject) {
      const url = URL.createObjectURL(record.fileObject);
      const a = document.createElement('a');
      a.href = url;
      a.download = record.name;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      return;
    }
    
    // 否则从后端下载
    const response = await fetch(`${API_BASE_URL}/files/download/${record.id}`);
    
    if (!response.ok) {
      throw new Error(`Download failed: ${response.statusText}`);
    }
    
    const blob = await response.blob();
    const url = URL.createObjectURL(blob);
    
    // 从 Content-Disposition 头获取文件名，或使用默认名称
    const contentDisposition = response.headers.get('Content-Disposition');
    let fileName = record.name;
    if (contentDisposition) {
      const match = contentDisposition.match(/filename="?([^"]+)"?/);
      if (match) fileName = match[1];
    }
    
    const a = document.createElement('a');
    a.href = url;
    a.download = fileName;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
  } catch (error) {
    console.error('Download failed:', error);
    throw error;
  }
};

// ====== 文档解析相关接口 ======
// 连接到真实的Flask后端解析服务

// 解析本地文件
export const parseLocalFile = async (formData) => {
  try {
    const response = await fetch(`${API_BASE_URL}/parse/local`, {
      method: 'POST',
      body: formData,
    });
    
    // 直接处理响应，不使用 handleResponse
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ error: 'Network error' }));
      return {
        ok: false,
        error: errorData.error || `HTTP error! status: ${response.status}`
      };
    }
    
    const result = await response.json();
    
    if (result.success) {
      return {
        ok: true,
        data: {
          id: result.data.parse_id,
          fileName: result.data.original_name,
          content: result.data.text_content,
          summary: result.data.summary,
          textLength: result.data.text_length,
          fileType: result.data.file_type,
          createdAt: new Date().toISOString(),
        }
      };
    } else {
      return {
        ok: false,
        error: result.error || '解析失败'
      };
    }
  } catch (error) {
    console.error('Parse local file failed:', error);
    return {
      ok: false,
      error: error.message
    };
  }
};

// 解析数据库中的文件
export const parseFromDB = async (fileId) => {
  try {
    const response = await fetch(`${API_BASE_URL}/parse/database/${fileId}`, {
      method: 'POST',
    });
    
    // 直接处理响应，不使用 handleResponse
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ error: 'Network error' }));
      return {
        ok: false,
        error: errorData.error || `HTTP error! status: ${response.status}`
      };
    }
    
    const result = await response.json();
    
    if (result.success) {
      return {
        ok: true,
        data: {
          id: result.data.parse_id,
          fileName: result.data.original_name,
          content: result.data.text_content,
          summary: result.data.summary,
          textLength: result.data.text_length,
          fileType: result.data.file_type,
          fileId: result.data.file_id,
          createdAt: result.data.parsed_at || new Date().toISOString(),
        }
      };
    } else {
      return {
        ok: false,
        error: result.error || '解析失败'
      };
    }
  } catch (error) {
    console.error('Parse database file failed:', error);
    return {
      ok: false,
      error: error.message
    };
  }
};

// 获取解析历史记录
export const getParseHistory = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/parse/history`);
    const result = await handleResponse(response);
    
    if (result.success) {
      // 转换数据格式以适应前端组件
      return result.data.history.map(record => ({
        id: record.id,
        fileName: record.original_name,
        content: record.summary, // 使用摘要作为预览内容
        textLength: record.text_length,
        fileType: record.file_type,
        fileId: record.file_id,
        createdAt: record.parsed_at,
        status: record.status
      }));
    } else {
      throw new Error(result.error || '获取解析历史失败');
    }
  } catch (error) {
    console.error('Failed to fetch parse history:', error);
    return [];
  }
};

// 删除解析记录
export const deleteParseRecord = async (id) => {
  try {
    const response = await fetch(`${API_BASE_URL}/parse/${id}`, {
      method: 'DELETE',
    });
    
    const result = await handleResponse(response);
    return {
      ok: result.success,
      message: result.message
    };
  } catch (error) {
    console.error('Delete parse record failed:', error);
    throw error;
  }
};

// 导出解析内容
export const exportParsedContent = async (record, format = 'txt') => {
  try {
    const response = await fetch(`${API_BASE_URL}/parse/download/${record.id}`);
    
    if (!response.ok) {
      throw new Error(`Download failed: ${response.statusText}`);
    }
    
    const blob = await response.blob();
    const url = URL.createObjectURL(blob);
    
    // 从 Content-Disposition 头获取文件名，或使用默认名称
    const contentDisposition = response.headers.get('Content-Disposition');
    let fileName = `${record.fileName}_解析结果.txt`;
    if (contentDisposition) {
      const match = contentDisposition.match(/filename="?([^"]+)"?/);
      if (match) fileName = match[1];
    }
    
    const a = document.createElement('a');
    a.href = url;
    a.download = fileName;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
  } catch (error) {
    console.error('Export parsed content failed:', error);
    throw error;
  }
};

// 获取完整解析内容
export const getParsedContent = async (parseId) => {
  try {
    const response = await fetch(`${API_BASE_URL}/parse/${parseId}`);
    const result = await handleResponse(response);
    
    if (result.success) {
      return {
        ok: true,
        data: {
          id: result.data.parse_id,
          fileName: result.data.original_name,
          content: result.data.text_content,
          summary: result.data.summary,
          textLength: result.data.text_length,
          fileType: result.data.file_type,
          fileId: result.data.file_id,
          createdAt: result.data.parsed_at,
          status: result.data.status
        }
      };
    } else {
      throw new Error(result.error || '获取解析内容失败');
    }
  } catch (error) {
    console.error('Get parsed content failed:', error);
    return {
      ok: false,
      error: error.message
    };
  }
};

// 搜索解析文本
export const searchParsedTexts = async (keyword, limit = 50) => {
  try {
    const response = await fetch(`${API_BASE_URL}/parse/search?q=${encodeURIComponent(keyword)}&limit=${limit}`);
    const result = await handleResponse(response);
    
    if (result.success) {
      return {
        ok: true,
        data: result.data.results.map(record => ({
          id: record.id,
          fileName: record.original_name,
          content: record.summary,
          textLength: record.text_length,
          fileType: record.file_type,
          fileId: record.file_id,
          createdAt: record.parsed_at,
          status: record.status
        })),
        keyword: result.data.keyword,
        totalFound: result.data.total_found
      };
    } else {
      throw new Error(result.error || '搜索失败');
    }
  } catch (error) {
    console.error('Search parsed texts failed:', error);
    return {
      ok: false,
      error: error.message
    };
  }
};
