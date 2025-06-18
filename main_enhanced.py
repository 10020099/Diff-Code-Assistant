#!/usr/bin/env python3
"""
Diff Code Assistant - 增强版
一个功能强大的代码修改助手，帮助您与LLM协作进行大规模代码重构

作者: 优化版本
版本: 2.0.0
"""

import os
import glob
import difflib
import logging
import threading
import tempfile
import re
import shutil
from datetime import datetime
from typing import List, Dict, Optional, Tuple, Any, NamedTuple
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import customtkinter as ctk
import pyperclip

# ================================
# 配置部分
# ================================

# 默认排除模式
DEFAULT_EXCLUDE_PATTERNS = [
    "*.pyc", "__pycache__", ".git", ".gitignore", "node_modules",
    ".vscode", ".idea", "*.log", ".env", "dist", "build",
    "*.egg-info", ".pytest_cache", ".coverage", "*.tmp", "*.bak"
]

# 支持的文件扩展名
SUPPORTED_EXTENSIONS = {
    '.py': 'Python', '.js': 'JavaScript', '.ts': 'TypeScript', '.jsx': 'React JSX',
    '.tsx': 'React TSX', '.java': 'Java', '.cpp': 'C++', '.c': 'C', '.h': 'Header',
    '.cs': 'C#', '.php': 'PHP', '.rb': 'Ruby', '.go': 'Go', '.rs': 'Rust',
    '.swift': 'Swift', '.kt': 'Kotlin', '.html': 'HTML', '.css': 'CSS',
    '.scss': 'SCSS', '.xml': 'XML', '.json': 'JSON', '.yaml': 'YAML',
    '.yml': 'YAML', '.md': 'Markdown', '.txt': 'Text', '.sql': 'SQL',
    '.sh': 'Shell', '.bat': 'Batch', '.ps1': 'PowerShell'
}

# UI配置
UI_CONFIG = {
    'window_size': '1000x800',
    'color_theme': 'blue',
    'appearance_mode': 'System'
}

# 差异显示颜色
DIFF_COLORS = {
    'add': '#28a745',
    'delete': '#dc3545',
    'context': '#6c757d',
    'header': '#007bff'
}

# ================================
# 数据结构定义
# ================================

class DiffHunk(NamedTuple):
    """Diff块数据结构"""
    old_start: int
    old_count: int
    new_start: int
    new_count: int
    lines: List[str]

class FileChange(NamedTuple):
    """文件修改数据结构"""
    old_path: str
    new_path: str
    hunks: List[DiffHunk]
    is_new_file: bool = False
    is_deleted_file: bool = False

# ================================
# 工具函数部分
# ================================

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def is_text_file(file_path: str) -> bool:
    """检查文件是否为文本文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            f.read(1024)
        return True
    except (UnicodeDecodeError, PermissionError):
        return False

def get_file_size_str(file_path: str) -> str:
    """获取文件大小的字符串表示"""
    try:
        size = os.path.getsize(file_path)
        if size < 1024:
            return f"{size} B"
        elif size < 1024 * 1024:
            return f"{size / 1024:.1f} KB"
        else:
            return f"{size / (1024 * 1024):.1f} MB"
    except OSError:
        return "Unknown"

def scan_directory(root: str, exclude_patterns: List[str], max_file_size: int = 1024 * 1024) -> List[str]:
    """扫描目录并返回文件列表"""
    files = []
    try:
        for dirpath, dirnames, filenames in os.walk(root):
            rel_dir = os.path.relpath(dirpath, root)
            if any(glob.fnmatch.fnmatch(rel_dir, pat) for pat in exclude_patterns):
                dirnames.clear()
                continue
            
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                rel_path = os.path.relpath(file_path, root)
                
                # 检查排除模式
                if any(glob.fnmatch.fnmatch(rel_path, pat) for pat in exclude_patterns):
                    continue
                
                # 检查文件大小和类型
                try:
                    if os.path.getsize(file_path) > max_file_size:
                        continue
                    if not is_text_file(file_path):
                        continue
                except OSError:
                    continue
                
                files.append(file_path)
        
        logger.info(f"扫描完成，找到 {len(files)} 个文件")
        return files
    except Exception as e:
        logger.error(f"扫描目录时出错: {e}")
        return []

def build_tree(paths: List[str], root: str) -> str:
    """构建文件树字符串"""
    if not paths:
        return "空项目\n"
    
    tree = f"项目: {os.path.basename(root)}\n"
    sorted_paths = sorted([os.path.relpath(p, root) for p in paths])
    
    prev_parts = []
    for rel_path in sorted_paths:
        parts = rel_path.split(os.sep)
        for i, part in enumerate(parts):
            prefix = "│   " * i + "├── "
            if prev_parts[:i+1] != parts[:i+1]:
                if i == len(parts) - 1:  # 文件
                    file_path = os.path.join(root, rel_path)
                    size_str = get_file_size_str(file_path)
                    tree += f"{prefix}{part} ({size_str})\n"
                else:  # 目录
                    tree += f"{prefix}{part}/\n"
        prev_parts = parts
    
    return tree

def generate_context_from_paths(paths: List[str], root: str, include_line_numbers: bool = True) -> str:
    """从文件路径生成上下文字符串"""
    if not paths:
        return "没有选择任何文件。\n"
    
    tree_str = build_tree(paths, root)
    context = f"=== 项目结构 ===\n{tree_str}\n=== 文件内容 ({len(paths)} 个文件) ===\n\n"
    
    for i, path in enumerate(paths, 1):
        rel_path = os.path.relpath(path, root)
        try:
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            if include_line_numbers and content.strip():
                lines = content.split('\n')
                numbered_lines = [f"{line_num:4d} | {line}" for line_num, line in enumerate(lines, 1)]
                content = '\n'.join(numbered_lines)
            
            context += f"--- 文件 {i}: {rel_path} ---\n{content}\n--- 文件 {i} 结束 ---\n\n"
        except Exception as e:
            context += f"--- 文件 {i}: {rel_path} ---\n<读取失败: {e}>\n--- 文件 {i} 结束 ---\n\n"
    
    return context

def validate_diff(diff_content: str) -> Tuple[bool, str]:
    """验证diff内容的格式"""
    if not diff_content.strip():
        return False, "Diff内容为空"

    lines = diff_content.strip().split('\n')
    has_changes = any(line.startswith(('+', '-')) for line in lines)

    if not has_changes:
        return False, "Diff中没有发现任何更改"

    return True, ""

def validate_diff_advanced(diff_content: str) -> Tuple[bool, str, List[str]]:
    """高级diff验证，返回详细信息"""
    if not diff_content.strip():
        return False, "Diff内容为空", []

    lines = diff_content.strip().split('\n')
    warnings = []
    errors = []

    # 检查基本格式
    has_file_headers = any(line.startswith('--- ') or line.startswith('+++ ') for line in lines)
    has_hunk_headers = any(line.startswith('@@') for line in lines)
    has_changes = any(line.startswith(('+', '-')) and not line.startswith(('+++', '---')) for line in lines)

    if not has_file_headers:
        warnings.append("缺少文件头信息 (--- 和 +++ 行)")

    if not has_hunk_headers:
        warnings.append("缺少hunk头信息 (@@ 行)")

    if not has_changes:
        errors.append("没有发现实际的代码更改")

    # 检查hunk格式
    for i, line in enumerate(lines):
        if line.startswith('@@'):
            if not re.match(r'@@ -\d+(?:,\d+)? \+\d+(?:,\d+)? @@', line):
                errors.append(f"第 {i+1} 行: hunk头格式不正确")

    # 检查文件路径
    file_paths = []
    for line in lines:
        if line.startswith('--- ') or line.startswith('+++ '):
            path = line[4:].strip()
            if path and path != '/dev/null':
                file_paths.append(path)

    if not file_paths:
        errors.append("没有找到有效的文件路径")

    is_valid = len(errors) == 0
    message = ""

    if errors:
        message = "错误: " + "; ".join(errors)
    elif warnings:
        message = "警告: " + "; ".join(warnings)
    else:
        message = "格式验证通过"

    return is_valid, message, warnings

def check_file_conflicts(file_changes: List[FileChange], project_root: str) -> List[str]:
    """检查文件冲突"""
    conflicts = []

    for change in file_changes:
        file_path = os.path.join(project_root, change.new_path)

        # 检查文件是否存在且可写
        if os.path.exists(file_path):
            if not os.access(file_path, os.W_OK):
                conflicts.append(f"{change.new_path}: 文件只读，无法修改")
        else:
            # 检查目录是否存在且可写
            dir_path = os.path.dirname(file_path)
            if dir_path and not os.path.exists(dir_path):
                try:
                    os.makedirs(dir_path, exist_ok=True)
                except OSError as e:
                    conflicts.append(f"{change.new_path}: 无法创建目录 - {e}")
            elif dir_path and not os.access(dir_path, os.W_OK):
                conflicts.append(f"{change.new_path}: 目录不可写")

    return conflicts

def get_project_stats(file_paths: List[str]) -> Dict[str, Any]:
    """获取项目统计信息"""
    stats = {
        'total_files': len(file_paths),
        'total_lines': 0,
        'total_size': 0,
        'file_types': {}
    }

    for path in file_paths:
        try:
            stats['total_size'] += os.path.getsize(path)
            ext = Path(path).suffix.lower()
            stats['file_types'][ext] = stats['file_types'].get(ext, 0) + 1

            if is_text_file(path):
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    stats['total_lines'] += len(f.readlines())
        except Exception:
            continue

    return stats

def parse_diff(diff_content: str) -> List[FileChange]:
    """解析diff内容，返回文件修改列表"""
    if not diff_content.strip():
        return []

    lines = diff_content.strip().split('\n')
    file_changes = []
    current_file = None
    current_hunks = []
    current_hunk = None
    current_hunk_lines = []

    i = 0
    while i < len(lines):
        line = lines[i]

        # 检测文件头
        if line.startswith('--- '):
            # 保存之前的文件
            if current_file:
                if current_hunk and current_hunk_lines:
                    current_hunks.append(DiffHunk(*current_hunk, current_hunk_lines))
                file_changes.append(FileChange(current_file[0], current_file[1], current_hunks))

            # 开始新文件
            old_path = line[4:].strip()
            if old_path.startswith('a/'):
                old_path = old_path[2:]
            elif old_path.startswith('b/'):
                old_path = old_path[2:]

            # 查找对应的 +++ 行
            if i + 1 < len(lines) and lines[i + 1].startswith('+++ '):
                new_path = lines[i + 1][4:].strip()
                if new_path.startswith('a/'):
                    new_path = new_path[2:]
                elif new_path.startswith('b/'):
                    new_path = new_path[2:]
                i += 1
            else:
                new_path = old_path

            current_file = (old_path, new_path)
            current_hunks = []
            current_hunk = None
            current_hunk_lines = []

        # 检测hunk头 (@@)
        elif line.startswith('@@'):
            # 保存之前的hunk
            if current_hunk and current_hunk_lines:
                current_hunks.append(DiffHunk(*current_hunk, current_hunk_lines))

            # 解析hunk头
            match = re.match(r'@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@', line)
            if match:
                old_start = int(match.group(1))
                old_count = int(match.group(2)) if match.group(2) else 1
                new_start = int(match.group(3))
                new_count = int(match.group(4)) if match.group(4) else 1
                current_hunk = (old_start, old_count, new_start, new_count)
                current_hunk_lines = []

        # 收集hunk内容
        elif current_hunk and (line.startswith(' ') or line.startswith('+') or line.startswith('-')):
            current_hunk_lines.append(line)

        i += 1

    # 保存最后一个文件
    if current_file:
        if current_hunk and current_hunk_lines:
            current_hunks.append(DiffHunk(*current_hunk, current_hunk_lines))
        file_changes.append(FileChange(current_file[0], current_file[1], current_hunks))

    return file_changes

def create_backup(file_path: str, backup_dir: str) -> str:
    """创建文件备份"""
    if not os.path.exists(file_path):
        return ""

    os.makedirs(backup_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"{os.path.basename(file_path)}.{timestamp}.bak"
    backup_path = os.path.join(backup_dir, backup_name)

    shutil.copy2(file_path, backup_path)
    return backup_path

def apply_hunk_to_lines(lines: List[str], hunk: DiffHunk) -> List[str]:
    """将单个hunk应用到文件行列表"""
    result_lines = lines.copy()

    # 找到hunk的起始位置（转换为0基索引）
    start_line = hunk.old_start - 1

    # 收集要删除和添加的行
    to_delete = []  # (line_index, content)
    to_add = []     # (line_index, content)

    current_line = start_line

    for line in hunk.lines:
        if line.startswith(' '):
            # 上下文行，跳过
            current_line += 1
        elif line.startswith('-'):
            # 标记要删除的行
            delete_content = line[1:]
            to_delete.append((current_line, delete_content))
            current_line += 1
        elif line.startswith('+'):
            # 标记要添加的行（在当前位置插入）
            add_content = line[1:]
            to_add.append((current_line, add_content))
            # 注意：添加行不会改变当前行号

    # 先处理删除（从后往前删除避免索引变化）
    for line_idx, content in reversed(to_delete):
        if line_idx < len(result_lines):
            if result_lines[line_idx].rstrip() == content.rstrip():
                result_lines.pop(line_idx)
            else:
                logger.warning(f"要删除的行内容不匹配在行 {line_idx + 1}")

    # 重新计算添加位置（因为删除可能改变了行号）
    # 简化处理：重新解析hunk来确定正确的插入位置
    current_line = start_line
    insert_offset = 0

    for line in hunk.lines:
        if line.startswith(' '):
            current_line += 1
        elif line.startswith('-'):
            # 删除行会减少偏移
            insert_offset -= 1
            current_line += 1
        elif line.startswith('+'):
            # 添加行
            add_content = line[1:]
            insert_pos = current_line + insert_offset
            if insert_pos <= len(result_lines):
                result_lines.insert(insert_pos, add_content)
                insert_offset += 1
            else:
                result_lines.append(add_content)
                insert_offset += 1

    return result_lines

def apply_diff_to_file(file_path: str, file_change: FileChange, project_root: str) -> bool:
    """将diff修改应用到单个文件"""
    try:
        full_path = os.path.join(project_root, file_change.new_path)

        # 确保目录存在
        os.makedirs(os.path.dirname(full_path), exist_ok=True)

        # 读取现有文件内容
        if os.path.exists(full_path):
            with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            # 移除行尾换行符以便处理
            lines = [line.rstrip('\n\r') for line in lines]
        else:
            lines = []

        # 按照hunk的顺序从后往前应用，避免行号偏移问题
        sorted_hunks = sorted(file_change.hunks, key=lambda h: h.old_start, reverse=True)

        for hunk in sorted_hunks:
            lines = apply_hunk_to_lines(lines, hunk)

        # 写回文件
        with open(full_path, 'w', encoding='utf-8') as f:
            for line in lines:
                f.write(line + '\n')

        return True

    except Exception as e:
        logger.error(f"应用diff到文件 {file_path} 失败: {e}")
        return False

# ================================
# GUI组件部分
# ================================

class FileTreeFrame(ctk.CTkScrollableFrame):
    """增强的文件树组件"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.check_vars: Dict[str, tk.BooleanVar] = {}
        self.file_items: List[str] = []
        self.filter_var = tk.StringVar()
        self.filter_var.trace('w', self._filter_files)
        
        # 搜索和控制区域
        self._setup_controls()
    
    def _setup_controls(self):
        """设置控制组件"""
        # 搜索框
        search_frame = ctk.CTkFrame(self)
        search_frame.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkLabel(search_frame, text="过滤:").pack(side="left", padx=5)
        self.search_entry = ctk.CTkEntry(search_frame, textvariable=self.filter_var, 
                                       placeholder_text="输入关键词过滤文件")
        self.search_entry.pack(side="left", fill="x", expand=True, padx=5)
        
        # 控制按钮
        btn_frame = ctk.CTkFrame(self)
        btn_frame.pack(fill="x", padx=5, pady=2)
        
        ctk.CTkButton(btn_frame, text="全选", command=self._select_all, width=60).pack(side="left", padx=2)
        ctk.CTkButton(btn_frame, text="取消", command=self._deselect_all, width=60).pack(side="left", padx=2)
        ctk.CTkButton(btn_frame, text="反选", command=self._invert_selection, width=60).pack(side="left", padx=2)
        
        self.stats_label = ctk.CTkLabel(btn_frame, text="")
        self.stats_label.pack(side="right", padx=5)
    
    def load_files(self, file_paths: List[str], root_dir: str):
        """加载文件列表"""
        # 清空现有内容
        for widget in self.winfo_children():
            if isinstance(widget, ctk.CTkCheckBox):
                widget.destroy()
        
        self.check_vars.clear()
        self.file_items.clear()
        
        sorted_paths = sorted([os.path.relpath(p, root_dir) for p in file_paths])
        
        for rel_path in sorted_paths:
            full_path = os.path.join(root_dir, rel_path)
            parts = rel_path.split(os.sep)
            indent = len(parts) - 1
            filename = parts[-1]
            ext = Path(filename).suffix.lower()
            
            self.file_items.append(rel_path)
            
            var = tk.BooleanVar(value=True)
            size_str = get_file_size_str(full_path)
            type_str = SUPPORTED_EXTENSIONS.get(ext, '未知')
            display_text = f"{'  ' * indent}{filename} ({size_str}) [{type_str}]"
            
            cb = ctk.CTkCheckBox(self, text=display_text, variable=var)
            cb.pack(anchor="w", padx=5, pady=1)
            
            self.check_vars[rel_path] = var
        
        self._update_stats()
    
    def get_selected_files(self, root_dir: str) -> List[str]:
        """获取选中的文件路径"""
        return [os.path.join(root_dir, rel_path) 
                for rel_path, var in self.check_vars.items() if var.get()]
    
    def _filter_files(self, *args):
        """过滤文件显示"""
        filter_text = self.filter_var.get().lower()
        for widget in self.winfo_children():
            if isinstance(widget, ctk.CTkCheckBox):
                text = widget.cget("text").lower()
                if not filter_text or filter_text in text:
                    widget.pack(anchor="w", padx=5, pady=1)
                else:
                    widget.pack_forget()
    
    def _select_all(self):
        """全选"""
        for var in self.check_vars.values():
            var.set(True)
        self._update_stats()
    
    def _deselect_all(self):
        """取消全选"""
        for var in self.check_vars.values():
            var.set(False)
        self._update_stats()
    
    def _invert_selection(self):
        """反选"""
        for var in self.check_vars.values():
            var.set(not var.get())
        self._update_stats()
    
    def _update_stats(self):
        """更新统计信息"""
        selected = sum(1 for var in self.check_vars.values() if var.get())
        total = len(self.check_vars)
        self.stats_label.configure(text=f"选中: {selected}/{total}")

class DiffViewer(tk.Text):
    """Diff查看器组件"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, wrap="none", **kwargs)
        
        # 配置标签样式
        self.tag_config('add', foreground=DIFF_COLORS['add'])
        self.tag_config('delete', foreground=DIFF_COLORS['delete'])
        self.tag_config('context', foreground=DIFF_COLORS['context'])
        self.tag_config('header', foreground=DIFF_COLORS['header'], font=('Consolas', 10, 'bold'))
        
        # 滚动条
        scrollbar_v = ttk.Scrollbar(parent, orient="vertical", command=self.yview)
        scrollbar_v.pack(side="right", fill="y")
        self.configure(yscrollcommand=scrollbar_v.set)
        
        scrollbar_h = ttk.Scrollbar(parent, orient="horizontal", command=self.xview)
        scrollbar_h.pack(side="bottom", fill="x")
        self.configure(xscrollcommand=scrollbar_h.set)
    
    def display_diff(self, diff_content: str):
        """显示diff内容"""
        self.delete("1.0", "end")
        
        if not diff_content.strip():
            self.insert("end", "没有diff内容\n", 'context')
            return
        
        for line in diff_content.split('\n'):
            if line.startswith('+++') or line.startswith('---') or line.startswith('@@'):
                self.insert("end", line + '\n', 'header')
            elif line.startswith('+'):
                self.insert("end", line + '\n', 'add')
            elif line.startswith('-'):
                self.insert("end", line + '\n', 'delete')
            else:
                self.insert("end", line + '\n', 'context')

class ProgressDialog(ctk.CTkToplevel):
    """进度对话框"""
    
    def __init__(self, parent, title="处理中..."):
        super().__init__(parent)
        self.title(title)
        self.geometry("400x150")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        
        self.progress_label = ctk.CTkLabel(self, text="正在处理...")
        self.progress_label.pack(pady=20)
        
        self.progress_bar = ctk.CTkProgressBar(self)
        self.progress_bar.pack(fill="x", padx=20, pady=10)
        self.progress_bar.set(0)
        
        self.cancelled = False
    
    def update_progress(self, value: float, text: str = ""):
        """更新进度"""
        self.progress_bar.set(value)
        if text:
            self.progress_label.configure(text=text)
        self.update()

# ================================
# 主应用程序
# ================================

class DiffCodeAssistant(ctk.CTk):
    """Diff Code Assistant 增强版主应用"""
    
    def __init__(self):
        super().__init__()
        
        # 应用配置
        self.title("Diff Code Assistant - 增强版")
        self.geometry(UI_CONFIG['window_size'])
        self.minsize(800, 600)
        
        # 数据存储
        self.project_root: Optional[str] = None
        self.all_files: List[str] = []
        self.context: str = ""
        self.current_diff: str = ""
        self.exclude_patterns = DEFAULT_EXCLUDE_PATTERNS.copy()
        self.backup_files: List[str] = []  # 备份文件列表
        
        # 初始化UI
        self._setup_ui()
        
        # 绑定事件
        self.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        logger.info("应用启动完成")
    
    def _setup_ui(self):
        """设置用户界面"""
        # 创建选项卡
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(expand=True, fill="both", padx=10, pady=10)
        
        for tab in ["项目设置", "上下文生成", "Diff预览", "代码应用"]:
            self.tabview.add(tab)
        
        self._setup_project_tab()
        self._setup_context_tab()
        self._setup_diff_tab()
        self._setup_apply_tab()
    
    def _setup_project_tab(self):
        """设置项目配置选项卡"""
        tab = self.tabview.tab("项目设置")
        
        # 项目路径选择
        path_frame = ctk.CTkFrame(tab)
        path_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(path_frame, text="项目路径:").pack(side="left", padx=5)
        self.path_entry = ctk.CTkEntry(path_frame, placeholder_text="选择项目根目录")
        self.path_entry.pack(side="left", fill="x", expand=True, padx=5)
        ctk.CTkButton(path_frame, text="浏览", command=self._browse_project, width=80).pack(side="right", padx=5)
        
        # 设置选项
        settings_frame = ctk.CTkFrame(tab)
        settings_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(settings_frame, text="最大文件大小(MB):").pack(side="left", padx=5)
        self.max_size_entry = ctk.CTkEntry(settings_frame, width=80)
        self.max_size_entry.insert(0, "1")
        self.max_size_entry.pack(side="left", padx=5)
        
        self.include_line_numbers = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(settings_frame, text="包含行号", variable=self.include_line_numbers).pack(side="left", padx=10)
        
        ctk.CTkButton(settings_frame, text="扫描项目", command=self._scan_project, width=100).pack(side="right", padx=5)
        
        # 主内容区域
        content_frame = ctk.CTkFrame(tab)
        content_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # 左侧：文件树
        left_frame = ctk.CTkFrame(content_frame)
        left_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        
        ctk.CTkLabel(left_frame, text="文件选择", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=5)
        self.file_tree = FileTreeFrame(left_frame, height=400)
        self.file_tree.pack(fill="both", expand=True, padx=5, pady=5)
        
        # 右侧：统计信息
        right_frame = ctk.CTkFrame(content_frame, width=300)
        right_frame.pack(side="right", fill="y", padx=5, pady=5)
        right_frame.pack_propagate(False)
        
        ctk.CTkLabel(right_frame, text="项目统计", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=5)
        self.stats_text = ctk.CTkTextbox(right_frame, height=200)
        self.stats_text.pack(fill="both", expand=True, padx=5, pady=5)
        
        # 底部按钮
        button_frame = ctk.CTkFrame(tab)
        button_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkButton(button_frame, text="生成上下文", command=self._generate_context).pack(side="right", padx=5)
        ctk.CTkButton(button_frame, text="刷新统计", command=self._update_stats).pack(side="right", padx=5)
    
    def _setup_context_tab(self):
        """设置上下文生成选项卡"""
        tab = self.tabview.tab("上下文生成")
        
        # 提示输入
        prompt_frame = ctk.CTkFrame(tab)
        prompt_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(prompt_frame, text="LLM指令:", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", padx=5, pady=2)
        self.prompt_entry = ctk.CTkEntry(prompt_frame, height=40, placeholder_text="描述您希望执行的代码修改...")
        self.prompt_entry.pack(fill="x", padx=5, pady=5)
        
        # 按钮
        button_frame = ctk.CTkFrame(prompt_frame)
        button_frame.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkButton(button_frame, text="生成完整提示", command=self._create_full_prompt).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="复制到剪贴板", command=self._copy_prompt).pack(side="left", padx=5)
        
        # 上下文预览
        preview_frame = ctk.CTkFrame(tab)
        preview_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        ctk.CTkLabel(preview_frame, text="生成的完整提示:", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", padx=5, pady=2)
        self.prompt_display = ctk.CTkTextbox(preview_frame, wrap="word")
        self.prompt_display.pack(fill="both", expand=True, padx=5, pady=5)
    
    def _setup_diff_tab(self):
        """设置Diff预览选项卡"""
        tab = self.tabview.tab("Diff预览")
        
        # 输入区域
        input_frame = ctk.CTkFrame(tab)
        input_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(input_frame, text="粘贴LLM返回的Diff:", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", padx=5, pady=2)
        self.diff_input = ctk.CTkTextbox(input_frame, height=120)
        self.diff_input.pack(fill="x", padx=5, pady=5)
        
        # 按钮
        button_frame = ctk.CTkFrame(input_frame)
        button_frame.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkButton(button_frame, text="预览Diff", command=self._preview_diff).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="验证格式", command=self._validate_diff).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="清空", command=self._clear_diff).pack(side="left", padx=5)
        
        # 预览区域
        preview_frame = ctk.CTkFrame(tab)
        preview_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        ctk.CTkLabel(preview_frame, text="Diff预览 (绿色=添加, 红色=删除):", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", padx=5, pady=2)
        
        diff_container = ctk.CTkFrame(preview_frame)
        diff_container.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.diff_viewer = DiffViewer(diff_container)
        self.diff_viewer.pack(fill="both", expand=True)
    
    def _setup_apply_tab(self):
        """设置代码应用选项卡"""
        tab = self.tabview.tab("代码应用")

        # 说明
        info_frame = ctk.CTkFrame(tab)
        info_frame.pack(fill="x", padx=10, pady=10)

        info_text = """两种应用方式：
方式1 (推荐): 直接应用Diff - 自动解析并应用修改，支持备份和回滚
方式2 (传统): 手动应用 - 生成提示给LLM，获取完整代码后手动替换"""

        ctk.CTkLabel(info_frame, text=info_text, justify="left").pack(padx=10, pady=10)

        # 直接应用区域
        direct_frame = ctk.CTkFrame(tab)
        direct_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(direct_frame, text="方式1: 直接应用Diff", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=5, pady=5)

        # 直接应用选项
        options_frame = ctk.CTkFrame(direct_frame)
        options_frame.pack(fill="x", padx=5, pady=5)

        self.create_backup_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(options_frame, text="创建备份文件", variable=self.create_backup_var).pack(side="left", padx=5)

        self.dry_run_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(options_frame, text="预览模式(不实际修改)", variable=self.dry_run_var).pack(side="left", padx=10)

        # 直接应用按钮
        direct_buttons = ctk.CTkFrame(direct_frame)
        direct_buttons.pack(fill="x", padx=5, pady=5)

        ctk.CTkButton(direct_buttons, text="🚀 直接应用Diff", command=self._apply_diff_directly,
                     fg_color="#28a745", hover_color="#218838").pack(side="left", padx=5)
        ctk.CTkButton(direct_buttons, text="📋 预览修改", command=self._preview_diff_changes).pack(side="left", padx=5)
        ctk.CTkButton(direct_buttons, text="↩️ 回滚备份", command=self._rollback_changes).pack(side="left", padx=5)

        # 分隔线
        separator = ctk.CTkFrame(tab, height=2)
        separator.pack(fill="x", padx=10, pady=10)

        # 传统方式区域
        traditional_frame = ctk.CTkFrame(tab)
        traditional_frame.pack(fill="both", expand=True, padx=10, pady=5)

        ctk.CTkLabel(traditional_frame, text="方式2: 传统手动应用", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=5, pady=5)

        # 按钮
        button_frame = ctk.CTkFrame(traditional_frame)
        button_frame.pack(fill="x", padx=5, pady=5)

        ctk.CTkButton(button_frame, text="生成应用提示", command=self._generate_apply_prompt).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="复制应用提示", command=self._copy_apply_prompt).pack(side="left", padx=5)

        # 应用提示显示
        display_frame = ctk.CTkFrame(traditional_frame)
        display_frame.pack(fill="both", expand=True, padx=5, pady=5)

        ctk.CTkLabel(display_frame, text="应用提示:", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", padx=5, pady=2)
        self.apply_prompt_display = ctk.CTkTextbox(display_frame)
        self.apply_prompt_display.pack(fill="both", expand=True, padx=5, pady=5)

        # 状态显示
        self.apply_status_label = ctk.CTkLabel(tab, text="", font=ctk.CTkFont(size=12))
        self.apply_status_label.pack(pady=5)
    
    def _browse_project(self):
        """浏览选择项目目录"""
        folder = filedialog.askdirectory(title="选择项目根目录")
        if folder:
            self.path_entry.delete(0, ctk.END)
            self.path_entry.insert(0, folder)
            self.project_root = folder
    
    def _scan_project(self):
        """扫描项目文件"""
        project_path = self.path_entry.get().strip()
        if not project_path or not os.path.isdir(project_path):
            messagebox.showerror("错误", "请选择有效的项目目录")
            return
        
        try:
            max_size_mb = float(self.max_size_entry.get())
            max_size = int(max_size_mb * 1024 * 1024)
        except ValueError:
            max_size = 1024 * 1024
        
        self.project_root = project_path
        
        # 后台扫描
        progress = ProgressDialog(self, "扫描项目文件...")
        
        def scan_thread():
            try:
                progress.update_progress(0.3, "正在扫描文件...")
                self.all_files = scan_directory(project_path, self.exclude_patterns, max_size)
                
                progress.update_progress(0.7, "正在加载文件树...")
                self.after(0, lambda: self.file_tree.load_files(self.all_files, project_path))
                
                progress.update_progress(0.9, "正在更新统计...")
                self.after(0, self._update_stats)
                
                progress.update_progress(1.0, "扫描完成")
                self.after(100, progress.destroy)
                
                self.after(0, lambda: messagebox.showinfo("完成", f"扫描完成，共找到 {len(self.all_files)} 个文件"))
            except Exception as e:
                logger.error(f"扫描失败: {e}")
                self.after(0, lambda: messagebox.showerror("错误", f"扫描失败: {e}"))
                self.after(0, progress.destroy)
        
        threading.Thread(target=scan_thread, daemon=True).start()
    
    def _generate_context(self):
        """生成上下文"""
        if not self.project_root:
            messagebox.showerror("错误", "请先扫描项目")
            return
        
        selected_files = self.file_tree.get_selected_files(self.project_root)
        if not selected_files:
            messagebox.showwarning("警告", "请至少选择一个文件")
            return
        
        progress = ProgressDialog(self, "生成上下文...")
        
        def generate_thread():
            try:
                progress.update_progress(0.5, "正在读取文件...")
                include_line_numbers = self.include_line_numbers.get()
                self.context = generate_context_from_paths(selected_files, self.project_root, include_line_numbers)
                
                progress.update_progress(1.0, "生成完成")
                self.after(100, progress.destroy)
                self.after(0, lambda: self.tabview.set("上下文生成"))
                
                logger.info(f"上下文生成成功，包含 {len(selected_files)} 个文件")
            except Exception as e:
                logger.error(f"生成上下文失败: {e}")
                self.after(0, lambda: messagebox.showerror("错误", f"生成失败: {e}"))
                self.after(0, progress.destroy)
        
        threading.Thread(target=generate_thread, daemon=True).start()
    
    def _create_full_prompt(self):
        """创建完整提示"""
        if not self.context:
            messagebox.showerror("错误", "请先生成上下文")
            return
        
        user_prompt = self.prompt_entry.get().strip()
        if not user_prompt:
            messagebox.showwarning("警告", "请输入LLM指令")
            return
        
        full_prompt = f"""请根据以下项目上下文和指令，生成代码修改的diff格式输出：

{self.context}

=== 用户指令 ===
{user_prompt}

=== 要求 ===
1. 仔细分析项目结构和代码内容
2. 根据指令生成相应的代码修改
3. 以标准diff格式输出所有更改
4. 确保修改的一致性和正确性

请生成diff格式的修改建议："""
        
        self.prompt_display.delete("0.0", "end")
        self.prompt_display.insert("0.0", full_prompt)
    
    def _copy_prompt(self):
        """复制提示到剪贴板"""
        prompt = self.prompt_display.get("0.0", "end").strip()
        if not prompt:
            messagebox.showwarning("警告", "没有可复制的内容")
            return
        
        try:
            pyperclip.copy(prompt)
            messagebox.showinfo("成功", "提示已复制到剪贴板")
        except Exception as e:
            messagebox.showerror("错误", f"复制失败: {e}")
    
    def _preview_diff(self):
        """预览Diff"""
        diff_content = self.diff_input.get("0.0", "end").strip()
        if not diff_content:
            messagebox.showwarning("警告", "请输入Diff内容")
            return
        
        self.current_diff = diff_content
        self.diff_viewer.display_diff(diff_content)
    
    def _validate_diff(self):
        """验证Diff内容"""
        diff_content = self.diff_input.get("0.0", "end").strip()
        if not diff_content:
            messagebox.showwarning("警告", "请输入Diff内容")
            return

        is_valid, message, warnings = validate_diff_advanced(diff_content)

        if is_valid:
            if warnings:
                messagebox.showwarning("验证结果", f"格式验证通过，但有警告:\n{message}")
            else:
                messagebox.showinfo("验证结果", "Diff格式验证通过")
        else:
            messagebox.showerror("验证结果", f"Diff格式验证失败:\n{message}")
    
    def _clear_diff(self):
        """清空Diff内容"""
        self.diff_input.delete("0.0", "end")
        self.diff_viewer.display_diff("")
        self.current_diff = ""
    
    def _generate_apply_prompt(self):
        """生成应用提示"""
        if not self.current_diff:
            messagebox.showerror("错误", "请先预览Diff内容")
            return
        
        apply_prompt = f"""请根据以下diff内容对文件进行修改，并返回修改后的完整文件内容：

=== DIFF内容 ===
{self.current_diff}

=== 要求 ===
1. 严格按照diff指示进行修改
2. 返回所有被修改文件的完整内容
3. 保持代码格式和语法正确
4. 如有新文件，提供完整内容

请返回修改后的文件内容："""
        
        self.apply_prompt_display.delete("0.0", "end")
        self.apply_prompt_display.insert("0.0", apply_prompt)
    
    def _copy_apply_prompt(self):
        """复制应用提示"""
        prompt = self.apply_prompt_display.get("0.0", "end").strip()
        if not prompt:
            messagebox.showwarning("警告", "没有可复制的内容")
            return

        try:
            pyperclip.copy(prompt)
            messagebox.showinfo("成功", "应用提示已复制到剪贴板")
        except Exception as e:
            messagebox.showerror("错误", f"复制失败: {e}")

    def _apply_diff_directly(self):
        """直接应用diff修改"""
        if not self.current_diff:
            messagebox.showerror("错误", "请先预览Diff内容")
            return

        if not self.project_root:
            messagebox.showerror("错误", "请先选择项目根目录")
            return

        # 高级验证diff
        is_valid, message, warnings = validate_diff_advanced(self.current_diff)
        if not is_valid:
            messagebox.showerror("验证失败", f"Diff格式验证失败:\n{message}")
            return

        if warnings:
            if not messagebox.askyesno("验证警告", f"Diff验证有警告:\n{message}\n\n是否继续？"):
                return

        # 解析diff
        try:
            file_changes = parse_diff(self.current_diff)
            if not file_changes:
                messagebox.showerror("错误", "无法解析Diff内容或没有发现文件修改")
                return
        except Exception as e:
            messagebox.showerror("错误", f"解析Diff失败: {e}")
            return

        # 检查文件冲突
        conflicts = check_file_conflicts(file_changes, self.project_root)
        if conflicts:
            conflict_msg = "发现以下文件冲突:\n\n" + "\n".join(f"• {conflict}" for conflict in conflicts[:10])
            if len(conflicts) > 10:
                conflict_msg += f"\n... 还有 {len(conflicts) - 10} 个冲突"
            conflict_msg += "\n\n是否继续？"

            if not messagebox.askyesno("文件冲突", conflict_msg):
                return

        # 确认对话框
        affected_files = [change.new_path for change in file_changes]
        confirm_msg = f"即将修改以下 {len(affected_files)} 个文件:\n\n"
        confirm_msg += "\n".join(f"• {path}" for path in affected_files[:10])
        if len(affected_files) > 10:
            confirm_msg += f"\n... 还有 {len(affected_files) - 10} 个文件"

        confirm_msg += f"\n\n备份: {'是' if self.create_backup_var.get() else '否'}"
        confirm_msg += f"\n预览模式: {'是' if self.dry_run_var.get() else '否'}"

        if conflicts:
            confirm_msg += f"\n冲突: {len(conflicts)} 个"
        if warnings:
            confirm_msg += f"\n警告: {len(warnings)} 个"

        confirm_msg += "\n\n确定要继续吗？"

        if not messagebox.askyesno("确认应用", confirm_msg):
            return

        # 执行应用
        self._execute_diff_application(file_changes)

    def _execute_diff_application(self, file_changes: List[FileChange]):
        """执行diff应用"""
        progress = ProgressDialog(self, "应用Diff修改...")
        success_count = 0
        error_count = 0
        backup_dir = None

        def apply_thread():
            nonlocal success_count, error_count, backup_dir

            try:
                # 创建备份目录
                if self.create_backup_var.get() and not self.dry_run_var.get():
                    backup_dir = os.path.join(self.project_root, ".diff_backups",
                                            datetime.now().strftime("%Y%m%d_%H%M%S"))
                    os.makedirs(backup_dir, exist_ok=True)

                total_files = len(file_changes)

                for i, file_change in enumerate(file_changes):
                    progress.update_progress((i + 1) / total_files,
                                           f"处理文件 {i + 1}/{total_files}: {file_change.new_path}")

                    try:
                        file_path = os.path.join(self.project_root, file_change.new_path)

                        # 创建备份
                        if self.create_backup_var.get() and not self.dry_run_var.get():
                            if os.path.exists(file_path):
                                backup_path = create_backup(file_path, backup_dir)
                                if backup_path:
                                    self.backup_files.append(backup_path)

                        # 应用修改（除非是预览模式）
                        if not self.dry_run_var.get():
                            if apply_diff_to_file(file_path, file_change, self.project_root):
                                success_count += 1
                            else:
                                error_count += 1
                        else:
                            success_count += 1  # 预览模式都算成功

                    except Exception as e:
                        logger.error(f"处理文件 {file_change.new_path} 失败: {e}")
                        error_count += 1

                progress.update_progress(1.0, "应用完成")
                self.after(100, progress.destroy)

                # 显示结果
                result_msg = f"应用完成!\n\n成功: {success_count} 个文件\n失败: {error_count} 个文件"
                if self.dry_run_var.get():
                    result_msg += "\n\n(预览模式，未实际修改文件)"
                elif backup_dir and self.backup_files:
                    result_msg += f"\n\n备份位置: {backup_dir}"

                self.after(0, lambda: self._update_apply_status(result_msg))
                self.after(0, lambda: messagebox.showinfo("应用结果", result_msg))

            except Exception as e:
                logger.error(f"应用diff失败: {e}")
                self.after(0, lambda: messagebox.showerror("错误", f"应用失败: {e}"))
                self.after(0, progress.destroy)

        threading.Thread(target=apply_thread, daemon=True).start()

    def _preview_diff_changes(self):
        """预览diff修改"""
        if not self.current_diff:
            messagebox.showerror("错误", "请先预览Diff内容")
            return

        try:
            file_changes = parse_diff(self.current_diff)
            if not file_changes:
                messagebox.showwarning("警告", "没有发现文件修改")
                return

            # 创建预览窗口
            preview_window = ctk.CTkToplevel(self)
            preview_window.title("Diff修改预览")
            preview_window.geometry("800x600")
            preview_window.transient(self)

            # 预览内容
            preview_text = ctk.CTkTextbox(preview_window)
            preview_text.pack(fill="both", expand=True, padx=10, pady=10)

            preview_content = f"将要修改的文件 ({len(file_changes)} 个):\n\n"

            for i, change in enumerate(file_changes, 1):
                preview_content += f"{i}. {change.new_path}\n"
                preview_content += f"   修改块数: {len(change.hunks)}\n"

                for j, hunk in enumerate(change.hunks):
                    additions = sum(1 for line in hunk.lines if line.startswith('+'))
                    deletions = sum(1 for line in hunk.lines if line.startswith('-'))
                    preview_content += f"   块 {j+1}: +{additions} -{deletions} 行\n"

                preview_content += "\n"

            preview_text.insert("0.0", preview_content)

        except Exception as e:
            messagebox.showerror("错误", f"预览失败: {e}")

    def _rollback_changes(self):
        """回滚修改"""
        if not self.backup_files:
            messagebox.showwarning("警告", "没有可回滚的备份文件")
            return

        confirm_msg = f"发现 {len(self.backup_files)} 个备份文件，确定要回滚吗？\n\n"
        confirm_msg += "这将恢复所有修改前的文件状态。"

        if not messagebox.askyesno("确认回滚", confirm_msg):
            return

        success_count = 0
        error_count = 0

        for backup_path in self.backup_files:
            try:
                # 从备份路径推断原始文件路径
                backup_name = os.path.basename(backup_path)
                original_name = backup_name.split('.')[0] + '.' + backup_name.split('.')[1] if '.' in backup_name else backup_name.split('.')[0]

                # 这里需要更复杂的逻辑来确定原始文件位置
                # 简化处理：假设备份文件名包含相对路径信息
                messagebox.showinfo("提示", "回滚功能需要手动实现文件路径映射")
                break

            except Exception as e:
                logger.error(f"回滚文件 {backup_path} 失败: {e}")
                error_count += 1

    def _update_apply_status(self, message: str):
        """更新应用状态"""
        if hasattr(self, 'apply_status_label'):
            self.apply_status_label.configure(text=message)
    
    def _update_stats(self):
        """更新统计信息"""
        if hasattr(self, 'file_tree') and self.project_root:
            selected_files = self.file_tree.get_selected_files(self.project_root)
            if selected_files:
                stats = get_project_stats(selected_files)
                
                # 格式化统计信息
                stats_text = f"文件总数: {stats['total_files']}\n"
                stats_text += f"代码行数: {stats['total_lines']:,}\n"
                
                size = stats['total_size']
                if size < 1024:
                    size_str = f"{size} B"
                elif size < 1024 * 1024:
                    size_str = f"{size / 1024:.1f} KB"
                else:
                    size_str = f"{size / (1024 * 1024):.1f} MB"
                
                stats_text += f"总大小: {size_str}\n\n文件类型:\n"
                
                if stats['file_types']:
                    sorted_types = sorted(stats['file_types'].items(), key=lambda x: x[1], reverse=True)
                    for ext, count in sorted_types[:10]:  # 显示前10种类型
                        ext_name = SUPPORTED_EXTENSIONS.get(ext, '未知')
                        stats_text += f"  {ext or '无扩展名'} ({ext_name}): {count}\n"
                
                self.stats_text.delete("0.0", "end")
                self.stats_text.insert("0.0", stats_text)
    
    def _on_closing(self):
        """应用关闭处理"""
        logger.info("应用关闭")
        self.destroy()

# ================================
# 主函数
# ================================

def main():
    """主函数"""
    # 设置外观
    ctk.set_appearance_mode(UI_CONFIG['appearance_mode'])
    ctk.set_default_color_theme(UI_CONFIG['color_theme'])
    
    try:
        app = DiffCodeAssistant()
        app.mainloop()
    except KeyboardInterrupt:
        logger.info("用户中断")
    except Exception as e:
        logger.error(f"应用错误: {e}")
        messagebox.showerror("错误", f"应用遇到错误: {e}")

if __name__ == "__main__":
    main()