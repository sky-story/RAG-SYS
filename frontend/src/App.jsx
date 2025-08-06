/*
App.jsx - React 路由配置入口
负责注册应用的路由结构，整合导航栏和页面组件。
管理全局状态，包括上传记录和解析记录。
*/

import React, { useState, useEffect } from "react";
import Navbar from "./components/Navbar";
import Home from "./pages/Home";
import Upload from "./pages/Upload";
import Parse from "./pages/Parse";
import Segment from "./pages/Segment";
import QA from "./pages/QA";
import { getUploadRecords, getParseHistory } from "./utils/api";
import "./index.css";

const App = () => {
  const [currentPage, setCurrentPage] = useState('home');
  
  // 全局状态 - 上传记录
  const [uploadRecords, setUploadRecords] = useState([]);
  
  // 全局状态 - 解析记录
  const [parseHistory, setParseHistory] = useState([]);

  // 初始化加载数据
  useEffect(() => {
    loadInitialData();
  }, []);

  const loadInitialData = async () => {
    try {
      // 加载上传记录和解析历史
      const [uploads, parsers] = await Promise.all([
        getUploadRecords(),
        getParseHistory()
      ]);
      setUploadRecords(uploads);
      setParseHistory(parsers);
    } catch (error) {
      console.error('加载初始数据失败:', error);
    }
  };

  // 添加新的上传记录
  const addUploadRecord = (newRecord) => {
    setUploadRecords(prev => [newRecord, ...prev]);
  };

  // 删除上传记录
  const removeUploadRecord = (id) => {
    setUploadRecords(prev => prev.filter(record => record.id !== id));
  };

  // 添加新的解析记录
  const addParseRecord = (newRecord) => {
    setParseHistory(prev => [newRecord, ...prev]);
  };

  // 删除解析记录
  const removeParseRecord = (id) => {
    setParseHistory(prev => prev.filter(record => record.id !== id));
  };

  const renderPage = () => {
    switch (currentPage) {
      case 'home':
        return <Home />;
      case 'upload':
        return (
          <Upload 
            uploadRecords={uploadRecords}
            onAddRecord={addUploadRecord}
            onRemoveRecord={removeUploadRecord}
          />
        );
      case 'parse':
        return (
          <Parse 
            uploadRecords={uploadRecords}
            parseHistory={parseHistory}
            onAddParseRecord={addParseRecord}
            onRemoveParseRecord={removeParseRecord}
          />
        );
      case 'segment':
        return (
          <Segment 
            parseHistory={parseHistory}
          />
        );
      case 'qa':
        return <QA />;
      default:
        return <Home />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex">
      <Navbar currentPage={currentPage} onNavigate={setCurrentPage} />
      <div className="flex-1 overflow-auto">
        {renderPage()}
      </div>
    </div>
  );
};

export default App;
