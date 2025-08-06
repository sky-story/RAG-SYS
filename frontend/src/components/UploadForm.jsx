/*
UploadForm.jsx - 上传组件：负责渲染文件选择按钮与拖拽区域，并处理文件上传交互
*/

import React, { useState } from "react";
import ProgressBar from "./ProgressBar";
import { uploadFiles } from "../utils/api";

const MAX_SIZE = 100 * 1024 * 1024; // 100MB

const UploadForm = ({ onUploadSuccess }) => {
  const [uploadTasks, setUploadTasks] = useState([]);

  // 处理文件数组
  const handleFiles = (fileList) => {
    const newTasks = Array.from(fileList)
      .map((file) => {
        if (file.size > MAX_SIZE) {
          alert(`${file.name} 超过 100MB，已跳过`);
          return null;
        }
        const id = Date.now() + Math.random();
        return { id, file, progress: 0, status: "uploading" };
      })
      .filter(Boolean);

    // 更新任务列表
    setUploadTasks((prev) => [...prev, ...newTasks]);

    // 对每个任务执行模拟上传
    newTasks.forEach((task) => simulateUpload(task));
  };

  // 模拟上传逻辑
  const simulateUpload = (task) => {
    const interval = setInterval(() => {
      setUploadTasks((prev) =>
        prev.map((t) =>
          t.id === task.id
            ? { ...t, progress: Math.min(t.progress + 10, 100) }
            : t
        )
      );
    }, 200);

    const formData = new FormData();
    formData.append("file", task.file);

    // 调用 API（Mock）
    uploadFiles(formData)
      .then(() => {
        clearInterval(interval);
        setUploadTasks((prev) =>
          prev.map((t) =>
            t.id === task.id ? { ...t, progress: 100, status: "done" } : t
          )
        );

        // 通知父组件上传成功，并保存文件对象用于下载
        onUploadSuccess({
          id: task.id,
          name: task.file.name,
          size: task.file.size,
          createdAt: new Date().toISOString(),
          fileObject: task.file, // 保存原始文件对象
        });
      })
      .catch(() => {
        clearInterval(interval);
        setUploadTasks((prev) =>
          prev.map((t) => (t.id === task.id ? { ...t, status: "error" } : t))
        );
        alert(`${task.file.name} 上传失败`);
      });
  };

  // input change
  const onInputChange = (e) => handleFiles(e.target.files);

  // 拖拽
  const onDrop = (e) => {
    e.preventDefault();
    handleFiles(e.dataTransfer.files);
  };

  return (
    <div
      className="border-2 border-dashed border-gray-300 p-6 rounded"
      onDragOver={(e) => e.preventDefault()}
      onDrop={onDrop}
    >
      <div className="flex flex-col items-center space-y-2">
        <input
          id="file-upload"
          type="file"
          multiple
          className="hidden"
          onChange={onInputChange}
          accept=".doc,.docx,.pdf,.txt"
        />
        <label
          htmlFor="file-upload"
          className="cursor-pointer px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          选择文件
        </label>
        <p className="text-sm text-gray-500">或拖拽文件到此区域</p>
      </div>

      {/* 进度列表 */}
      {uploadTasks.length > 0 && (
        <div className="mt-4 space-y-2">
          {uploadTasks.map((task) => (
            <div key={task.id}>
              <span className="text-sm mr-2">{task.file.name}</span>
              <ProgressBar progress={task.progress} />
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default UploadForm;
