# 化工行业大模型知识库 (Chem Knowledge Base)

> 初始项目框架 — 前后端分离、模块化目录、依赖隔离

本仓库旨在为化工行业提供一个可扩展的“大模型知识库”示例，实现文档上传、解析、切分标注以及基于嵌入向量的问答能力。

---

## 目录结构概览

```text
chem-knowledge-base/
├── frontend/         # React + Tailwind 前端代码
├── backend/          # Flask 后端代码
├── data/             # 本地原始文件备份
├── docs/             # 项目设计与技术文档
└── README.md         # 项目说明
```

各文件夹详细说明见相应子目录下的注释。

---

## 快速开始

### 前端
```bash
# 创建并安装依赖（已生成 package.json，可直接安装）
cd frontend
npm install
npm run dev
```

### 后端
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py  # 默认 localhost:5000
```

> 首次 clone 后，请根据需要修改 `.env` / `config.py` 中的后端或数据库地址。

---

## 后续开发指引
1. **不要在主分支直接开发** ：请通过 feature 分支提交 PR。
2. **保持注释** ：保持与本模板一致的代码注释风格，方便实习生/协作者理解。
3. **遵循 Lint & Commit 规范** ：可后续集成 ESLint / Prettier（前端）与 Flake8 / Black（后端）。
4. **文档先行** ：在 `docs/` 补充接口文档、数据库设计与流程图。

祝编码愉快！