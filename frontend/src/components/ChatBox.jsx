/*
ChatBox.jsx - 对话框组件：右侧展示用户提问与模型回答的对话界面，支持发送新问题
*/

import React, { useState, useRef, useEffect } from "react";
import TagSelector from "./TagSelector";

const ChatBox = ({ 
  currentRecord = null, 
  onSendQuestion, 
  isLoading = false 
}) => {
  const [message, setMessage] = useState("");
  const [selectedTags, setSelectedTags] = useState([]);
  const [showTagSelector, setShowTagSelector] = useState(false);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // 自动滚动到底部
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [currentRecord, isLoading]);

  // 自动聚焦输入框
  useEffect(() => {
    if (!isLoading) {
      inputRef.current?.focus();
    }
  }, [isLoading]);

  const handleSend = () => {
    const question = message.trim();
    if (!question || isLoading) return;

    onSendQuestion(question, selectedTags);
    setMessage("");
    setSelectedTags([]);
    setShowTagSelector(false);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="border rounded-lg overflow-hidden bg-white flex flex-col h-[600px]">
      {/* 头部 */}
      <div className="bg-gray-50 px-4 py-3 border-b">
        <h3 className="font-semibold">知识问答</h3>
        <p className="text-sm text-gray-500">
          {currentRecord ? '查看历史对话' : '输入问题获取化工专业知识'}
        </p>
      </div>

      {/* 对话区域 */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {!currentRecord && !isLoading ? (
          // 欢迎界面
          <div className="text-center text-gray-500 py-8">
            <div className="text-4xl mb-4">🤖</div>
            <p className="text-lg mb-2">化工知识助手</p>
            <p className="text-sm mb-4">
              基于 RAG 技术的智能问答系统
              <br />
              可以根据上传的文档内容提供专业解答
            </p>
            
            {/* RAG 功能介绍 */}
            <div className="bg-blue-50 p-4 rounded-lg text-left max-w-md mx-auto">
              <div className="text-sm text-blue-800 font-medium mb-2">💡 智能特性</div>
              <div className="space-y-1 text-xs text-blue-700">
                <div>📚 基于文档内容的精准回答</div>
                <div>🔍 智能检索相关段落</div>
                <div>🤖 OpenAI GPT-3.5 驱动</div>
                <div>📊 回答质量评估</div>
              </div>
            </div>
          </div>
        ) : (
          // 对话内容
          <>
            {currentRecord && (
              <>
                {/* 用户问题 */}
                <div className="flex justify-end">
                  <div className="max-w-xs lg:max-w-md">
                    <div className="bg-blue-600 text-white rounded-lg px-4 py-2">
                      <p className="text-sm">{currentRecord.question}</p>
                    </div>
                    <div className="flex justify-end mt-1">
                      <span className="text-xs text-gray-500">
                        {new Date(currentRecord.timestamp).toLocaleString()}
                      </span>
                    </div>
                    {currentRecord.tags && currentRecord.tags.length > 0 && (
                      <div className="flex justify-end mt-1">
                        <div className="flex flex-wrap gap-1">
                          {currentRecord.tags.map((tag, index) => (
                            <span
                              key={index}
                              className="px-2 py-0.5 text-xs bg-blue-100 text-blue-800 rounded-full"
                            >
                              {tag}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>

                {/* 系统回答 */}
                <div className="flex justify-start">
                  <div className="max-w-xs lg:max-w-md">
                    <div className="bg-gray-100 rounded-lg px-4 py-2">
                      <pre className="text-sm text-gray-800 whitespace-pre-wrap font-sans">
                        {currentRecord.answer}
                      </pre>
                      
                      {/* RAG 信息展示 */}
                      {currentRecord.retrievalResults && (
                        <div className="mt-3 p-2 bg-blue-50 rounded border text-xs">
                          <div className="flex items-center gap-2 mb-1">
                            <span className="font-medium text-blue-700">📚 检索信息</span>
                            {currentRecord.responseType === 'rag_based' && (
                              <span className="px-1 py-0.5 bg-blue-200 text-blue-800 rounded text-xs">RAG</span>
                            )}
                          </div>
                          <div className="text-gray-600">
                            找到 {currentRecord.retrievalResults.usedSegments} 个相关段落
                            {currentRecord.retrievalResults.searchTime && (
                              <span> · 搜索用时 {currentRecord.retrievalResults.searchTime}s</span>
                            )}
                          </div>
                          
                          {/* 引用段落 */}
                          {currentRecord.retrievalResults.citedSegments && currentRecord.retrievalResults.citedSegments.length > 0 && (
                            <div className="mt-2">
                              <span className="font-medium text-gray-700">📖 参考段落:</span>
                              <div className="mt-1 space-y-1">
                                {currentRecord.retrievalResults.citedSegments.slice(0, 2).map((segment, index) => (
                                  <div key={index} className="pl-2 border-l-2 border-blue-200">
                                    <div className="text-gray-600">
                                      {segment.text && segment.text.length > 80 
                                        ? `${segment.text.substring(0, 80)}...` 
                                        : segment.text || '无内容预览'
                                      }
                                    </div>
                                    {segment.similarity && (
                                      <div className="text-gray-500 text-xs">
                                        相似度: {(segment.similarity * 100).toFixed(1)}%
                                      </div>
                                    )}
                                  </div>
                                ))}
                              </div>
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                    <div className="flex justify-between mt-1">
                      <div className="flex items-center gap-2">
                        <span className="text-xs text-gray-500">AI助手</span>
                        {currentRecord.generationResults?.model && (
                          <span className="text-xs text-gray-500">
                            · {currentRecord.generationResults.model}
                          </span>
                        )}
                        {currentRecord.totalTime && (
                          <span className="text-xs text-gray-500">
                            · {currentRecord.totalTime}s
                          </span>
                        )}
                      </div>
                      {currentRecord.confidence && (
                        <span className="text-xs text-gray-500">
                          置信度: {currentRecord.confidence}%
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              </>
            )}

            {/* 加载状态 */}
            {isLoading && (
              <>
                {/* 用户刚发送的问题 */}
                <div className="flex justify-end">
                  <div className="max-w-xs lg:max-w-md">
                    <div className="bg-blue-600 text-white rounded-lg px-4 py-2">
                      <p className="text-sm">{message}</p>
                    </div>
                    <div className="flex justify-end mt-1">
                      <span className="text-xs text-gray-500">刚刚</span>
                    </div>
                  </div>
                </div>

                {/* AI思考中 */}
                <div className="flex justify-start">
                  <div className="max-w-xs lg:max-w-md">
                    <div className="bg-gray-100 rounded-lg px-4 py-2">
                      <div className="flex items-center space-x-2">
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-gray-600"></div>
                        <span className="text-sm text-gray-600">AI正在思考...</span>
                      </div>
                    </div>
                  </div>
                </div>
              </>
            )}
          </>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* 输入区域 */}
      <div className="border-t bg-gray-50 p-4">
        {/* 标签选择器 */}
        {showTagSelector && (
          <div className="mb-3 border rounded bg-white">
            <TagSelector
              selectedTags={selectedTags}
              onTagsChange={setSelectedTags}
              mode="select"
            />
          </div>
        )}

        {/* 输入框 */}
        <div className="flex space-x-2">
          <div className="flex-1">
            <textarea
              ref={inputRef}
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="输入您的化工专业问题..."
              disabled={isLoading}
              className="w-full px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
              rows="2"
            />
            <div className="flex justify-between items-center mt-1">
              <button
                onClick={() => setShowTagSelector(!showTagSelector)}
                className="text-xs text-gray-500 hover:text-gray-700"
              >
                {showTagSelector ? '收起标签' : '添加标签'}
              </button>
              <span className="text-xs text-gray-400">
                按 Enter 发送，Shift + Enter 换行
              </span>
            </div>
          </div>
          
          <button
            onClick={handleSend}
            disabled={!message.trim() || isLoading}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:bg-gray-400 self-start"
          >
            {isLoading ? '发送中' : '发送'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default ChatBox;
