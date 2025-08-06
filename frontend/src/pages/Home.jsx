/*
Home.jsx - 系统主页页面：用于展示上传趋势图、问答热度图、文档类型分布图，并通过左侧导航栏跳转至其他模块页面
*/

import React, { useState, useEffect } from "react";
import DashboardCard from "../components/DashboardCard";
import ChartUploadTrend from "../components/ChartUploadTrend";
import ChartQAHeat from "../components/ChartQAHeat";
import ChartDocTypePie from "../components/ChartDocTypePie";
import { 
  fetchUploadStats, 
  fetchQATrends, 
  fetchDocTypes, 
  fetchSystemOverview 
} from "../utils/dashboard-api";

const Home = () => {
  const [uploadData, setUploadData] = useState({ data: [], total: 0 });
  const [qaData, setQaData] = useState({ data: [], total: 0 });
  const [docTypeData, setDocTypeData] = useState({ data: [], total: 0 });
  const [systemOverview, setSystemOverview] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  // 加载仪表盘数据
  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    setIsLoading(true);
    try {
      const [uploadStats, qaTrends, docTypes, overview] = await Promise.all([
        fetchUploadStats(),
        fetchQATrends(),
        fetchDocTypes(),
        fetchSystemOverview()
      ]);

      if (uploadStats.ok) setUploadData(uploadStats);
      if (qaTrends.ok) setQaData(qaTrends);
      if (docTypes.ok) setDocTypeData(docTypes);
      if (overview.ok) setSystemOverview(overview.data);
    } catch (error) {
      console.error('加载仪表盘数据失败:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto p-6 space-y-6">
      {/* 页面标题 */}
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold text-gray-900">化工行业大模型知识库</h1>
        <p className="text-lg text-gray-600 mt-2">
          专业化工知识管理与智能问答系统
        </p>
        {systemOverview && (
          <p className="text-sm text-gray-500 mt-2">
            系统运行时间: {systemOverview.systemUptime} · 
            最后更新: {new Date(systemOverview.lastUpdated).toLocaleString()}
          </p>
        )}
      </div>

      {/* 系统概览卡片 */}
      {systemOverview && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <div className="bg-gradient-to-r from-blue-500 to-blue-600 text-white p-6 rounded-lg">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-blue-100 text-sm">总文档数</p>
                <p className="text-2xl font-bold">{systemOverview.totalDocuments}</p>
              </div>
              <div className="text-3xl opacity-80">📚</div>
            </div>
          </div>
          
          <div className="bg-gradient-to-r from-green-500 to-green-600 text-white p-6 rounded-lg">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-green-100 text-sm">总问答数</p>
                <p className="text-2xl font-bold">{systemOverview.totalQuestions}</p>
              </div>
              <div className="text-3xl opacity-80">💬</div>
            </div>
          </div>
          
          <div className="bg-gradient-to-r from-purple-500 to-purple-600 text-white p-6 rounded-lg">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-purple-100 text-sm">活跃用户</p>
                <p className="text-2xl font-bold">{systemOverview.totalUsers}</p>
              </div>
              <div className="text-3xl opacity-80">👥</div>
            </div>
          </div>
          
          <div className="bg-gradient-to-r from-orange-500 to-orange-600 text-white p-6 rounded-lg">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-orange-100 text-sm">系统稳定性</p>
                <p className="text-2xl font-bold">{systemOverview.systemUptime}</p>
              </div>
              <div className="text-3xl opacity-80">⚡</div>
            </div>
          </div>
        </div>
      )}

      {/* 主要图表区域 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
        {/* 文档上传趋势图 */}
        <DashboardCard
          title="文档上传趋势"
          subtitle="近一周每日上传文件数量"
          icon="📈"
          isLoading={isLoading}
          className="lg:col-span-1"
        >
          <ChartUploadTrend 
            data={uploadData.data} 
            total={uploadData.total} 
          />
        </DashboardCard>

        {/* 知识问答热度图 */}
        <DashboardCard
          title="问答活跃度"
          subtitle="近一周每日问答频率统计"
          icon="🔥"
          isLoading={isLoading}
          className="lg:col-span-1"
        >
          <ChartQAHeat 
            data={qaData.data} 
            total={qaData.total} 
          />
        </DashboardCard>

        {/* 文档类型分布饼图 */}
        <DashboardCard
          title="文档类型分布"
          subtitle="知识库中各类型文档占比"
          icon="📊"
          isLoading={isLoading}
          className="lg:col-span-2 xl:col-span-1"
        >
          <ChartDocTypePie 
            data={docTypeData.data} 
            total={docTypeData.total} 
          />
        </DashboardCard>
      </div>

      {/* 快速操作区域 */}
      <div className="bg-gray-50 rounded-lg p-6">
        <h3 className="text-lg font-semibold mb-4">快速操作</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <button className="flex items-center space-x-3 p-4 bg-white rounded-lg hover:bg-blue-50 transition-colors border">
            <span className="text-2xl">📁</span>
            <div className="text-left">
              <p className="font-medium">上传文档</p>
              <p className="text-sm text-gray-500">导入新的专业文档</p>
            </div>
          </button>
          
          <button className="flex items-center space-x-3 p-4 bg-white rounded-lg hover:bg-green-50 transition-colors border">
            <span className="text-2xl">📄</span>
            <div className="text-left">
              <p className="font-medium">解析文档</p>
              <p className="text-sm text-gray-500">处理文档内容</p>
            </div>
          </button>
          
          <button className="flex items-center space-x-3 p-4 bg-white rounded-lg hover:bg-purple-50 transition-colors border">
            <span className="text-2xl">✂️</span>
            <div className="text-left">
              <p className="font-medium">文档分段</p>
              <p className="text-sm text-gray-500">标注和分类</p>
            </div>
          </button>
          
          <button className="flex items-center space-x-3 p-4 bg-white rounded-lg hover:bg-orange-50 transition-colors border">
            <span className="text-2xl">💬</span>
            <div className="text-left">
              <p className="font-medium">智能问答</p>
              <p className="text-sm text-gray-500">获取专业解答</p>
            </div>
          </button>
        </div>
      </div>

      {/* 系统状态 */}
      <div className="text-center text-sm text-gray-500 bg-blue-50 p-4 rounded-lg">
        <p>
          🔄 数据每5分钟自动刷新 · 
          📊 统计数据基于过去7天 · 
          🛡️ 系统稳定运行中
        </p>
      </div>
    </div>
  );
};

export default Home;
