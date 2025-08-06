/*
QA.jsx - 页面组件：化工行业知识问答主页面，支持用户提问、查看回答、管理历史记录
*/

import React, { useState, useEffect } from "react";
import ChatBox from "../components/ChatBox";
import HistoryPanel from "../components/HistoryPanel";
import { 
  askQuestion, 
  fetchQAHistory, 
  deleteQARecord, 
  batchDeleteQARecords 
} from "../utils/qa-api";

const QA = () => {
  const [qaHistory, setQaHistory] = useState([]);
  const [selectedRecord, setSelectedRecord] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isHistoryLoading, setIsHistoryLoading] = useState(true);

  // 加载问答历史
  useEffect(() => {
    loadHistory();
  }, []);

  const loadHistory = async () => {
    setIsHistoryLoading(true);
    try {
      const history = await fetchQAHistory();
      setQaHistory(history);
    } catch (error) {
      console.error('加载历史记录失败:', error);
    } finally {
      setIsHistoryLoading(false);
    }
  };

  // 发送问题
  const handleSendQuestion = async (question, tags = []) => {
    setIsLoading(true);
    setSelectedRecord(null); // 清空当前查看的记录

    try {
      const result = await askQuestion(question, tags);
      
      if (result.ok) {
        const newRecord = result.data;
        
        // 添加到历史记录
        setQaHistory(prev => [newRecord, ...prev]);
        
        // 设置为当前显示的记录
        setSelectedRecord(newRecord);
      } else {
        alert('提问失败，请重试');
      }
    } catch (error) {
      alert(`提问出错: ${error.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  // 选择历史记录
  const handleSelectRecord = (record) => {
    setSelectedRecord(record);
  };

  // 删除单条记录
  const handleDeleteRecord = async (id) => {
    try {
      await deleteQARecord(id);
      setQaHistory(prev => prev.filter(record => record.id !== id));
      
      // 如果删除的是当前显示的记录，清空显示
      if (selectedRecord && selectedRecord.id === id) {
        setSelectedRecord(null);
      }
    } catch (error) {
      alert(`删除失败: ${error.message}`);
    }
  };

  // 批量删除记录
  const handleBatchDelete = async (ids) => {
    try {
      await batchDeleteQARecords(ids);
      setQaHistory(prev => prev.filter(record => !ids.includes(record.id)));
      
      // 如果删除的记录中包含当前显示的记录，清空显示
      if (selectedRecord && ids.includes(selectedRecord.id)) {
        setSelectedRecord(null);
      }
    } catch (error) {
      alert(`批量删除失败: ${error.message}`);
    }
  };

  return (
    <div className="max-w-7xl mx-auto p-6 space-y-6">
      {/* 页面标题 */}
      <div className="text-center">
        <h1 className="text-2xl font-bold">知识问答</h1>
        <p className="text-gray-600 mt-2">
          专业化工知识问答助手，为您提供准确的技术解答
        </p>
      </div>

      {/* 主要内容区域 - 左右布局 */}
      <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">
        {/* 左侧：历史记录面板 */}
        <div className="lg:col-span-2">
          <HistoryPanel
            history={qaHistory}
            onSelectRecord={handleSelectRecord}
            onDeleteRecord={handleDeleteRecord}
            onBatchDelete={handleBatchDelete}
            selectedRecord={selectedRecord}
            isLoading={isHistoryLoading}
          />
        </div>

        {/* 右侧：对话框 */}
        <div className="lg:col-span-3">
          <ChatBox
            currentRecord={selectedRecord}
            onSendQuestion={handleSendQuestion}
            isLoading={isLoading}
          />
        </div>
      </div>

      {/* 底部提示 */}
      <div className="text-center text-sm text-gray-500 bg-blue-50 p-4 rounded-lg">
        <p className="mb-2">💡 <strong>使用提示</strong></p>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-left">
          <div>
            <strong>• 提问技巧</strong>
            <br />描述具体场景，提供背景信息，使用专业术语
          </div>
          <div>
            <strong>• 标签分类</strong>
            <br />为问题添加标签便于后续查找和管理
          </div>
          <div>
            <strong>• 历史管理</strong>
            <br />可筛选、搜索、导出历史问答记录
          </div>
        </div>
      </div>
    </div>
  );
};

export default QA;
