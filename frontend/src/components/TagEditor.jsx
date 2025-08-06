/*
TagEditor.jsx - 标签编辑组件
右侧组件：编辑标签，支持推荐标签、批量添加、手动输入等功能
*/

import React, { useState, useEffect } from "react";
import { getRecommendedTags } from "../utils/segment-api";

const TagEditor = ({ 
  selectedSegments = [], 
  segments = [],
  onSaveTags, 
  onBatchSaveTags,
  isLoading = false 
}) => {
  const [newTag, setNewTag] = useState("");
  const [recommendedTags, setRecommendedTags] = useState([]);
  const [customTags, setCustomTags] = useState([]);

  // 获取推荐标签
  useEffect(() => {
    if (selectedSegments.length === 1) {
      // 只为单个段落获取推荐标签
      const segmentId = selectedSegments[0];
      getRecommendedTags(segmentId)
        .then(result => {
          if (result.ok) {
            setRecommendedTags(result.data.recommendedTags || []);
          }
        })
        .catch(error => {
          console.error('获取推荐标签失败:', error);
          // 使用默认推荐标签
          setRecommendedTags([
            "定义", "概念", "原理", "方法", "应用", "实验", "结论", 
            "背景", "设备", "工艺", "安全", "环境", "管理", "设计",
            "化工", "反应器", "传质", "传热", "分离", "控制"
          ]);
        });
    } else {
      // 多选或无选择时，使用通用推荐标签
      setRecommendedTags([
        "定义", "概念", "原理", "方法", "应用", "实验", "结论", 
        "背景", "设备", "工艺", "安全", "环境", "管理", "设计",
        "化工", "反应器", "传质", "传热", "分离", "控制"
      ]);
    }
  }, [selectedSegments]);

  // 获取当前选中段落的信息
  const selectedSegmentData = segments.filter(segment => 
    selectedSegments.includes(segment.id)
  );

  // 获取共同标签（所有选中段落都有的标签）
  const commonTags = selectedSegmentData.length > 0 
    ? selectedSegmentData.reduce((common, segment) => {
        if (common === null) return segment.tags || [];
        return common.filter(tag => (segment.tags || []).includes(tag));
      }, null) || []
    : [];

  // 获取推荐标签（基于选中段落的已有推荐）
  const suggestedTags = selectedSegmentData.length > 0
    ? [...new Set(selectedSegmentData.flatMap(segment => segment.recommendedTags || []))]
    : [];

  // 添加自定义标签
  const handleAddCustomTag = () => {
    const tag = newTag.trim();
    if (tag && !customTags.includes(tag)) {
      setCustomTags(prev => [...prev, tag]);
      setNewTag("");
    }
  };

  // 移除自定义标签
  const handleRemoveCustomTag = (tagToRemove) => {
    setCustomTags(prev => prev.filter(tag => tag !== tagToRemove));
  };

  // 添加推荐标签到自定义标签列表
  const handleAddRecommendedTag = (tag) => {
    if (!customTags.includes(tag)) {
      setCustomTags(prev => [...prev, tag]);
    }
  };

  // 保存单个段落标签
  const handleSaveSingle = (segmentId) => {
    const segment = segments.find(s => s.id === segmentId);
    if (segment) {
      const newTags = [...new Set([...(segment.tags || []), ...customTags])];
      onSaveTags(segmentId, newTags);
    }
  };

  // 批量保存标签
  const handleBatchSave = () => {
    if (selectedSegments.length > 0 && customTags.length > 0) {
      onBatchSaveTags(selectedSegments, customTags);
      setCustomTags([]);
    }
  };

  // 清空操作
  const handleClear = () => {
    setCustomTags([]);
    setNewTag("");
  };

  if (selectedSegments.length === 0) {
    return (
      <div className="border rounded-lg p-6 h-96 flex items-center justify-center">
        <div className="text-center text-gray-500">
          <p className="text-lg mb-2">🏷️</p>
          <p>请选择段落进行标签编辑</p>
        </div>
      </div>
    );
  }

  return (
    <div className="border rounded-lg overflow-hidden">
      {/* 头部 */}
      <div className="bg-gray-50 px-4 py-3 border-b">
        <h3 className="font-semibold">标签编辑</h3>
        <p className="text-sm text-gray-500">
          已选择 {selectedSegments.length} 个段落
        </p>
      </div>

      <div className="p-4 space-y-4 max-h-96 overflow-y-auto">
        {/* 当前段落信息 */}
        {selectedSegments.length === 1 && (
          <div className="bg-blue-50 p-3 rounded-lg">
            <h4 className="text-sm font-medium mb-2">当前段落</h4>
            <p className="text-sm text-gray-700 mb-2">
              {selectedSegmentData[0]?.text ? selectedSegmentData[0].text.substring(0, 100) : '无文本内容'}
              {selectedSegmentData[0]?.text && selectedSegmentData[0].text.length > 100 ? '...' : ''}
            </p>
            {selectedSegmentData[0]?.tags && selectedSegmentData[0].tags.length > 0 && (
              <div className="flex flex-wrap gap-1">
                <span className="text-xs text-gray-600 mr-2">现有标签:</span>
                {selectedSegmentData[0].tags.map((tag, index) => (
                  <span key={index} className="px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded-full">
                    {tag}
                  </span>
                ))}
              </div>
            )}
          </div>
        )}

        {/* 批量选择信息 */}
        {selectedSegments.length > 1 && (
          <div className="bg-green-50 p-3 rounded-lg">
            <h4 className="text-sm font-medium mb-2">批量标注</h4>
            <p className="text-sm text-gray-700 mb-2">
              已选择 {selectedSegments.length} 个段落进行批量标注
            </p>
            {commonTags.length > 0 && (
              <div className="flex flex-wrap gap-1">
                <span className="text-xs text-gray-600 mr-2">共同标签:</span>
                {commonTags.map((tag, index) => (
                  <span key={index} className="px-2 py-1 text-xs bg-green-100 text-green-800 rounded-full">
                    {tag}
                  </span>
                ))}
              </div>
            )}
          </div>
        )}

        {/* 自定义标签输入 */}
        <div>
          <h4 className="text-sm font-medium mb-2">添加标签</h4>
          <div className="flex space-x-2">
            <input
              type="text"
              value={newTag}
              onChange={(e) => setNewTag(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleAddCustomTag()}
              placeholder="输入自定义标签"
              className="flex-1 px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
            <button
              onClick={handleAddCustomTag}
              disabled={!newTag.trim()}
              className="px-3 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:bg-gray-300"
            >
              添加
            </button>
          </div>
        </div>

        {/* 待添加的标签 */}
        {customTags.length > 0 && (
          <div>
            <h4 className="text-sm font-medium mb-2">待添加标签</h4>
            <div className="flex flex-wrap gap-2">
              {customTags.map((tag, index) => (
                <span
                  key={index}
                  className="px-3 py-1 text-sm bg-yellow-100 text-yellow-800 rounded-full flex items-center space-x-1"
                >
                  <span>{tag}</span>
                  <button
                    onClick={() => handleRemoveCustomTag(tag)}
                    className="text-yellow-600 hover:text-yellow-800"
                  >
                    ✕
                  </button>
                </span>
              ))}
            </div>
          </div>
        )}

        {/* 推荐标签 */}
        {suggestedTags.length > 0 && (
          <div>
            <h4 className="text-sm font-medium mb-2">推荐标签</h4>
            <div className="flex flex-wrap gap-2">
              {suggestedTags.map((tag, index) => (
                <button
                  key={index}
                  onClick={() => handleAddRecommendedTag(tag)}
                  className="px-3 py-1 text-sm bg-gray-100 text-gray-700 rounded-full hover:bg-gray-200 transition-colors"
                >
                  + {tag}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* 常用标签 */}
        <div>
          <h4 className="text-sm font-medium mb-2">常用标签</h4>
          <div className="flex flex-wrap gap-2 max-h-32 overflow-y-auto">
            {recommendedTags.map((tag, index) => (
              <button
                key={index}
                onClick={() => handleAddRecommendedTag(tag)}
                className="px-3 py-1 text-sm bg-gray-100 text-gray-700 rounded-full hover:bg-gray-200 transition-colors"
              >
                + {tag}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* 操作按钮 */}
      <div className="bg-gray-50 px-4 py-3 border-t space-y-2">
        {selectedSegments.length === 1 ? (
          <button
            onClick={() => handleSaveSingle(selectedSegments[0])}
            disabled={customTags.length === 0 || isLoading}
            className="w-full px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 disabled:bg-gray-300"
          >
            {isLoading ? '保存中...' : '保存标签'}
          </button>
        ) : (
          <button
            onClick={handleBatchSave}
            disabled={customTags.length === 0 || isLoading}
            className="w-full px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 disabled:bg-gray-300"
          >
            {isLoading ? '保存中...' : `批量保存到 ${selectedSegments.length} 个段落`}
          </button>
        )}
        
        <button
          onClick={handleClear}
          className="w-full px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600"
        >
          清空
        </button>
      </div>
    </div>
  );
};

export default TagEditor;