/*
tailwind.config.js - Tailwind CSS 配置文件
可根据 UI 需求在 theme 中扩展自定义颜色与断点。
*/

/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{js,jsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
};
