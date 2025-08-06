/*
segment-api.js - 文档分段相关API接口
专门处理文档分段、标签管理等功能的API封装
*/

// 获取文档分段内容
export const getDocumentSegments = async (docId) => {
  // 模拟获取文档分段数据
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({
        ok: true,
        data: {
          id: docId,
          fileName: "化工原理手册.pdf",
          totalPages: 5,
          segments: [
            {
              id: 1,
              content: "化工是一门重要的工程学科，它涉及化学反应、传质传热等基本原理。化工过程的设计和优化需要深入理解这些基础理论。",
              pageNumber: 1,
              startIndex: 0,
              endIndex: 68,
              tags: ["定义", "基础概念"],
              recommendedTags: ["化工", "工程", "理论"]
            },
            {
              id: 2,
              content: "反应器是化工生产的核心设备，其设计直接影响生产效率和产品质量。常见的反应器类型包括管式反应器、搅拌釜式反应器等。",
              pageNumber: 1,
              startIndex: 69,
              endIndex: 137,
              tags: ["设备"],
              recommendedTags: ["反应器", "设备", "设计"]
            },
            {
              id: 3,
              content: "传质是物质在相间或相内的传递过程，是化工单元操作的基础。包括分子扩散、对流传质等机理。",
              pageNumber: 2,
              startIndex: 0,
              endIndex: 58,
              tags: [],
              recommendedTags: ["传质", "单元操作", "扩散"]
            },
            {
              id: 4,
              content: "传热过程在化工生产中具有重要意义，主要包括导热、对流和辐射三种方式。热交换器的设计需要考虑传热效率。",
              pageNumber: 2,
              startIndex: 59,
              endIndex: 117,
              tags: ["传热"],
              recommendedTags: ["传热", "热交换器", "效率"]
            },
            {
              id: 5,
              content: "化工安全是生产过程中的重中之重，包括工艺安全、设备安全、环境安全等多个方面。必须建立完善的安全管理体系。",
              pageNumber: 3,
              startIndex: 0,
              endIndex: 68,
              tags: ["安全", "管理"],
              recommendedTags: ["安全", "管理体系", "环境"]
            },
            {
              id: 6,
              content: "质量控制是确保产品符合标准的重要环节，需要建立完善的检测体系和质量管理流程。",
              pageNumber: 4,
              startIndex: 0,
              endIndex: 48,
              tags: [],
              recommendedTags: ["质量", "控制", "检测"]
            },
            {
              id: 7,
              content: "化工自动化技术的发展大大提高了生产效率，包括DCS系统、PLC控制等先进技术的应用。",
              pageNumber: 5,
              startIndex: 0,
              endIndex: 54,
              tags: ["自动化"],
              recommendedTags: ["自动化", "DCS", "PLC"]
            }
          ]
        }
      });
    }, 800);
  });
};

// 保存段落标签
export const saveSegmentTags = async (segmentId, tags) => {
  // 模拟保存标签
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({ ok: true });
    }, 300);
  });
};

// 批量保存段落标签
export const batchSaveSegmentTags = async (segmentIds, tags) => {
  // 模拟批量保存标签
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({ ok: true });
    }, 500);
  });
};

// 获取推荐标签
export const getRecommendedTags = async () => {
  // 模拟获取推荐标签
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve([
        "定义", "概念", "原理", "方法", "应用", "实验", "结论", 
        "背景", "设备", "工艺", "安全", "环境", "管理", "设计",
        "化工", "反应器", "传质", "传热", "分离", "控制"
      ]);
    }, 200);
  });
};