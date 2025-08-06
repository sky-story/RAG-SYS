/*
Navbar.jsx - 页面导航栏组件
左侧导航栏，可跳转至上传/解析/问答等页面。
*/

import React from "react";
import TooltipHint from "./TooltipHint";

const Navbar = ({ currentPage, onNavigate }) => {
  const navItems = [
    { 
      key: 'home', 
      label: '首页', 
      icon: '🏠',
      tooltip: '首页：查看系统概览和数据统计图表'
    },
    { 
      key: 'upload', 
      label: '文档上传', 
      icon: '📁',
      tooltip: '文档上传：支持本地文件导入到知识库'
    },
    { 
      key: 'parse', 
      label: '文档解析', 
      icon: '📄',
      tooltip: '文档解析：将上传文档解析为可检索的文本'
    },
    { 
      key: 'segment', 
      label: '文档分段', 
      icon: '✂️',
      tooltip: '文档分段：对解析文档进行分段和标签标注'
    },
    { 
      key: 'qa', 
      label: '知识问答', 
      icon: '💬',
      tooltip: '知识问答：基于知识库进行智能问答'
    },
  ];

  return (
    <nav className="w-64 bg-gray-800 text-white h-screen p-4">
      <div className="mb-8">
        <h2 className="text-xl font-bold text-center">化工知识库</h2>
      </div>
      
      <ul className="space-y-2">
        {navItems.map((item) => (
          <li key={item.key}>
            <TooltipHint content={item.tooltip} position="right">
              <button
                onClick={() => onNavigate(item.key)}
                className={`w-full flex items-center space-x-3 p-3 rounded-lg transition-colors ${
                  currentPage === item.key
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-300 hover:bg-gray-700 hover:text-white'
                }`}
              >
                <span className="text-lg">{item.icon}</span>
                <span>{item.label}</span>
              </button>
            </TooltipHint>
          </li>
        ))}
      </ul>
    </nav>
  );
};

export default Navbar;
