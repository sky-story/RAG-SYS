/*
ChartQAHeat.jsx - 折线图组件：展示近一周每日知识问答频率趋势，用于分析用户问答活跃度
*/

import React from "react";

const ChartQAHeat = ({ data = [], total = 0 }) => {
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
  const maxQuestions = Math.max(...data.map(d => d.questions));
  const minQuestions = Math.min(...data.map(d => d.questions));
  const range = maxQuestions - minQuestions || 1;

  // 生成坐标点
  const points = data.map((item, index) => {
    const x = padding + (index / (data.length - 1)) * innerWidth;
    const y = padding + innerHeight - ((item.questions - minQuestions) / range) * innerHeight;
    return { x, y, ...item };
  });

  // 生成平滑曲线路径
  const generateSmoothPath = (points) => {
    if (points.length < 2) return '';
    
    let path = `M ${points[0].x} ${points[0].y}`;
    
    for (let i = 1; i < points.length; i++) {
      const prev = points[i - 1];
      const curr = points[i];
      const cpx1 = prev.x + (curr.x - prev.x) * 0.3;
      const cpy1 = prev.y;
      const cpx2 = curr.x - (curr.x - prev.x) * 0.3;
      const cpy2 = curr.y;
      
      path += ` C ${cpx1} ${cpy1}, ${cpx2} ${cpy2}, ${curr.x} ${curr.y}`;
    }
    
    return path;
  };

  const pathData = generateSmoothPath(points);

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
        strokeDasharray="2,2"
      />
    );
  }

  // 计算平均值
  const average = Math.round(total / 7);
  const averageY = padding + innerHeight - ((average - minQuestions) / range) * innerHeight;

  return (
    <div className="space-y-4">
      {/* 统计信息 */}
      <div className="flex justify-between text-sm">
        <span className="text-gray-600">
          近7天总问答: <span className="font-semibold text-green-600">{total}</span> 次
        </span>
        <span className="text-gray-600">
          日均: <span className="font-semibold">{average}</span> 次
        </span>
      </div>

      {/* 图表 */}
      <div className="relative">
        <svg width={chartWidth} height={chartHeight} className="w-full h-auto">
          {/* 网格线 */}
          <g>{gridLines}</g>
          
          {/* 平均线 */}
          <line
            x1={padding}
            y1={averageY}
            x2={chartWidth - padding}
            y2={averageY}
            stroke="#f59e0b"
            strokeWidth="1"
            strokeDasharray="5,5"
            opacity="0.7"
          />
          <text
            x={chartWidth - padding - 5}
            y={averageY - 5}
            textAnchor="end"
            fontSize="10"
            fill="#f59e0b"
          >
            平均
          </text>
          
          {/* Y轴标签 */}
          {[0, 1, 2, 3, 4].map(i => {
            const value = Math.round(minQuestions + (range * i / 4));
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
          
          {/* 面积填充 */}
          <path
            d={`${pathData} L ${points[points.length - 1].x} ${chartHeight - padding} L ${points[0].x} ${chartHeight - padding} Z`}
            fill="url(#qaGradient)"
            opacity="0.4"
          />
          
          {/* 主折线 */}
          <path
            d={pathData}
            stroke="#10b981"
            strokeWidth="3"
            fill="none"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
          
          {/* 渐变定义 */}
          <defs>
            <linearGradient id="qaGradient" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor="#10b981" stopOpacity="0.8"/>
              <stop offset="100%" stopColor="#10b981" stopOpacity="0.1"/>
            </linearGradient>
          </defs>
          
          {/* 数据点 */}
          {points.map((point, index) => (
            <g key={`point-${index}`}>
              <circle
                cx={point.x}
                cy={point.y}
                r="5"
                fill="#10b981"
                stroke="white"
                strokeWidth="2"
                className="hover:r-7 transition-all duration-200"
              />
              {/* 热力效果 */}
              <circle
                cx={point.x}
                cy={point.y}
                r={Math.max(8, point.questions / maxQuestions * 15)}
                fill="#10b981"
                opacity="0.2"
                className="animate-pulse"
              />
              <circle
                cx={point.x}
                cy={point.y}
                r="15"
                fill="transparent"
                className="hover:fill-green-100 transition-all duration-200"
              >
                <title>{`${point.weekday}: ${point.questions}次问答`}</title>
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

      {/* 活跃度指标 */}
      <div className="flex justify-center space-x-6 text-sm">
        <div className="flex items-center space-x-1">
          <div className="w-3 h-3 bg-green-500 rounded-full"></div>
          <span className="text-gray-600">问答热度</span>
        </div>
        <div className="flex items-center space-x-1">
          <div className="w-3 h-1 bg-yellow-500"></div>
          <span className="text-gray-600">平均线</span>
        </div>
        <div className="text-gray-500">
          峰值: {maxQuestions} 次/天
        </div>
      </div>
    </div>
  );
};

export default ChartQAHeat;