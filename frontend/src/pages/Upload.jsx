/*
Upload.jsx - 页面组件：用于展示“知识库文档上传”页面，包括上传区域、历史记录等布局
*/

import React, { useEffect, useMemo, useState } from "react";
import UploadForm from "../components/UploadForm";
import FileCard from "../components/FileCard";
import { getUploadRecords, deleteFile, downloadFile } from "../utils/api";

const PAGE_SIZE = 5;

const Upload = ({ uploadRecords = [], onAddRecord, onRemoveRecord }) => {
  const [search, setSearch] = useState("");
  const [currentPage, setCurrentPage] = useState(1);

  // 使用传入的 uploadRecords 而不是本地状态

  // 搜索过滤
  const filtered = useMemo(() => {
    return uploadRecords.filter((r) =>
      r.name.toLowerCase().includes(search.toLowerCase())
    );
  }, [uploadRecords, search]);

  // 分页
  const totalPages = Math.ceil(filtered.length / PAGE_SIZE) || 1;
  const paginated = filtered.slice(
    (currentPage - 1) * PAGE_SIZE,
    currentPage * PAGE_SIZE
  );

  // 上传成功回调
  const handleUploadSuccess = (newRecord) => {
    onAddRecord(newRecord);
  };

  // 删除记录
  const handleDelete = (rec) => {
    deleteFile(rec.id).then(() => {
      onRemoveRecord(rec.id);
    });
  };

  // 下载文件
  const handleDownload = async (rec) => {
    try {
      await downloadFile(rec);
    } catch (error) {
      alert(`下载失败：${error.message}`);
    }
  };

  // 导出 JSON
  const exportJSON = () => {
    const blob = new Blob([JSON.stringify(uploadRecords, null, 2)], {
      type: "application/json",
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "upload_records.json";
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="max-w-4xl mx-auto p-4 space-y-6">
      <h1 className="text-2xl font-bold">知识库文档上传</h1>

      {/* 上传区域 */}
      <UploadForm onUploadSuccess={handleUploadSuccess} />

      {/* 搜索与导出 */}
      <div className="flex items-center justify-between">
        <input
          className="border px-3 py-1 rounded w-64"
          placeholder="搜索文件名"
          value={search}
          onChange={(e) => {
            setSearch(e.target.value);
            setCurrentPage(1);
          }}
        />

        <button
          onClick={exportJSON}
          className="px-3 py-1 bg-gray-700 text-white rounded"
        >
          导出 JSON
        </button>
      </div>

      {/* 历史记录列表 */}
      <div className="space-y-2">
        {paginated.map((rec) => (
          <FileCard
            key={rec.id}
            record={rec}
            onDelete={handleDelete}
            onDownload={handleDownload}
          />
        ))}
        {paginated.length === 0 && (
          <p className="text-sm text-gray-500">暂无记录</p>
        )}
      </div>

      {/* 分页 */}
      {totalPages > 1 && (
        <div className="flex justify-center space-x-2">
          <button
            disabled={currentPage === 1}
            onClick={() => setCurrentPage((p) => p - 1)}
            className="px-2 py-1 border rounded disabled:opacity-50"
          >
            上一页
          </button>
          <span className="px-2 py-1">
            {currentPage} / {totalPages}
          </span>
          <button
            disabled={currentPage === totalPages}
            onClick={() => setCurrentPage((p) => p + 1)}
            className="px-2 py-1 border rounded disabled:opacity-50"
          >
            下一页
          </button>
        </div>
      )}
    </div>
  );
};

export default Upload;
