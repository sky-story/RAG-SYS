/*
dashboard-api.js - 仪表盘相关API接口
专门处理首页统计数据、图表数据等功能的API封装
*/

// 获取文档上传趋势数据
export const fetchUploadStats = async () => {
  // 模拟上传趋势数据
  return new Promise((resolve) => {
    setTimeout(() => {
      const today = new Date();
      const data = [];
      
      for (let i = 6; i >= 0; i--) {
        const date = new Date(today);
        date.setDate(date.getDate() - i);
        
        data.push({
          date: date.toISOString().split('T')[0],
          dateLabel: `${date.getMonth() + 1}/${date.getDate()}`,
          uploads: Math.floor(Math.random() * 20) + 5, // 5-25个文件
          weekday: date.toLocaleDateString('zh-CN', { weekday: 'short' })
        });
      }
      
      resolve({
        ok: true,
        data: data,
        total: data.reduce((sum, item) => sum + item.uploads, 0)
      });
    }, 400);
  });
};

// 获取问答频率趋势数据
export const fetchQATrends = async () => {
  // 模拟问答趋势数据
  return new Promise((resolve) => {
    setTimeout(() => {
      const today = new Date();
      const data = [];
      
      for (let i = 6; i >= 0; i--) {
        const date = new Date(today);
        date.setDate(date.getDate() - i);
        
        data.push({
          date: date.toISOString().split('T')[0],
          dateLabel: `${date.getMonth() + 1}/${date.getDate()}`,
          questions: Math.floor(Math.random() * 50) + 10, // 10-60个问题
          weekday: date.toLocaleDateString('zh-CN', { weekday: 'short' })
        });
      }
      
      resolve({
        ok: true,
        data: data,
        total: data.reduce((sum, item) => sum + item.questions, 0)
      });
    }, 500);
  });
};

// 获取文档类型分布数据
export const fetchDocTypes = async () => {
  // 模拟文档类型分布数据
  return new Promise((resolve) => {
    setTimeout(() => {
      const total = 150 + Math.floor(Math.random() * 100); // 150-250个文档
      
      const pdfCount = Math.floor(total * 0.6); // 60%
      const docxCount = Math.floor(total * 0.25); // 25%
      const txtCount = total - pdfCount - docxCount; // 其余
      
      resolve({
        ok: true,
        data: [
          { 
            type: 'PDF', 
            count: pdfCount, 
            percentage: Math.round((pdfCount / total) * 100),
            color: '#3B82F6' // blue
          },
          { 
            type: 'DOCX', 
            count: docxCount, 
            percentage: Math.round((docxCount / total) * 100),
            color: '#10B981' // green
          },
          { 
            type: 'TXT', 
            count: txtCount, 
            percentage: Math.round((txtCount / total) * 100),
            color: '#F59E0B' // yellow
          }
        ],
        total: total
      });
    }, 300);
  });
};

// 获取系统概览数据
export const fetchSystemOverview = async () => {
  // 模拟系统概览数据
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({
        ok: true,
        data: {
          totalDocuments: 186,
          totalQuestions: 342,
          totalUsers: 23,
          systemUptime: '99.8%',
          lastUpdated: new Date().toISOString()
        }
      });
    }, 200);
  });
};