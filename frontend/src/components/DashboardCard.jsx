/*
DashboardCard.jsx - 仪表盘卡片容器组件
用于包装仪表盘中的各种图表和统计信息，提供统一的卡片样式
*/

import React from "react";

const DashboardCard = ({ 
  title, 
  subtitle, 
  icon, 
  children, 
  isLoading = false,
  className = "" 
}) => {
  return (
    <div className={`bg-white rounded-lg border border-gray-200 shadow-sm hover:shadow-md transition-shadow ${className}`}>
      {/* 卡片头部 */}
      <div className="px-6 py-4 border-b border-gray-100">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            {icon && (
              <div className="text-2xl">{icon}</div>
            )}
            <div>
              <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
              {subtitle && (
                <p className="text-sm text-gray-500">{subtitle}</p>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* 卡片内容 */}
      <div className="p-6">
        {isLoading ? (
          <div className="flex items-center justify-center h-48">
            <div className="text-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-2"></div>
              <p className="text-sm text-gray-500">加载中...</p>
            </div>
          </div>
        ) : (
          children
        )}
      </div>
    </div>
  );
};

export default DashboardCard;