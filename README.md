# 🌐 Diff Code Assistant - Cyberpunk Edition

一个功能强大的赛博朋克风格代码修改助手，帮助您与LLM协作进行大规模代码重构。

## ✨ 特性

### 🎨 赛博朋克视觉风格
- 霓虹色彩主题 (青色/紫色/品红)
- 扫描线特效
- 发光效果
- 未来科技感UI

### 💪 强大功能
- **智能文件扫描** - 自动排除无关文件，支持文件大小过滤
- **高级文件树** - 搜索/过滤/反选，显示文件类型和大小
- **上下文生成** - 自动生成项目结构和文件内容，支持行号
- **LLM集成** - 一键生成完整的LLM提示
- **Diff预览** - 彩色语法高亮，高级格式验证
- **双模式应用**:
  - 方式1 (推荐): 直接应用Diff - 自动解析并应用修改，支持备份和回滚
  - 方式2 (传统): 手动应用 - 生成提示给LLM，获取完整代码后手动替换
- **安全保护** - 自动备份、冲突检查、预览模式
- **项目统计** - 文件数量、代码行数、文件类型分析

## 📦 安装

### 依赖
```bash
pip install -r requirements.txt
```

### 需要的包
- customtkinter - 现代UI框架
- pyperclip - 剪贴板操作

## 🚀 使用方法

### 1. 启动应用
```bash
python main.py
```

### 2. 基本工作流程

#### Tab 1: 项目设置
1. 点击"浏览"选择项目根目录
2. 设置最大文件大小 (默认1MB)
3. 选择是否包含行号
4. 点击"扫描"扫描项目文件
5. 在文件树中选择需要的文件 (支持搜索过滤)
6. 查看右侧统计信息
7. 点击"生成上下文"

#### Tab 2: 上下文生成
1. 输入你想要执行的代码修改描述
2. 点击"生成完整提示"
3. 点击"复制到剪贴板"
4. 将提示粘贴到LLM (如ChatGPT, Claude等)

#### Tab 3: Diff预览
1. 将LLM返回的diff内容粘贴到输入框
2. 点击"预览Diff"查看彩色高亮
3. 点击"验证格式"检查diff是否有效
4. 确认无误后进入下一步

#### Tab 4: 代码应用

**方式1 - 直接应用 (推荐)**
1. 勾选"创建备份文件" (强烈推荐)
2. 可选勾选"预览模式"进行测试
3. 点击"🚀 直接应用Diff"
4. 确认修改的文件列表
5. 等待应用完成
6. 如需回滚，点击"↩️ 回滚备份"

**方式2 - 传统手动**
1. 点击"生成应用提示"
2. 将提示发送给LLM
3. 获取完整文件内容
4. 手动替换文件

## 🎯 核心功能详解

### 文件扫描
- 支持自定义排除模式
- 文件大小限制
- 自动过滤二进制文件
- 显示文件类型和大小

### 上下文生成
- 生成美化的文件树
- 可选行号显示
- 支持大型项目
- 智能内容提取

### Diff验证
- 检查文件头格式
- 验证hunk头格式
- 检查文件路径有效性
- 提供详细的错误和警告信息

### 安全机制
- 自动文件备份
- 文件冲突检查
- 预览模式 (dry-run)
- 只读文件检测
- 目录权限检查

## 📁 项目结构

```
Diff-Code-Assistant/
├── main.py                 # 主程序 (赛博朋克增强版)
├── cyberpunk/             # 赛博朋克UI组件库
│   ├── __init__.py
│   ├── colors.py          # 配色方案
│   ├── components/        # UI组件
│   └── effects/           # 视觉特效
├── requirements.txt       # 依赖列表
└── README.md             # 本文件
```

## 🎨 UI组件

### 核心组件
- `CyberFrame` - 赛博朋克风格容器
- `CyberCard` - 卡片容器
- `CyberButton` - 霓虹按钮 (支持primary/secondary/success/danger变体)
- `CyberEntry` - 输入框
- `CyberLabel` - 标签 (支持title/heading/body/caption变体)
- `CyberTextbox` - 文本框
- `CyberProgressBar` - 进度条
- `CyberFileTree` - 增强文件树 (搜索/过滤/统计)
- `CyberProgressDialog` - 进度对话框

### 视觉特效
- `ScanlineEffect` - 扫描线
- `NeonGlow` - 霓虹发光
- `MatrixRain` - 矩阵雨
- `ParticleSystem` - 粒子系统

## ⚙️ 配置

### 排除模式
默认排除以下文件/目录:
```python
*.pyc, __pycache__, .git, .gitignore, node_modules,
.vscode, .idea, *.log, .env, dist, build,
*.egg-info, .pytest_cache, .coverage, *.tmp, *.bak
```

### 支持的文件类型
Python, JavaScript, TypeScript, React, Java, C++, C#, PHP, Ruby, Go, Rust, Swift, Kotlin, HTML, CSS, XML, JSON, YAML, Markdown, SQL, Shell等

## 🔧 高级功能

### 文件冲突检查
- 只读文件检测
- 目录权限验证
- 路径有效性检查

### 备份系统
- 时间戳命名
- 独立备份目录
- 保留原文件权限

### Diff解析
- 支持标准unified diff格式
- 处理时间戳信息
- 支持git路径前缀 (a/, b/)
- 智能路径清理

## 🐛 故障排除

### 问题: 扫描找不到文件
- 检查排除模式是否过于严格
- 确认文件大小限制是否合理
- 验证文件是否为文本文件

### 问题: Diff验证失败
- 确保diff格式正确 (使用`---`和`+++`头)
- 检查hunk头格式 (`@@`)
- 验证文件路径有效性

### 问题: 应用失败
- 检查文件是否只读
- 确认目录权限
- 查看错误日志
- 使用预览模式测试

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交Issue和Pull Request!

## 🌟 致谢

- CustomTkinter - 现代UI框架
- 赛博朋克文化 - 视觉灵感

---

**享受赛博朋克风格的代码重构之旅!** 🌐✨
