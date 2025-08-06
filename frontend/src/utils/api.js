/*
api.js - 与后端接口通信的工具封装（Mock 版本）
此文件统一封装 fetch（或 axios）请求，当前使用 setTimeout 模拟网络延迟。
*/

// 上传文件，接收 FormData，返回 Promise<{ok: boolean}>
export const uploadFiles = async (formData) => {
  // TODO: 将来替换为实际 fetch 调用
  return new Promise((resolve) => {
    setTimeout(() => resolve({ ok: true }), 1000);
  });
};

// 获取上传记录列表，返回 Promise<UploadRecord[]>
export const getUploadRecords = async () => {
  // 模拟历史数据
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve([
        {
          id: 1,
          name: "示例文档.pdf",
          createdAt: new Date().toISOString(),
        },
      ]);
    }, 500);
  });
};

// 删除文件
export const deleteFile = async (id) => {
  // 模拟删除成功
  return new Promise((resolve) => setTimeout(resolve, 300));
};

// 下载文件
export const downloadFile = async (record) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      let blob, fileName;
      
      // 如果有原始文件对象，直接下载原始文件
      if (record.fileObject) {
        blob = record.fileObject;
        fileName = record.name;
      } else {
        // 否则创建模拟的文件内容
        const content = `这是模拟的文件内容：${record.name}\n上传时间：${record.createdAt}\n文件ID：${record.id}`;
        blob = new Blob([content], { type: 'text/plain;charset=utf-8' });
        fileName = record.name.replace(/\.[^/.]+$/, "") + "_downloaded.txt";
      }
      
      const url = URL.createObjectURL(blob);
      
      // 创建下载链接并触发下载
      const a = document.createElement('a');
      a.href = url;
      a.download = fileName;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      
      resolve();
    }, 300);
  });
};

// ====== 文档解析相关接口 ======

// 解析本地文件
export const parseLocalFile = async (formData) => {
  // 模拟解析本地文件
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({
        ok: true,
        data: {
          id: Date.now(),
          fileName: "示例文档.pdf",
          content: "这是解析后的文档内容示例...\n\n第一章：化工基础\n化工是一门重要的工程学科，涉及化学反应、传质传热等基本原理。\n\n第二章：反应器设计\n反应器是化工生产的核心设备，其设计直接影响生产效率和产品质量。",
          createdAt: new Date().toISOString(),
        }
      });
    }, 2000);
  });
};

// 解析数据库中的文件
export const parseFromDB = async (fileId) => {
  // 模拟从数据库解析文件
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({
        ok: true,
        data: {
          id: Date.now(),
          fileName: `数据库文件_${fileId}.pdf`,
          content: `解析数据库文件 ID: ${fileId} 的内容...\n\n包含专业化工知识：\n- 化学反应动力学\n- 传质传热原理\n- 设备设计规范\n- 安全操作指南`,
          createdAt: new Date().toISOString(),
        }
      });
    }, 1500);
  });
};

// 获取解析历史记录
export const getParseHistory = async () => {
  // 模拟历史解析记录
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve([
        {
          id: 1,
          fileName: "化工原理手册.pdf",
          content: "这是之前解析的化工原理手册内容...",
          createdAt: new Date(Date.now() - 86400000).toISOString(),
        },
        {
          id: 2,
          fileName: "反应器设计指南.docx",
          content: "反应器设计的基本原则和方法...",
          createdAt: new Date(Date.now() - 172800000).toISOString(),
        },
      ]);
    }, 500);
  });
};

// 删除解析记录
export const deleteParseRecord = async (id) => {
  // 模拟删除解析记录
  return new Promise((resolve) => setTimeout(resolve, 300));
};

// 导出解析内容
export const exportParsedContent = async (record, format = 'txt') => {
  return new Promise((resolve) => {
    setTimeout(() => {
      const content = `文件名: ${record.fileName}\n解析时间: ${record.createdAt}\n\n内容:\n${record.content}`;
      const mimeType = format === 'pdf' ? 'application/pdf' : 'text/plain';
      const fileName = record.fileName.replace(/\.[^/.]+$/, "") + `.${format}`;
      
      const blob = new Blob([content], { type: mimeType });
      const url = URL.createObjectURL(blob);
      
      const a = document.createElement('a');
      a.href = url;
      a.download = fileName;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      
      resolve();
    }, 300);
  });
};
