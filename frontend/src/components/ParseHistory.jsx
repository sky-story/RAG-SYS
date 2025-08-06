/*
ParseHistory.jsx - 解析历史记录组件
展示历史解析记录，支持查看详情和删除操作。
*/

import React, { useState } from "react";

const ParseHistory = ({ history, onDelete, onView }) => {
  const [expandedId, setExpandedId] = useState(null);

  const toggleExpand = (id) => {
    setExpandedId(expandedId === id ? null : id);
  };

  if (history.length === 0) {
    return (
      <div className="border rounded-lg p-6 text-center text-gray-500">
        <p>暂无解析历史记录</p>
      </div>
    );
  }

  return (
    <div className="border rounded-lg overflow-hidden">
      <div className="bg-gray-50 px-4 py-3 border-b">
        <h3 className="font-semibold">解析历史</h3>
      </div>
      
      <div className="divide-y max-h-64 overflow-y-auto">
        {history.map((record) => (
          <div key={record.id} className="p-4">
            <div className="flex items-center justify-between">
              <div className="flex-1">
                <p className="font-medium">{record.fileName}</p>
                <p className="text-sm text-gray-500">
                  {new Date(record.createdAt).toLocaleString()}
                </p>
              </div>
              
              <div className="flex space-x-2">
                <button
                  onClick={() => toggleExpand(record.id)}
                  className="px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700"
                >
                  {expandedId === record.id ? '收起' : '预览'}
                </button>
                <button
                  onClick={() => onView(record)}
                  className="px-3 py-1 text-sm bg-green-600 text-white rounded hover:bg-green-700"
                >
                  查看
                </button>
                <button
                  onClick={() => {
                    if (window.confirm('确定删除此解析记录？')) {
                      onDelete(record.id);
                    }
                  }}
                  className="px-3 py-1 text-sm bg-red-600 text-white rounded hover:bg-red-700"
                >
                  删除
                </button>
              </div>
            </div>
            
            {/* 展开的内容预览 */}
            {expandedId === record.id && (
              <div className="mt-3 p-3 bg-gray-50 rounded text-sm">
                <p className="text-gray-700">
                  {record.content.length > 200 
                    ? record.content.substring(0, 200) + '...' 
                    : record.content
                  }
                </p>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default ParseHistory;