/*
Segment.jsx - 页面组件：用于展示文档段落划分结果，支持标签打标、搜索、批量编辑等功能
*/

import React, { useState, useEffect } from "react";
import DocumentViewer from "../components/DocumentViewer";
import SegmentList from "../components/SegmentList";
import TagEditor from "../components/TagEditor";
import ProgressBar from "../components/ProgressBar";
import { 
  getDocumentSegments, 
  saveSegmentTags, 
  batchSaveSegmentTags 
} from "../utils/segment-api";

const Segment = ({ parseHistory = [] }) => {
  const [selectedDocument, setSelectedDocument] = useState(null);
  const [documentData, setDocumentData] = useState(null);
  const [segments, setSegments] = useState([]);
  const [selectedSegments, setSelectedSegments] = useState([]);
  const [currentPage, setCurrentPage] = useState(1);
  const [searchTerm, setSearchTerm] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [currentEditingSegment, setCurrentEditingSegment] = useState(null);
  const [loadingProgress, setLoadingProgress] = useState(0);

  // 模拟加载已解析的文档
  useEffect(() => {
    if (parseHistory.length > 0) {
      // 自动选择第一个已解析的文档
      handleSelectDocument(parseHistory[0]);
    }
  }, [parseHistory]);

  // 选择文档
  const handleSelectDocument = async (doc) => {
    setSelectedDocument(doc);
    setIsLoading(true);
    setLoadingProgress(0);

    try {
      // 模拟加载进度
      const progressInterval = setInterval(() => {
        setLoadingProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return 90;
          }
          return prev + 20;
        });
      }, 200);

      const result = await getDocumentSegments(doc.id);
      
      clearInterval(progressInterval);
      setLoadingProgress(100);

      if (result.ok) {
        setDocumentData(result.data);
        setSegments(result.data.segments);
        setCurrentPage(1);
        setSelectedSegments([]);
        setSearchTerm("");
      }
    } catch (error) {
      alert(`加载文档失败: ${error.message}`);
    } finally {
      setIsLoading(false);
      setTimeout(() => setLoadingProgress(0), 1000);
    }
  };

  // 页面切换
  const handlePageChange = (pageNum) => {
    setCurrentPage(pageNum);
    // 清空搜索以显示该页面的所有段落
    setSearchTerm("");
  };

  // 段落选择
  const handleSegmentSelect = (segment) => {
    setCurrentEditingSegment(segment.id);
    if (!selectedSegments.includes(segment.id)) {
      setSelectedSegments([segment.id]);
    }
  };

  // 段落多选切换
  const handleSegmentToggle = (segmentId) => {
    setSelectedSegments(prev => 
      prev.includes(segmentId)
        ? prev.filter(id => id !== segmentId)
        : [...prev, segmentId]
    );
  };

  // 保存单个段落标签
  const handleSaveTags = async (segmentId, tags) => {
    setIsSaving(true);
    try {
      await saveSegmentTags(segmentId, tags);
      
      // 更新本地状态
      setSegments(prev => prev.map(segment => 
        segment.id === segmentId 
          ? { ...segment, tags }
          : segment
      ));
      
      setCurrentEditingSegment(null);
      alert('标签保存成功！');
    } catch (error) {
      alert(`保存失败: ${error.message}`);
    } finally {
      setIsSaving(false);
    }
  };

  // 批量保存标签
  const handleBatchSaveTags = async (segmentIds, tags) => {
    setIsSaving(true);
    try {
      await batchSaveSegmentTags(segmentIds, tags);
      
      // 更新本地状态
      setSegments(prev => prev.map(segment => 
        segmentIds.includes(segment.id)
          ? { ...segment, tags: [...new Set([...(segment.tags || []), ...tags])] }
          : segment
      ));
      
      setSelectedSegments([]);
      alert(`成功为 ${segmentIds.length} 个段落添加标签！`);
    } catch (error) {
      alert(`批量保存失败: ${error.message}`);
    } finally {
      setIsSaving(false);
    }
  };

  // 获取当前页面的段落用于高亮
  const currentPageSegments = segments
    .filter(segment => segment.pageNumber === currentPage)
    .map(segment => segment.id);

  return (
    <div className="max-w-7xl mx-auto p-6 space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">文档分段与标注</h1>
        
        {/* 文档选择器 */}
        <div className="flex items-center space-x-3">
          <span className="text-sm text-gray-600">选择文档:</span>
          <select
            value={selectedDocument?.id || ""}
            onChange={(e) => {
              const doc = parseHistory.find(d => d.id === parseInt(e.target.value));
              if (doc) handleSelectDocument(doc);
            }}
            className="px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="">请选择已解析的文档</option>
            {parseHistory.map(doc => (
              <option key={doc.id} value={doc.id}>
                {doc.fileName}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* 加载进度 */}
      {isLoading && (
        <div className="bg-blue-50 p-4 rounded-lg">
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm text-blue-700">正在加载文档分段数据...</span>
            <span className="text-sm text-blue-600">{loadingProgress}%</span>
          </div>
          <ProgressBar progress={loadingProgress} />
        </div>
      )}

      {/* 主要内容区域 - 三栏布局 */}
      {documentData && (
        <div className="grid grid-cols-12 gap-6">
          {/* 左侧：文档查看器 */}
          <div className="col-span-3">
            <DocumentViewer
              document={documentData}
              currentPage={currentPage}
              onPageChange={handlePageChange}
              highlightedSegments={currentPageSegments}
            />
          </div>

          {/* 中间：段落列表 */}
          <div className="col-span-5">
            <SegmentList
              segments={segments}
              selectedSegments={selectedSegments}
              onSegmentSelect={handleSegmentSelect}
              onSegmentToggle={handleSegmentToggle}
              searchTerm={searchTerm}
              onSearchChange={setSearchTerm}
              highlightedPage={searchTerm ? null : currentPage}
              currentEditingSegment={currentEditingSegment}
            />
          </div>

          {/* 右侧：标签编辑器 */}
          <div className="col-span-4">
            <TagEditor
              selectedSegments={selectedSegments}
              segments={segments}
              onSaveTags={handleSaveTags}
              onBatchSaveTags={handleBatchSaveTags}
              isLoading={isSaving}
            />
          </div>
        </div>
      )}

      {/* 空状态 */}
      {!documentData && !isLoading && (
        <div className="text-center py-12">
          <div className="text-gray-500">
            <p className="text-lg mb-2">📄</p>
            <p className="text-lg mb-2">暂无可分段的文档</p>
            <p className="text-sm">请先在"文档解析"页面解析文档，然后返回此页面进行分段标注</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default Segment;
