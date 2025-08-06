/*
Parse.jsx - 页面组件：实现化工知识库的文档解析功能，左侧为文件选择，右侧为内容预览与历史记录
*/

import React, { useState, useEffect } from "react";
import FileSelector from "../components/FileSelector";
import ParsedContent from "../components/ParsedContent";
import ProgressBar from "../components/ProgressBar";
import ParseHistory from "../components/ParseHistory";
import { 
  parseLocalFile, 
  parseFromDB, 
  getParseHistory, 
  deleteParseRecord 
} from "../utils/api";

const Parse = ({ uploadRecords = [], parseHistory = [], onAddParseRecord, onRemoveParseRecord }) => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [parsedData, setParsedData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [progress, setProgress] = useState(0);

  // 使用传入的 parseHistory 而不是本地状态

  // 开始解析
  const handleParse = async () => {
    if (!selectedFile) {
      alert('请先选择要解析的文件');
      return;
    }

    setIsLoading(true);
    setProgress(0);
    setParsedData(null);

    try {
      // 模拟进度更新
      const progressInterval = setInterval(() => {
        setProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return 90;
          }
          return prev + 10;
        });
      }, 200);

      let result;
      if (selectedFile.type === 'local') {
        const formData = new FormData();
        formData.append('file', selectedFile.file);
        result = await parseLocalFile(formData);
      } else {
        result = await parseFromDB(selectedFile.id);
      }

      clearInterval(progressInterval);
      setProgress(100);

      if (result.ok) {
        setParsedData(result.data);
        // 添加到解析历史
        onAddParseRecord(result.data);
      } else {
        alert('解析失败，请重试');
      }
    } catch (error) {
      alert(`解析出错: ${error.message}`);
    } finally {
      setIsLoading(false);
      setTimeout(() => setProgress(0), 1000);
    }
  };

  // 查看历史记录
  const handleViewHistory = (record) => {
    setParsedData(record);
    setSelectedFile({
      type: 'history',
      name: record.fileName,
    });
  };

  // 删除历史记录
  const handleDeleteHistory = async (id) => {
    try {
      await deleteParseRecord(id);
      onRemoveParseRecord(id);
      
      // 如果当前显示的是被删除的记录，清空显示
      if (parsedData && parsedData.id === id) {
        setParsedData(null);
      }
    } catch (error) {
      alert(`删除失败: ${error.message}`);
    }
  };

  return (
    <div className="max-w-7xl mx-auto p-6 space-y-6">
      <h1 className="text-2xl font-bold">文档解析</h1>
      
      {/* 主要内容区域 - 左右布局 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* 左侧：文件选择和操作 */}
        <div className="space-y-4">
          <FileSelector 
            onFileSelect={setSelectedFile}
            selectedFile={selectedFile}
            uploadRecords={uploadRecords}
          />
          
          {/* 解析按钮和进度 */}
          <div className="border rounded-lg p-4 space-y-3">
            <button
              onClick={handleParse}
              disabled={!selectedFile || isLoading}
              className="w-full px-4 py-2 bg-blue-600 text-white rounded disabled:bg-gray-400 disabled:cursor-not-allowed hover:bg-blue-700"
            >
              {isLoading ? '解析中...' : '开始解析'}
            </button>
            
            {/* 进度条 */}
            {isLoading && (
              <div className="space-y-2">
                <p className="text-sm text-gray-600">解析进度</p>
                <ProgressBar progress={progress} />
              </div>
            )}
          </div>
        </div>

        {/* 右侧：解析结果展示 */}
        <div>
          <ParsedContent 
            parsedData={parsedData}
            isLoading={isLoading}
          />
        </div>
      </div>

      {/* 底部：历史记录 */}
      <ParseHistory 
        history={parseHistory}
        onView={handleViewHistory}
        onDelete={handleDeleteHistory}
      />
    </div>
  );
};

export default Parse;
