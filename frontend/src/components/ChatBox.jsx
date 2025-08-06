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
            <p className="text-sm">
              我可以帮您解答化工相关的专业问题
              <br />
              包括工艺流程、设备原理、安全规范等
            </p>
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
                    </div>
                    <div className="flex justify-between mt-1">
                      <span className="text-xs text-gray-500">
                        AI助手
                      </span>
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
