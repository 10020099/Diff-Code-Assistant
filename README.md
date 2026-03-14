# Diff Code Assistant

赛博朋克风格的 AI 代码修改助手，直接集成 LLM API，在应用内完成对话→生成 Diff→应用修改的完整工作流。

![Electron](https://img.shields.io/badge/Electron-28-47848F?logo=electron)
![React](https://img.shields.io/badge/React-18-61DAFB?logo=react)
![TypeScript](https://img.shields.io/badge/TypeScript-5-3178C6?logo=typescript)
![License](https://img.shields.io/badge/License-MIT-green)

## 功能特性

### 🤖 AI 直接集成
- **多提供商支持**: OpenAI (Chat Completions / Responses API)、Claude、Gemini、DeepSeek
- **自定义 Base URL**: 支持中转接口，一个配置适配所有兼容接口
- **流式响应**: 实时显示 AI 输出，支持中途停止
- **多轮对话**: 保持上下文，可持续追加修改指令

### 📝 智能 Diff 管理
- **自动提取**: 从 AI 回复中自动提取 ` ```diff ` 代码块
- **按文件分组预览**: 每个文件独立展示，统计增删行数
- **一键应用**: 验证 + 备份 + 应用一步完成
- **单文件/全部应用**: 可选择性地只应用部分文件的修改

### 🔒 安全保护
- **自动备份**: 每次应用前自动备份原文件
- **智能清理**: 每个文件只保留最近 5 份备份，不会塞满磁盘
- **对话历史**: 自动保存，随时回看过往对话

### 💻 项目扫描
- **智能文件扫描**: 自动排除 `node_modules`、`.git` 等无关目录
- **文件大小过滤**: 跳过过大的文件
- **上下文生成**: 自动构建包含项目结构和代码内容的 Prompt

### 🎨 赛博朋克 UI
- 霓虹色彩 + 扫描线特效
- 三栏布局（对话历史 / 聊天区域 / Diff 预览）
- 深色主题，适合长时间编码

## 技术栈

| 技术 | 版本 | 说明 |
|------|------|------|
| Electron | 28 | 跨平台桌面应用框架 |
| React | 18 | 组件化 UI 框架 |
| TypeScript | 5 | 类型安全 |
| Tailwind CSS | 3 | 原子化 CSS 框架 |
| Zustand | 4 | 轻量级状态管理 |
| electron-vite | 2 | Electron 专用构建工具 |

## 快速开始

### 安装依赖

```bash
npm install
```

### 开发模式

```bash
npm run dev
```

### 构建生产版本

```bash
npm run build
```

### 打包应用

```bash
# Windows
npm run package:win

# macOS
npm run package:mac

# Linux
npm run package:linux
```

## 使用方法

### 1. 项目设置
选择项目目录 → 配置扫描选项 → 扫描文件 → 选择需要包含的文件 → 生成上下文

### 2. AI 修改
输入代码修改指令 → AI 流式返回修改方案（含 diff）→ 右侧面板自动显示按文件分组的  Diff 预览 → 一键应用修改

支持多轮对话：如果对修改结果不满意，直接在对话中追加指令即可。

### 3. 设置
配置 API 提供商（API Key、Base URL、模型名称）→ 编辑系统提示词 → 测试连接

## 项目结构

```
Diff-Code-Assistant/
├── src/
│   ├── main/                          # Electron 主进程
│   │   ├── index.ts                   # 主进程入口
│   │   ├── ipc/                       # IPC 通信处理
│   │   │   ├── fileHandlers.ts        # 文件扫描操作
│   │   │   ├── diffHandlers.ts        # Diff 解析与应用
│   │   │   ├── backupHandlers.ts      # 备份管理
│   │   │   ├── llmHandlers.ts         # LLM API 调用（流式/非流式）
│   │   │   └── configHandlers.ts      # 配置与对话历史持久化
│   │   ├── llm/                       # LLM 提供商适配层
│   │   │   ├── types.ts               # 统一类型定义
│   │   │   ├── providerBase.ts        # 提供商抽象基类
│   │   │   ├── openai.ts             # OpenAI Chat Completions
│   │   │   ├── openaiResponses.ts    # OpenAI Responses API
│   │   │   ├── claude.ts             # Anthropic Claude
│   │   │   ├── gemini.ts             # Google Gemini
│   │   │   ├── deepseek.ts           # DeepSeek (OpenAI 兼容)
│   │   │   └── index.ts              # 工厂方法
│   │   └── utils/
│   │       ├── fileScanner.ts         # 文件扫描与上下文生成
│   │       └── diffParser.ts          # Diff 解析与应用
│   │
│   ├── preload/                       # 预加载脚本
│   │   └── index.ts                   # 暴露 IPC API 到渲染进程
│   │
│   └── renderer/                      # 渲染进程 (React)
│       ├── App.tsx                    # 主应用（3 Tab 布局）
│       ├── pages/
│       │   ├── ProjectSetup.tsx       # 项目设置页
│       │   ├── AIModify.tsx           # AI 修改核心页（对话+Diff预览）
│       │   └── Settings.tsx           # API 配置页
│       ├── components/
│       │   ├── ui/                    # 通用 UI 组件（CyberButton 等）
│       │   ├── features/             # 业务组件
│       │   │   ├── ChatMessage.tsx    # 聊天消息（支持 diff 高亮）
│       │   │   ├── ChatInput.tsx      # 输入框
│       │   │   ├── DiffGroupViewer.tsx # 按文件分组 Diff 预览
│       │   │   ├── ConversationList.tsx # 对话历史列表
│       │   │   └── ...
│       │   └── effects/              # 视觉特效
│       └── stores/
│           ├── projectStore.ts        # 项目状态
│           ├── settingsStore.ts       # API 配置状态
│           ├── chatStore.ts           # 对话与流式状态
│           └── diffStore.ts           # Diff 状态
│
├── package.json
├── tsconfig.json
├── tailwind.config.js
└── electron.vite.config.ts
```

## 支持的 LLM 提供商

| 提供商 | API 类型 | 默认 Base URL |
|--------|----------|---------------|
| OpenAI | Chat Completions | `https://api.openai.com/v1` |
| OpenAI | Responses API | `https://api.openai.com/v1` |
| Claude | Messages API | `https://api.anthropic.com` |
| Gemini | GenerativeLanguage | `https://generativelanguage.googleapis.com` |
| DeepSeek | OpenAI 兼容 | `https://api.deepseek.com` |

> 所有提供商均支持自定义 Base URL，可接入中转服务。

## 备份机制

- 备份存放在项目根目录的 `.diff_backups/` 文件夹中
- 文件命名格式：`{扁平化路径}.{YYYYMMDD-HHMMSS}.bak`
- 每个原始文件自动保留最近 5 份备份，旧的自动清理
- 建议将 `.diff_backups/` 加入 `.gitignore`

## 许可证

MIT License - Copyright (c) 2025 ZhengHao
