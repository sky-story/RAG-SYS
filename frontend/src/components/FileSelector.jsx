/*
FileSelector.jsx - 文件选择组件
支持上传本地文件或从已有文档中选择进行解析。
*/

import React, { useState, useEffect } from "react";
import { getUploadRecords } from "../utils/api";

const FileSelector = ({ onFileSelect, selectedFile, uploadRecords = [] }) => {
  const [mode, setMode] = useState('local'); // 'local' or 'database'

  // 使用传入的 uploadRecords 而不是本地状态

  const handleLocalFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      onFileSelect({
        type: 'local',
        file: file,
        name: file.name,
      });
    }
  };

  const handleDatabaseFileSelect = (record) => {
    onFileSelect({
      type: 'database',
      id: record.id,
      name: record.name,
    });
  };

  return (
    <div className="border rounded-lg p-4 space-y-4">
      <h3 className="text-lg font-semibold">选择解析文件</h3>
      
      {/* 模式切换 */}
      <div className="flex space-x-2">
        <button
          onClick={() => setMode('local')}
          className={`px-4 py-2 rounded ${
            mode === 'local' 
              ? 'bg-blue-600 text-white' 
              : 'bg-gray-200 text-gray-700'
          }`}
        >
          本地上传
        </button>
        <button
          onClick={() => setMode('database')}
          className={`px-4 py-2 rounded ${
            mode === 'database' 
              ? 'bg-blue-600 text-white' 
              : 'bg-gray-200 text-gray-700'
          }`}
        >
          已有文档
        </button>
      </div>

      {/* 本地文件上传 */}
      {mode === 'local' && (
        <div className="border-2 border-dashed border-gray-300 p-6 rounded text-center">
          <input
            id="parse-file-upload"
            type="file"
            className="hidden"
            onChange={handleLocalFileChange}
            accept=".doc,.docx,.pdf,.txt"
          />
          <label
            htmlFor="parse-file-upload"
            className="cursor-pointer px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            选择文件
          </label>
          <p className="text-sm text-gray-500 mt-2">
            支持 .doc, .docx, .pdf, .txt 格式
          </p>
          {selectedFile && selectedFile.type === 'local' && (
            <p className="text-sm text-green-600 mt-2">
              已选择: {selectedFile.name}
            </p>
          )}
        </div>
      )}

      {/* 已有文档选择 */}
      {mode === 'database' && (
        <div className="space-y-2 max-h-64 overflow-y-auto">
          {uploadRecords.length === 0 ? (
            <p className="text-gray-500 text-sm">暂无已上传文档</p>
          ) : (
            uploadRecords.map((file) => (
              <div
                key={file.id}
                onClick={() => handleDatabaseFileSelect(file)}
                className={`p-3 border rounded cursor-pointer transition-colors ${
                  selectedFile && selectedFile.type === 'database' && selectedFile.id === file.id
                    ? 'bg-blue-100 border-blue-500'
                    : 'hover:bg-gray-50'
                }`}
              >
                <p className="font-medium">{file.name}</p>
                <p className="text-xs text-gray-500">
                  {new Date(file.createdAt).toLocaleString()}
                </p>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
};

export default FileSelector;