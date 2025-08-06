/*
SegmentSearch.jsx - 段落搜索组件
提供关键词搜索段落的功能，可在SegmentList顶部复用
*/

import React from "react";

const SegmentSearch = ({ searchTerm, onSearchChange, onClear, placeholder = "搜索段落内容..." }) => {
  return (
    <div className="flex items-center space-x-2 mb-4">
      <div className="flex-1 relative">
        <input
          type="text"
          value={searchTerm}
          onChange={(e) => onSearchChange(e.target.value)}
          placeholder={placeholder}
          className="w-full px-3 py-2 pr-10 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
        {searchTerm && (
          <button
            onClick={onClear}
            className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
          >
            ✕
          </button>
        )}
      </div>
      
      <div className="flex items-center text-sm text-gray-500">
        <span className="mr-2">🔍</span>
        <span>搜索</span>
      </div>
    </div>
  );
};

export default SegmentSearch;