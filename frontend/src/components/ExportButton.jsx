/*
ExportButton.jsx - 导出按钮组件
支持将选中或全部问答记录导出为TXT/PDF格式
*/

import React, { useState } from "react";
import { exportQARecords } from "../utils/qa-api";

const ExportButton = ({ 
  selectedRecords = [], 
  allRecords = [], 
  disabled = false 
}) => {
  const [isExporting, setIsExporting] = useState(false);
  const [showOptions, setShowOptions] = useState(false);

  const handleExport = async (format, useSelected = false) => {
    setIsExporting(true);
    setShowOptions(false);

    try {
      const recordsToExport = useSelected && selectedRecords.length > 0 
        ? selectedRecords 
        : allRecords;

      if (recordsToExport.length === 0) {
        alert('没有可导出的记录');
        return;
      }

      await exportQARecords(recordsToExport, format);
      
      const count = recordsToExport.length;
      const type = useSelected ? '选中' : '全部';
      alert(`成功导出${type} ${count} 条记录为 ${format.toUpperCase()} 格式`);
    } catch (error) {
      alert(`导出失败: ${error.message}`);
    } finally {
      setIsExporting(false);
    }
  };

  return (
    <div className="relative">
      <button
        onClick={() => setShowOptions(!showOptions)}
        disabled={disabled || isExporting}
        className="flex items-center space-x-2 px-3 py-2 bg-green-600 text-white rounded hover:bg-green-700 disabled:bg-gray-400 text-sm"
      >
        <span>📤</span>
        <span>{isExporting ? '导出中...' : '导出'}</span>
        <span className="text-xs">▼</span>
      </button>

      {showOptions && (
        <div className="absolute top-full right-0 mt-1 bg-white border border-gray-300 rounded shadow-lg z-10 min-w-48">
          <div className="p-2">
            <div className="text-xs text-gray-600 mb-2 border-b pb-2">
              可导出记录：
              <br />
              • 选中：{selectedRecords.length} 条
              <br />
              • 全部：{allRecords.length} 条
            </div>
            
            {/* 导出选中记录 */}
            {selectedRecords.length > 0 && (
              <div className="mb-2">
                <div className="text-xs text-gray-600 mb-1">导出选中 ({selectedRecords.length} 条):</div>
                <div className="flex space-x-1">
                  <button
                    onClick={() => handleExport('txt', true)}
                    className="flex-1 px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded hover:bg-blue-200"
                  >
                    TXT
                  </button>
                  <button
                    onClick={() => handleExport('pdf', true)}
                    className="flex-1 px-2 py-1 text-xs bg-red-100 text-red-800 rounded hover:bg-red-200"
                  >
                    PDF
                  </button>
                </div>
              </div>
            )}

            {/* 导出全部记录 */}
            <div>
              <div className="text-xs text-gray-600 mb-1">导出全部 ({allRecords.length} 条):</div>
              <div className="flex space-x-1">
                <button
                  onClick={() => handleExport('txt', false)}
                  className="flex-1 px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded hover:bg-blue-200"
                >
                  TXT
                </button>
                <button
                  onClick={() => handleExport('pdf', false)}
                  className="flex-1 px-2 py-1 text-xs bg-red-100 text-red-800 rounded hover:bg-red-200"
                >
                  PDF
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* 点击外部关闭选项 */}
      {showOptions && (
        <div 
          className="fixed inset-0 z-0" 
          onClick={() => setShowOptions(false)}
        />
      )}
    </div>
  );
};

export default ExportButton;