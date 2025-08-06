/*
SegmentList.jsx - 段落列表组件
中间组件：显示当前文档的所有段落，支持选择、关键词搜索、高亮显示
*/

import React, { useMemo } from "react";
import SegmentSearch from "./SegmentSearch";

const SegmentList = ({ 
  segments = [], 
  selectedSegments = [], 
  onSegmentSelect, 
  onSegmentToggle,
  searchTerm = "",
  onSearchChange,
  highlightedPage = null,
  currentEditingSegment = null
}) => {
  // 过滤段落
  const filteredSegments = useMemo(() => {
    let filtered = segments;
    
    // 关键词搜索
    if (searchTerm.trim()) {
      filtered = filtered.filter(segment =>
        segment.content.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }
    
    // 页面过滤（如果指定了高亮页面）
    if (highlightedPage) {
      filtered = filtered.filter(segment => segment.pageNumber === highlightedPage);
    }
    
    return filtered;
  }, [segments, searchTerm, highlightedPage]);

  // 全选/取消全选
  const handleSelectAll = () => {
    const allIds = filteredSegments.map(segment => segment.id);
    const isAllSelected = allIds.every(id => selectedSegments.includes(id));
    
    if (isAllSelected) {
      // 取消全选
      allIds.forEach(id => {
        if (selectedSegments.includes(id)) {
          onSegmentToggle(id);
        }
      });
    } else {
      // 全选
      allIds.forEach(id => {
        if (!selectedSegments.includes(id)) {
          onSegmentToggle(id);
        }
      });
    }
  };

  const isAllSelected = filteredSegments.length > 0 && 
    filteredSegments.every(segment => selectedSegments.includes(segment.id));

  return (
    <div className="border rounded-lg overflow-hidden">
      {/* 头部 */}
      <div className="bg-gray-50 px-4 py-3 border-b">
        <div className="flex justify-between items-center mb-3">
          <h3 className="font-semibold">段落列表</h3>
          <div className="flex items-center space-x-2">
            {filteredSegments.length > 0 && (
              <button
                onClick={handleSelectAll}
                className="px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700"
              >
                {isAllSelected ? '取消全选' : '全选'}
              </button>
            )}
            <span className="text-sm text-gray-500">
              {selectedSegments.length > 0 && `已选 ${selectedSegments.length} 项`}
            </span>
          </div>
        </div>
        
        {/* 搜索框 */}
        <SegmentSearch
          searchTerm={searchTerm}
          onSearchChange={onSearchChange}
          onClear={() => onSearchChange("")}
          placeholder="搜索段落内容..."
        />
      </div>

      {/* 段落列表 */}
      <div className="max-h-96 overflow-y-auto">
        {filteredSegments.length === 0 ? (
          <div className="p-6 text-center text-gray-500">
            {searchTerm ? '没有找到匹配的段落' : '暂无段落数据'}
          </div>
        ) : (
          filteredSegments.map((segment) => (
            <div
              key={segment.id}
              className={`p-4 border-b hover:bg-gray-50 cursor-pointer transition-colors ${
                selectedSegments.includes(segment.id) ? 'bg-blue-50 border-blue-200' : ''
              } ${
                currentEditingSegment === segment.id ? 'ring-2 ring-green-500' : ''
              }`}
              onClick={() => onSegmentSelect(segment)}
            >
              <div className="flex items-start space-x-3">
                {/* 选择框 */}
                <input
                  type="checkbox"
                  checked={selectedSegments.includes(segment.id)}
                  onChange={(e) => {
                    e.stopPropagation();
                    onSegmentToggle(segment.id);
                  }}
                  className="mt-1 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                
                {/* 段落内容 */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded">
                      第 {segment.pageNumber} 页 · 段落 {segment.id}
                    </span>
                    {currentEditingSegment === segment.id && (
                      <span className="text-xs text-green-600 bg-green-100 px-2 py-1 rounded">
                        编辑中
                      </span>
                    )}
                  </div>
                  
                  <p className="text-sm text-gray-800 leading-relaxed mb-2">
                    {searchTerm ? (
                      // 高亮搜索关键词
                      segment.content.split(new RegExp(`(${searchTerm})`, 'gi')).map((part, index) =>
                        part.toLowerCase() === searchTerm.toLowerCase() ? (
                          <mark key={index} className="bg-yellow-200">{part}</mark>
                        ) : part
                      )
                    ) : (
                      segment.content
                    )}
                  </p>
                  
                  {/* 标签显示 */}
                  {segment.tags && segment.tags.length > 0 && (
                    <div className="flex flex-wrap gap-1">
                      {segment.tags.map((tag, index) => (
                        <span
                          key={index}
                          className="px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded-full"
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
        显示 {filteredSegments.length} / {segments.length} 个段落
        {highlightedPage && (
          <span className="ml-2 text-blue-600">
            （第 {highlightedPage} 页）
          </span>
        )}
      </div>
    </div>
  );
};

export default SegmentList;