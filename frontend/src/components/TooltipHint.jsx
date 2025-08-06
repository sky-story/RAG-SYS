/*
TooltipHint.jsx - 提示工具组件
用于在导航栏等位置显示模块说明的悬停提示
*/

import React, { useState } from "react";

const TooltipHint = ({ content, children, position = "right" }) => {
  const [isVisible, setIsVisible] = useState(false);

  const positionClasses = {
    right: "left-full top-1/2 transform -translate-y-1/2 ml-2",
    left: "right-full top-1/2 transform -translate-y-1/2 mr-2",
    top: "bottom-full left-1/2 transform -translate-x-1/2 mb-2",
    bottom: "top-full left-1/2 transform -translate-x-1/2 mt-2"
  };

  const arrowClasses = {
    right: "absolute right-full top-1/2 transform -translate-y-1/2 border-4 border-transparent border-r-gray-800",
    left: "absolute left-full top-1/2 transform -translate-y-1/2 border-4 border-transparent border-l-gray-800",
    top: "absolute top-full left-1/2 transform -translate-x-1/2 border-4 border-transparent border-t-gray-800",
    bottom: "absolute bottom-full left-1/2 transform -translate-x-1/2 border-4 border-transparent border-b-gray-800"
  };

  return (
    <div 
      className="relative inline-block"
      onMouseEnter={() => setIsVisible(true)}
      onMouseLeave={() => setIsVisible(false)}
    >
      {children}
      
      {isVisible && (
        <div className={`absolute z-50 ${positionClasses[position]}`}>
          <div className="bg-gray-800 text-white text-sm px-3 py-2 rounded whitespace-nowrap shadow-lg">
            {content}
            <div className={arrowClasses[position]}></div>
          </div>
        </div>
      )}
    </div>
  );
};

export default TooltipHint;