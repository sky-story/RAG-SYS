/*
DocumentViewer.jsx - 文档查看器组件
左侧组件：展示文档整体结构，包括分页导航和页码跳转功能
*/

import React from "react";

const DocumentViewer = ({ document, currentPage, onPageChange, highlightedSegments = [] }) => {
  if (!document) {
    return (
      <div className="border rounded-lg p-6 h-96 flex items-center justify-center">
        <div className="text-center text-gray-500">
          <p className="text-lg mb-2">📄</p>
          <p>请选择文档进行分段标注</p>
        </div>
      </div>
    );
  }

  // 生成页码列表
  const pages = Array.from({ length: document.totalPages }, (_, i) => i + 1);

  // 获取每页的段落数量
  const getPageSegmentCount = (pageNum) => {
    if (!document.segments) return 0;
    return document.segments.filter(segment => segment.pageNumber === pageNum).length;
  };

  // 检查页面是否有高亮段落
  const isPageHighlighted = (pageNum) => {
    if (!document.segments) return false;
    return document.segments
      .filter(segment => segment.pageNumber === pageNum)
      .some(segment => highlightedSegments.includes(segment.id));
  };

  return (
    <div className="border rounded-lg overflow-hidden">
      {/* 头部信息 */}
      <div className="bg-gray-50 px-4 py-3 border-b">
        <h3 className="font-semibold truncate">{document.fileName}</h3>
        <p className="text-sm text-gray-500">
          共 {document.totalPages} 页 · {document.segments?.length || 0} 个段落
        </p>
      </div>

      {/* 页面导航 */}
      <div className="p-4">
        <h4 className="text-sm font-medium mb-3">页面导航</h4>
        <div className="grid grid-cols-2 gap-2 max-h-64 overflow-y-auto">
          {pages.map((pageNum) => (
            <button
              key={pageNum}
              onClick={() => onPageChange(pageNum)}
              className={`p-3 rounded-lg border text-left transition-colors ${
                currentPage === pageNum
                  ? 'bg-blue-100 border-blue-500 text-blue-700'
                  : isPageHighlighted(pageNum)
                  ? 'bg-yellow-50 border-yellow-300 hover:bg-yellow-100'
                  : 'bg-white border-gray-200 hover:bg-gray-50'
              }`}
            >
              <div className="flex justify-between items-center">
                <span className="font-medium">第 {pageNum} 页</span>
                {isPageHighlighted(pageNum) && (
                  <span className="text-yellow-600">⭐</span>
                )}
              </div>
              <p className="text-xs text-gray-500 mt-1">
                {getPageSegmentCount(pageNum)} 个段落
              </p>
            </button>
          ))}
        </div>
      </div>

      {/* 文档信息 */}
      <div className="p-4 border-t bg-gray-50">
        <h4 className="text-sm font-medium mb-2">当前页面</h4>
        <div className="text-sm text-gray-600">
          <p>第 {currentPage} / {document.totalPages} 页</p>
          <p>包含 {getPageSegmentCount(currentPage)} 个段落</p>
        </div>
      </div>
    </div>
  );
};

export default DocumentViewer;