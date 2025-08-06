/*
ChartUploadTrend.jsx - 折线图组件：展示近一周每日文档上传数量趋势，用于评估系统使用活跃度
*/

import React from "react";

const ChartUploadTrend = ({ data = [], total = 0 }) => {
  if (!data.length) {
    return (
      <div className="flex items-center justify-center h-48 text-gray-500">
        <p>暂无数据</p>
      </div>
    );
  }

  // 计算图表尺寸
  const chartWidth = 400;
  const chartHeight = 200;
  const padding = 40;
  const innerWidth = chartWidth - padding * 2;
  const innerHeight = chartHeight - padding * 2;

  // 获取数据范围
  const maxUploads = Math.max(...data.map(d => d.uploads));
  const minUploads = Math.min(...data.map(d => d.uploads));
  const range = maxUploads - minUploads || 1;

  // 生成坐标点
  const points = data.map((item, index) => {
    const x = padding + (index / (data.length - 1)) * innerWidth;
    const y = padding + innerHeight - ((item.uploads - minUploads) / range) * innerHeight;
    return { x, y, ...item };
  });

  // 生成折线路径
  const pathData = points.map((point, index) => 
    `${index === 0 ? 'M' : 'L'} ${point.x} ${point.y}`
  ).join(' ');

  // 生成网格线
  const gridLines = [];
  for (let i = 0; i <= 4; i++) {
    const y = padding + (i / 4) * innerHeight;
    gridLines.push(
      <line 
        key={`grid-${i}`}
        x1={padding} 
        y1={y} 
        x2={chartWidth - padding} 
        y2={y} 
        stroke="#e5e7eb" 
        strokeWidth="1"
      />
    );
  }

  return (
    <div className="space-y-4">
      {/* 统计信息 */}
      <div className="flex justify-between text-sm">
        <span className="text-gray-600">
          近7天总上传: <span className="font-semibold text-blue-600">{total}</span> 个文件
        </span>
        <span className="text-gray-600">
          日均: <span className="font-semibold">{Math.round(total / 7)}</span> 个
        </span>
      </div>

      {/* 图表 */}
      <div className="relative">
        <svg width={chartWidth} height={chartHeight} className="w-full h-auto">
          {/* 网格线 */}
          <g>{gridLines}</g>
          
          {/* Y轴标签 */}
          {[0, 1, 2, 3, 4].map(i => {
            const value = Math.round(minUploads + (range * i / 4));
            const y = padding + innerHeight - (i / 4) * innerHeight;
            return (
              <text 
                key={`y-label-${i}`}
                x={padding - 10} 
                y={y + 4} 
                textAnchor="end" 
                fontSize="12" 
                fill="#6b7280"
              >
                {value}
              </text>
            );
          })}
          
          {/* 折线 */}
          <path
            d={pathData}
            stroke="#3b82f6"
            strokeWidth="3"
            fill="none"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
          
          {/* 面积填充 */}
          <path
            d={`${pathData} L ${points[points.length - 1].x} ${chartHeight - padding} L ${points[0].x} ${chartHeight - padding} Z`}
            fill="url(#uploadGradient)"
            opacity="0.3"
          />
          
          {/* 渐变定义 */}
          <defs>
            <linearGradient id="uploadGradient" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor="#3b82f6" stopOpacity="0.8"/>
              <stop offset="100%" stopColor="#3b82f6" stopOpacity="0.1"/>
            </linearGradient>
          </defs>
          
          {/* 数据点 */}
          {points.map((point, index) => (
            <g key={`point-${index}`}>
              <circle
                cx={point.x}
                cy={point.y}
                r="4"
                fill="#3b82f6"
                stroke="white"
                strokeWidth="2"
                className="hover:r-6 transition-all duration-200"
              />
              <circle
                cx={point.x}
                cy={point.y}
                r="12"
                fill="transparent"
                className="hover:fill-blue-100 transition-all duration-200"
              >
                <title>{`${point.weekday}: ${point.uploads}个文件`}</title>
              </circle>
            </g>
          ))}
          
          {/* X轴标签 */}
          {points.map((point, index) => (
            <text
              key={`x-label-${index}`}
              x={point.x}
              y={chartHeight - padding + 20}
              textAnchor="middle"
              fontSize="12"
              fill="#6b7280"
            >
              {point.weekday}
            </text>
          ))}
        </svg>
      </div>

      {/* 趋势指标 */}
      <div className="flex justify-center space-x-6 text-sm">
        <div className="flex items-center space-x-1">
          <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
          <span className="text-gray-600">上传趋势</span>
        </div>
        <div className="text-gray-500">
          峰值: {maxUploads} 个/天
        </div>
      </div>
    </div>
  );
};

export default ChartUploadTrend;