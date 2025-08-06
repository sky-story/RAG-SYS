/*
qa-api.js - 知识问答相关API接口
专门处理问答、历史记录管理等功能的API封装
*/

// 提问接口
export const askQuestion = async (question, tags = []) => {
  // 模拟问答接口
  return new Promise((resolve) => {
    setTimeout(() => {
      // 模拟不同类型的回答
      let answer = "";
      const lowerQuestion = question.toLowerCase();
      
      if (lowerQuestion.includes("化工") || lowerQuestion.includes("反应器")) {
        answer = "化工反应器是化学工业中最重要的设备之一。常见的反应器类型包括：\n\n1. **管式反应器**：适用于连续流动反应，传热传质效果好\n2. **搅拌釜式反应器**：适用于液相反应，混合效果佳\n3. **固定床反应器**：催化剂固定，操作简单\n4. **流化床反应器**：传热效果好，适用于气固反应\n\n选择反应器时需要考虑反应特性、物料性质、操作条件等因素。";
      } else if (lowerQuestion.includes("传质") || lowerQuestion.includes("传热")) {
        answer = "传质和传热是化工单元操作的基础原理：\n\n**传质过程**：\n- 分子扩散：由浓度梯度驱动\n- 对流传质：由流体流动引起\n- 主要应用：精馏、萃取、吸收等\n\n**传热过程**：\n- 导热：固体内部热量传递\n- 对流：流体与固体间热量传递\n- 辐射：电磁波形式的热量传递\n\n这些原理在换热器、反应器设计中都有重要应用。";
      } else if (lowerQuestion.includes("安全") || lowerQuestion.includes("事故")) {
        answer = "化工安全是生产过程中的重中之重：\n\n**主要安全措施**：\n1. 工艺安全管理(PSM)\n2. 危险与可操作性分析(HAZOP)\n3. 安全仪表系统(SIS)\n4. 应急响应计划\n\n**常见危险因素**：\n- 易燃易爆物质\n- 有毒有害化学品\n- 高温高压设备\n- 机械伤害\n\n建议建立完善的安全管理体系，定期进行安全培训和演练。";
      } else {
        answer = `关于"${question}"的问题，我理解您想了解相关的化工知识。\n\n根据我的知识库，这可能涉及到化工原理、设备设计或工艺流程等方面。建议您：\n\n1. 查阅相关的化工手册和标准\n2. 咨询专业的化工工程师\n3. 参考学术文献和研究资料\n\n如果您能提供更具体的背景信息，我可以给出更准确的回答。`;
      }

      resolve({
        ok: true,
        data: {
          id: Date.now(),
          question: question,
          answer: answer,
          tags: tags,
          timestamp: new Date().toISOString(),
          confidence: Math.round(Math.random() * 30 + 70), // 70-100的置信度
        }
      });
    }, 1000 + Math.random() * 2000); // 1-3秒的随机延迟
  });
};

// 获取问答历史
export const fetchQAHistory = async () => {
  // 模拟历史记录
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve([
        {
          id: 1,
          question: "化工反应器有哪些类型？",
          answer: "化工反应器主要包括管式反应器、搅拌釜式反应器、固定床反应器、流化床反应器等...",
          tags: ["技术问题", "设备"],
          timestamp: new Date(Date.now() - 86400000).toISOString(),
          confidence: 95
        },
        {
          id: 2,
          question: "传质过程的基本原理是什么？",
          answer: "传质是物质在相间或相内的传递过程，主要包括分子扩散和对流传质...",
          tags: ["理论知识", "原理"],
          timestamp: new Date(Date.now() - 172800000).toISOString(),
          confidence: 88
        },
        {
          id: 3,
          question: "化工生产安全注意事项有哪些？",
          answer: "化工生产安全需要注意工艺安全、设备安全、环境安全等多个方面...",
          tags: ["安全", "管理"],
          timestamp: new Date(Date.now() - 259200000).toISOString(),
          confidence: 92
        }
      ]);
    }, 500);
  });
};

// 删除问答记录
export const deleteQARecord = async (id) => {
  // 模拟删除
  return new Promise((resolve) => {
    setTimeout(() => resolve({ ok: true }), 300);
  });
};

// 批量删除问答记录
export const batchDeleteQARecords = async (ids) => {
  // 模拟批量删除
  return new Promise((resolve) => {
    setTimeout(() => resolve({ ok: true }), 500);
  });
};

// 导出问答记录
export const exportQARecords = async (records, format = 'txt') => {
  return new Promise((resolve) => {
    setTimeout(() => {
      let content = '';
      
      if (format === 'txt') {
        content = records.map(record => 
          `问题：${record.question}\n回答：${record.answer}\n标签：${record.tags.join(', ')}\n时间：${new Date(record.timestamp).toLocaleString()}\n置信度：${record.confidence}%\n\n${'='.repeat(50)}\n\n`
        ).join('');
      } else {
        // PDF格式的模拟内容
        content = `知识问答记录导出\n生成时间：${new Date().toLocaleString()}\n\n${records.map(record => 
          `Q: ${record.question}\nA: ${record.answer}\n`
        ).join('\n')}`;
      }
      
      const blob = new Blob([content], { 
        type: format === 'pdf' ? 'application/pdf' : 'text/plain;charset=utf-8' 
      });
      const url = URL.createObjectURL(blob);
      
      const a = document.createElement('a');
      a.href = url;
      a.download = `问答记录_${new Date().toISOString().split('T')[0]}.${format}`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      
      resolve();
    }, 300);
  });
};

// 获取问答标签
export const getQATags = async () => {
  // 模拟获取标签
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve([
        "技术问题", "理论知识", "安全", "设备", "工艺", "原理",
        "管理", "设计", "维护", "故障", "学习资料", "常识"
      ]);
    }, 200);
  });
};