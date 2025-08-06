/*
HistoryPanel.jsx - 历史记录面板组件
左侧组件：展示问答历史记录，支持点击查看、删除、批量操作
*/

import React, { useState, useMemo } from "react";
import QAFilterBar from "./QAFilterBar";
import TagSelector from "./TagSelector";
import ExportButton from "./ExportButton";

const HistoryPanel = ({ 
  history = [], 
  onSelectRecord, 
  onDeleteRecord,
  onBatchDelete,
  selectedRecord = null,
  isLoading = false
}) => {
  const [searchTerm, setSearchTerm] = useState("");
  const [dateFilter, setDateFilter] = useState("all");
  const [selectedTags, setSelectedTags] = useState([]);
  const [selectedRecords, setSelectedRecords] = useState([]);
  const [showBatchActions, setShowBatchActions] = useState(false);

  // 筛选逻辑
  const filteredHistory = useMemo(() => {
    let filtered = history;

    // 关键词搜索
    if (searchTerm.trim()) {
      const term = searchTerm.toLowerCase();
      filtered = filtered.filter(record => 
        record.question.toLowerCase().includes(term) ||
        record.answer.toLowerCase().includes(term)
      );
    }

    // 标签筛选
    if (selectedTags.length > 0) {
      filtered = filtered.filter(record =>
        selectedTags.some(tag => record.tags.includes(tag))
      );
    }

    // 日期筛选
    if (dateFilter !== 'all') {
      const now = new Date();
      const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
      
      filtered = filtered.filter(record => {
        const recordDate = new Date(record.timestamp);
        
        switch (dateFilter) {
          case 'today':
            return recordDate >= today;
          case 'week':
            const weekAgo = new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000);
            return recordDate >= weekAgo;
          case 'month':
            const monthAgo = new Date(today.getTime() - 30 * 24 * 60 * 60 * 1000);
            return recordDate >= monthAgo;
          default:
            return true;
        }
      });
    }

    return filtered.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
  }, [history, searchTerm, selectedTags, dateFilter]);

  // 清空筛选
  const handleClearFilters = () => {
    setSearchTerm("");
    setDateFilter("all");
    setSelectedTags([]);
  };

  // 记录选择
  const handleRecordToggle = (recordId) => {
    setSelectedRecords(prev => 
      prev.includes(recordId)
        ? prev.filter(id => id !== recordId)
        : [...prev, recordId]
    );
  };

  // 全选/取消全选
  const handleSelectAll = () => {
    const allIds = filteredHistory.map(record => record.id);
    const isAllSelected = allIds.every(id => selectedRecords.includes(id));
    
    if (isAllSelected) {
      setSelectedRecords(prev => prev.filter(id => !allIds.includes(id)));
    } else {
      setSelectedRecords(prev => [...new Set([...prev, ...allIds])]);
    }
  };

  // 批量删除
  const handleBatchDeleteClick = () => {
    if (selectedRecords.length === 0) return;
    
    if (window.confirm(`确定要删除选中的 ${selectedRecords.length} 条记录吗？`)) {
      onBatchDelete(selectedRecords);
      setSelectedRecords([]);
      setShowBatchActions(false);
    }
  };

  const isAllSelected = filteredHistory.length > 0 && 
    filteredHistory.every(record => selectedRecords.includes(record.id));

  // 获取选中的记录对象
  const selectedRecordObjects = history.filter(record => 
    selectedRecords.includes(record.id)
  );

  return (
    <div className="border rounded-lg overflow-hidden bg-white">
      {/* 头部 */}
      <div className="bg-gray-50 px-4 py-3 border-b">
        <div className="flex justify-between items-center">
          <h3 className="font-semibold">问答历史</h3>
          <div className="flex items-center space-x-2">
            <ExportButton 
              selectedRecords={selectedRecordObjects}
              allRecords={history}
              disabled={isLoading}
            />
            <button
              onClick={() => setShowBatchActions(!showBatchActions)}
              className="px-3 py-1 text-sm bg-gray-200 text-gray-700 rounded hover:bg-gray-300"
            >
              {showBatchActions ? '取消' : '批量'}
            </button>
          </div>
        </div>
      </div>

      {/* 筛选栏 */}
      <QAFilterBar
        searchTerm={searchTerm}
        onSearchChange={setSearchTerm}
        dateFilter={dateFilter}
        onDateFilterChange={setDateFilter}
        onClear={handleClearFilters}
      />

      {/* 标签筛选 */}
      <TagSelector
        selectedTags={selectedTags}
        onTagsChange={setSelectedTags}
        mode="filter"
      />

      {/* 批量操作栏 */}
      {showBatchActions && (
        <div className="bg-yellow-50 px-4 py-2 border-b">
          <div className="flex justify-between items-center">
            <div className="flex items-center space-x-3">
              <label className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  checked={isAllSelected}
                  onChange={handleSelectAll}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <span className="text-sm">全选</span>
              </label>
              <span className="text-sm text-gray-600">
                已选择 {selectedRecords.length} 项
              </span>
            </div>
            <button
              onClick={handleBatchDeleteClick}
              disabled={selectedRecords.length === 0}
              className="px-3 py-1 text-sm bg-red-600 text-white rounded hover:bg-red-700 disabled:bg-gray-400"
            >
              删除选中
            </button>
          </div>
        </div>
      )}

      {/* 历史记录列表 */}
      <div className="max-h-[450px] overflow-y-auto">
        {isLoading ? (
          <div className="p-6 text-center text-gray-500">
            <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600 mx-auto mb-2"></div>
            <p>加载中...</p>
          </div>
        ) : filteredHistory.length === 0 ? (
          <div className="p-6 text-center text-gray-500">
            {history.length === 0 ? '暂无问答记录' : '没有找到匹配的记录'}
          </div>
        ) : (
          filteredHistory.map((record) => (
            <div
              key={record.id}
              className={`p-4 border-b hover:bg-gray-50 cursor-pointer transition-colors ${
                selectedRecord?.id === record.id ? 'bg-blue-50 border-blue-200' : ''
              }`}
              onClick={() => !showBatchActions && onSelectRecord(record)}
            >
              <div className="flex items-start space-x-3">
                {/* 批量选择框 */}
                {showBatchActions && (
                  <input
                    type="checkbox"
                    checked={selectedRecords.includes(record.id)}
                    onChange={(e) => {
                      e.stopPropagation();
                      handleRecordToggle(record.id);
                    }}
                    className="mt-1 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                )}

                {/* 记录内容 */}
                <div className="flex-1 min-w-0">
                  <div className="flex justify-between items-start mb-1">
                    <p className="text-sm font-medium text-gray-900 line-clamp-2">
                      {record.question}
                    </p>
                    {!showBatchActions && (
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          if (window.confirm('确定要删除这条记录吗？')) {
                            onDeleteRecord(record.id);
                          }
                        }}
                        className="text-gray-400 hover:text-red-600 ml-2"
                      >
                        ✕
                      </button>
                    )}
                  </div>
                  
                  <p className="text-xs text-gray-500 mb-2">
                    {new Date(record.timestamp).toLocaleString()}
                    {record.confidence && (
                      <span className="ml-2">置信度: {record.confidence}%</span>
                    )}
                  </p>
                  
                  {record.tags && record.tags.length > 0 && (
                    <div className="flex flex-wrap gap-1">
                      {record.tags.map((tag, index) => (
                        <span
                          key={index}
                          className="px-2 py-0.5 text-xs bg-blue-100 text-blue-800 rounded-full"
                        >
                          {tag}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {/* 底部统计 */}
      <div className="bg-gray-50 px-4 py-2 border-t text-sm text-gray-600">
        显示 {filteredHistory.length} / {history.length} 条记录
      </div>
    </div>
  );
};

export default HistoryPanel;