/*
ChartDocTypePie.jsx - 饼图组件：展示当前知识库中PDF/DOCX/TXT各类文档占比分布
*/

import React from "react";

const ChartDocTypePie = ({ data = [], total = 0 }) => {
  if (!data.length) {
    return (
      <div className="flex items-center justify-center h-48 text-gray-500">
        <p>暂无数据</p>
      </div>
    );
  }

  // 饼图参数
  const radius = 80;
  const centerX = 120;
  const centerY = 100;
  const strokeWidth = 2;

  // 计算角度
  let currentAngle = -90; // 从顶部开始
  const slices = data.map(item => {
    const angle = (item.count / total) * 360;
    const startAngle = currentAngle;
    const endAngle = currentAngle + angle;
    currentAngle = endAngle;

    // 计算SVG弧形路径
    const startAngleRad = (startAngle * Math.PI) / 180;
    const endAngleRad = (endAngle * Math.PI) / 180;
    
    const x1 = centerX + radius * Math.cos(startAngleRad);
    const y1 = centerY + radius * Math.sin(startAngleRad);
    const x2 = centerX + radius * Math.cos(endAngleRad);
    const y2 = centerY + radius * Math.sin(endAngleRad);
    
    const largeArcFlag = angle > 180 ? 1 : 0;
    
    const pathData = [
      `M ${centerX} ${centerY}`,
      `L ${x1} ${y1}`,
      `A ${radius} ${radius} 0 ${largeArcFlag} 1 ${x2} ${y2}`,
      'Z'
    ].join(' ');

    // 计算标签位置
    const labelAngle = (startAngle + endAngle) / 2;
    const labelAngleRad = (labelAngle * Math.PI) / 180;
    const labelRadius = radius + 25;
    const labelX = centerX + labelRadius * Math.cos(labelAngleRad);
    const labelY = centerY + labelRadius * Math.sin(labelAngleRad);

    return {
      ...item,
      pathData,
      labelX,
      labelY,
      angle: labelAngle
    };
  });

  return (
    <div className="space-y-4">
      {/* 总计信息 */}
      <div className="text-center text-sm text-gray-600">
        文档总数: <span className="font-semibold text-blue-600">{total}</span> 个
      </div>

      {/* 饼图 */}
      <div className="flex items-center justify-center">
        <div className="relative">
          <svg width={centerX * 2 + 50} height={centerY * 2 + 50} className="overflow-visible">
            {/* 饼图切片 */}
            {slices.map((slice, index) => (
              <g key={slice.type}>
                <path
                  d={slice.pathData}
                  fill={slice.color}
                  stroke="white"
                  strokeWidth={strokeWidth}
                  className="hover:opacity-80 transition-opacity duration-200 cursor-pointer"
                >
                  <title>{`${slice.type}: ${slice.count}个 (${slice.percentage}%)`}</title>
                </path>
                
                {/* 标签线 */}
                <line
                  x1={centerX + (radius + 5) * Math.cos((slice.angle * Math.PI) / 180)}
                  y1={centerY + (radius + 5) * Math.sin((slice.angle * Math.PI) / 180)}
                  x2={slice.labelX - 15}
                  y2={slice.labelY}
                  stroke={slice.color}
                  strokeWidth="1"
                  opacity="0.6"
                />
                
                {/* 标签文字 */}
                <text
                  x={slice.labelX}
                  y={slice.labelY - 5}
                  textAnchor={slice.labelX > centerX ? "start" : "end"}
                  fontSize="12"
                  fill={slice.color}
                  fontWeight="600"
                >
                  {slice.type}
                </text>
                <text
                  x={slice.labelX}
                  y={slice.labelY + 8}
                  textAnchor={slice.labelX > centerX ? "start" : "end"}
                  fontSize="10"
                  fill="#6b7280"
                >
                  {slice.count}个 ({slice.percentage}%)
                </text>
              </g>
            ))}
            
            {/* 中心圆 */}
            <circle
              cx={centerX}
              cy={centerY}
              r="35"
              fill="white"
              stroke="#e5e7eb"
              strokeWidth="2"
            />
            
            {/* 中心文字 */}
            <text
              x={centerX}
              y={centerY - 5}
              textAnchor="middle"
              fontSize="14"
              fill="#374151"
              fontWeight="600"
            >
              文档分布
            </text>
            <text
              x={centerX}
              y={centerY + 10}
              textAnchor="middle"
              fontSize="10"
              fill="#6b7280"
            >
              按类型统计
            </text>
          </svg>
        </div>
      </div>

      {/* 图例 */}
      <div className="flex justify-center space-x-6">
        {data.map((item, index) => (
          <div key={item.type} className="flex items-center space-x-2">
            <div 
              className="w-4 h-4 rounded"
              style={{ backgroundColor: item.color }}
            ></div>
            <div className="text-sm">
              <span className="font-medium">{item.type}</span>
              <span className="text-gray-500 ml-1">
                ({item.percentage}%)
              </span>
            </div>
          </div>
        ))}
      </div>

      {/* 详细统计 */}
      <div className="bg-gray-50 p-3 rounded text-sm">
        <div className="grid grid-cols-3 gap-4 text-center">
          {data.map((item) => (
            <div key={item.type}>
              <div className="font-semibold" style={{ color: item.color }}>
                {item.count}
              </div>
              <div className="text-gray-600 text-xs">{item.type} 文档</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default ChartDocTypePie;