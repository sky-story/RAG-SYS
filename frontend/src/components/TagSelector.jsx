/*
TagSelector.jsx - 标签选择器组件
用于问答的标签分类器，便于快速检索和分类问题
*/

import React, { useState, useEffect } from "react";
import { getQATags } from "../utils/qa-api";

const TagSelector = ({ 
  selectedTags = [], 
  onTagsChange, 
  mode = "filter" // "filter" 或 "select"
}) => {
  const [availableTags, setAvailableTags] = useState([]);
  const [showAll, setShowAll] = useState(false);

  useEffect(() => {
    getQATags().then(setAvailableTags);
  }, []);

  const handleTagToggle = (tag) => {
    if (mode === "select") {
      // 选择模式：可以多选
      const newTags = selectedTags.includes(tag)
        ? selectedTags.filter(t => t !== tag)
        : [...selectedTags, tag];
      onTagsChange(newTags);
    } else {
      // 筛选模式：单选
      onTagsChange(selectedTags.includes(tag) ? [] : [tag]);
    }
  };

  const displayTags = showAll ? availableTags : availableTags.slice(0, 6);

  return (
    <div className="p-3 border-b bg-white">
      <div className="flex justify-between items-center mb-2">
        <h4 className="text-sm font-medium text-gray-700">
          {mode === "filter" ? "按标签筛选" : "选择标签"}
        </h4>
        {selectedTags.length > 0 && (
          <button
            onClick={() => onTagsChange([])}
            className="text-xs text-gray-500 hover:text-gray-700"
          >
            清空
          </button>
        )}
      </div>

      <div className="flex flex-wrap gap-1">
        {displayTags.map((tag) => (
          <button
            key={tag}
            onClick={() => handleTagToggle(tag)}
            className={`px-2 py-1 text-xs rounded-full border transition-colors ${
              selectedTags.includes(tag)
                ? 'bg-blue-100 border-blue-500 text-blue-800'
                : 'bg-gray-100 border-gray-300 text-gray-700 hover:bg-gray-200'
            }`}
          >
            {tag}
          </button>
        ))}
        
        {availableTags.length > 6 && (
          <button
            onClick={() => setShowAll(!showAll)}
            className="px-2 py-1 text-xs text-blue-600 hover:text-blue-800"
          >
            {showAll ? '收起' : `+${availableTags.length - 6}个`}
          </button>
        )}
      </div>

      {mode === "select" && selectedTags.length > 0 && (
        <div className="mt-2 pt-2 border-t">
          <span className="text-xs text-gray-600">已选择:</span>
          <div className="flex flex-wrap gap-1 mt-1">
            {selectedTags.map((tag) => (
              <span
                key={tag}
                className="px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded-full"
              >
                {tag}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default TagSelector;