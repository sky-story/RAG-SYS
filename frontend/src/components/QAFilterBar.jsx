/*
QAFilterBar.jsx - 问答筛选栏组件
提供搜索框和日期筛选功能，位于历史记录面板顶部
*/

import React from "react";

const QAFilterBar = ({ 
  searchTerm, 
  onSearchChange, 
  dateFilter, 
  onDateFilterChange,
  onClear 
}) => {
  const dateOptions = [
    { value: 'all', label: '全部时间' },
    { value: 'today', label: '今天' },
    { value: 'week', label: '近一周' },
    { value: 'month', label: '近一月' },
    { value: 'custom', label: '自定义' }
  ];

  return (
    <div className="space-y-3 p-3 bg-gray-50 border-b">
      {/* 搜索框 */}
      <div className="relative">
        <input
          type="text"
          value={searchTerm}
          onChange={(e) => onSearchChange(e.target.value)}
          placeholder="搜索问题或回答内容..."
          className="w-full px-3 py-2 pr-10 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
        />
        {searchTerm && (
          <button
            onClick={() => onSearchChange("")}
            className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
          >
            ✕
          </button>
        )}
      </div>

      {/* 日期筛选 */}
      <div className="flex items-center space-x-2">
        <span className="text-sm text-gray-600 whitespace-nowrap">时间:</span>
        <select
          value={dateFilter}
          onChange={(e) => onDateFilterChange(e.target.value)}
          className="flex-1 px-2 py-1 border border-gray-300 rounded text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        >
          {dateOptions.map(option => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      </div>

      {/* 清空按钮 */}
      {(searchTerm || dateFilter !== 'all') && (
        <button
          onClick={onClear}
          className="w-full px-3 py-1 text-sm bg-gray-200 text-gray-700 rounded hover:bg-gray-300 transition-colors"
        >
          清空筛选
        </button>
      )}
    </div>
  );
};

export default QAFilterBar;