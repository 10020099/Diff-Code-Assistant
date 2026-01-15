# Diff Code Assistant

赛博朋克风格的代码修改助手工具，帮助开发者与大语言模型 (LLM) 协作进行代码重构和修改。

![Electron](https://img.shields.io/badge/Electron-28-47848F?logo=electron)
![React](https://img.shields.io/badge/React-18-61DAFB?logo=react)
![TypeScript](https://img.shields.io/badge/TypeScript-5-3178C6?logo=typescript)
![License](https://img.shields.io/badge/License-MIT-green)

## 功能特性

- **智能文件扫描**: 自动扫描项目目录，排除无关文件，支持文件大小过滤
- **上下文生成**: 自动生成项目结构和文件内容，可选行号显示
- **LLM 提示生成**: 一键生成完整的 LLM 提示，便于与 ChatGPT/Claude 等交互
- **Diff 预览**: 彩色语法高亮显示 diff 内容，支持格式验证
- **直接应用 Diff**: 自动解析并应用 diff 修改到源文件
- **安全保护**: 自动备份、冲突检查、预览模式、回滚功能
- **赛博朋克 UI**: 霓虹色彩、扫描线特效、现代化界面

## 技术栈

| 技术 | 版本 | 说明 |
|------|------|------|
| Electron | 28 | 跨平台桌面应用框架 |
| React | 18 | 组件化 UI 框架 |
| TypeScript | 5 | 类型安全 |
| Tailwind CSS | 3 | 原子化 CSS 框架 |
| Zustand | 4 | 轻量级状态管理 |
| Vite | 5 | 快速构建工具 |

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

## 项目结构

```
Diff-Code-Assistant/
├── src/
│   ├── main/                      # Electron 主进程
│   │   ├── index.ts               # 主进程入口
│   │   ├── ipc/                   # IPC 通信处理
│   │   │   ├── fileHandlers.ts    # 文件操作
│   │   │   ├── diffHandlers.ts    # Diff 处理
│   │   │   └── backupHandlers.ts  # 备份管理
│   │   └── utils/
│   │       ├── fileScanner.ts     # 文件扫描
│   │       └── diffParser.ts      # Diff 解析
│   │
│   ├── preload/                   # 预加载脚本
│   │   └── index.ts
│   │
│   └── renderer/                  # 渲染进程 (React)
│       ├── index.html
│       ├── main.tsx               # React 入口
│       ├── App.tsx                # 主应用组件
│       ├── styles/                # 样式文件
│       ├── components/            # UI 组件
│       ├── pages/                 # 页面组件
│       └── stores/                # 状态管理
│
├── package.json
├── tsconfig.json
├── tailwind.config.js
└── electron.vite.config.ts
```

## 使用方法

1. **项目设置**: 选择项目目录，扫描文件，选择需要包含的文件
2. **上下文生成**: 输入 LLM 指令，生成完整提示并复制到剪贴板
3. **Diff 预览**: 粘贴 LLM 返回的 diff 内容，预览和验证
4. **代码应用**: 直接应用 diff 修改，支持备份和回滚

## 许可证

MIT License - Copyright (c) 2025 ZhengHao
