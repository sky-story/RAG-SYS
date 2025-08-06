/*
FileCard.jsx - 组件：展示单条上传文件的卡片，包含文件名、时间、下载与删除操作
*/

import React, { useState } from "react";

const FileCard = ({ record, onDelete, onDownload }) => {
  const [isDownloading, setIsDownloading] = useState(false);

  const handleDownload = async () => {
    setIsDownloading(true);
    try {
      await onDownload(record);
    } finally {
      setIsDownloading(false);
    }
  };

  return (
    <div className="flex items-center justify-between p-3 border rounded-lg hover:bg-gray-50">
      <div className="flex-1">
        <div className="flex items-center space-x-2">
          <p className="font-medium text-gray-900">{record.name}</p>
          {record.fileObject && (
            <span className="px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded">
              原始文件
            </span>
          )}
        </div>
        <p className="text-sm text-gray-500">
          {new Date(record.createdAt).toLocaleString()}
          {record.size && (
            <span className="ml-2">
              · {(record.size / 1024 / 1024).toFixed(2)} MB
            </span>
          )}
        </p>
      </div>
      <div className="flex space-x-2">
        <button
          onClick={handleDownload}
          disabled={isDownloading}
          className="px-3 py-1 text-sm bg-green-500 text-white rounded hover:bg-green-600 disabled:opacity-50"
        >
          {isDownloading ? "下载中..." : "下载"}
        </button>
        <button
          onClick={() => {
            if (window.confirm("确定删除？")) onDelete(record);
          }}
          className="px-3 py-1 text-sm bg-red-500 text-white rounded hover:bg-red-600"
        >
          删除
        </button>
      </div>
    </div>
  );
};

export default FileCard;
