/*
ParsedContent.jsx - 解析内容展示组件
展示解析后的文档全文内容，支持导出功能。
*/

import React from "react";
import { exportParsedContent } from "../utils/api";

const ParsedContent = ({ parsedData, isLoading }) => {
  const handleExport = async (format) => {
    if (parsedData) {
      try {
        await exportParsedContent(parsedData, format);
      } catch (error) {
        alert(`导出失败: ${error.message}`);
      }
    }
  };

  if (isLoading) {
    return (
      <div className="border rounded-lg p-6 h-96 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-2"></div>
          <p className="text-gray-500">正在解析文档...</p>
        </div>
      </div>
    );
  }

  if (!parsedData) {
    return (
      <div className="border rounded-lg p-6 h-96 flex items-center justify-center">
        <div className="text-center text-gray-500">
          <p className="text-lg mb-2">📄</p>
          <p>请选择文件并点击"开始解析"</p>
        </div>
      </div>
    );
  }

  return (
    <div className="border rounded-lg overflow-hidden">
      {/* 头部操作栏 */}
      <div className="bg-gray-50 px-4 py-3 border-b flex justify-between items-center">
        <div>
          <h3 className="font-semibold">{parsedData.fileName}</h3>
          <p className="text-sm text-gray-500">
            解析时间: {new Date(parsedData.createdAt).toLocaleString()}
          </p>
        </div>
        <div className="flex space-x-2">
          <button
            onClick={() => handleExport('txt')}
            className="px-3 py-1 text-sm bg-green-600 text-white rounded hover:bg-green-700"
          >
            导出TXT
          </button>
          <button
            onClick={() => handleExport('pdf')}
            className="px-3 py-1 text-sm bg-red-600 text-white rounded hover:bg-red-700"
          >
            导出PDF
          </button>
        </div>
      </div>

      {/* 内容区域 */}
      <div className="p-4 h-96 overflow-y-auto bg-white">
        <pre className="whitespace-pre-wrap text-sm leading-relaxed text-gray-800">
          {parsedData.content}
        </pre>
      </div>
    </div>
  );
};

export default ParsedContent;