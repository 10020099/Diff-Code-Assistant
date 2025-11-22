"""
赛博朋克文本框组件
提供多行文本编辑和显示
"""

import customtkinter as ctk
import tkinter as tk
from typing import Optional
from ..theme import CyberpunkTheme

class CyberTextbox(ctk.CTkTextbox):
    """
    赛博朋克风格文本框
    """
    
    def __init__(self,
                 master,
                 theme: Optional[CyberpunkTheme] = None,
                 with_line_numbers: bool = False,
                 read_only: bool = False,
                 **kwargs):
        """
        初始化文本框
        
        Args:
            master: 父组件
            theme: 主题实例
            with_line_numbers: 是否显示行号
            read_only: 是否只读
            **kwargs: 其他CTkTextbox参数
        """
        self.theme = theme or CyberpunkTheme()
        
        # 获取样式
        style = self.theme.get_textbox_style()
        merged_kwargs = {**style, **kwargs}
        merged_kwargs.pop('font', None)
        
        super().__init__(master, **merged_kwargs)
        
        self.with_line_numbers = with_line_numbers
        self.read_only = read_only
        
        # 配置只读
        if read_only:
            self.configure(state="disabled")
        
        # 绑定事件
        self.bind("<KeyRelease>", self._on_text_change)
    
    def _on_text_change(self, event):
        """文本改变事件"""
        pass  # 子类可以重写
    
    def set_text(self, text: str):
        """
        设置文本内容
        
        Args:
            text: 文本内容
        """
        was_disabled = self.cget("state") == "disabled"
        
        if was_disabled:
            self.configure(state="normal")
        
        self.delete("0.0", "end")
        self.insert("0.0", text)
        
        if was_disabled:
            self.configure(state="disabled")
    
    def get_text(self) -> str:
        """
        获取文本内容
        
        Returns:
            文本内容
        """
        return self.get("0.0", "end-1c")
    
    def append_text(self, text: str):
        """
        追加文本
        
        Args:
            text: 要追加的文本
        """
        was_disabled = self.cget("state") == "disabled"
        
        if was_disabled:
            self.configure(state="normal")
        
        self.insert("end", text)
        self.see("end")
        
        if was_disabled:
            self.configure(state="disabled")
    
    def clear(self):
        """清空文本"""
        was_disabled = self.cget("state") == "disabled"
        
        if was_disabled:
            self.configure(state="normal")
        
        self.delete("0.0", "end")
        
        if was_disabled:
            self.configure(state="disabled")
    
    def search_text(self, pattern: str, start: str = "1.0") -> Optional[str]:
        """
        搜索文本
        
        Args:
            pattern: 搜索模式
            start: 起始位置
        
        Returns:
            找到的位置或None
        """
        return self.search(pattern, start, stopindex="end")
    
    def highlight_line(self, line_number: int, color: str = None):
        """
        高亮指定行
        
        Args:
            line_number: 行号 (从1开始)
            color: 高亮颜色
        """
        if color is None:
            color = self.theme.color_scheme['primary']
        
        tag_name = f"highlight_{line_number}"
        start = f"{line_number}.0"
        end = f"{line_number}.end"
        
        self.tag_add(tag_name, start, end)
        self.tag_config(tag_name, background=color)

class CyberCodeEditor(CyberTextbox):
    """
    代码编辑器文本框
    支持基本的语法高亮
    """
    
    def __init__(self,
                 master,
                 theme: Optional[CyberpunkTheme] = None,
                 language: str = 'python',
                 **kwargs):
        """
        初始化代码编辑器
        
        Args:
            master: 父组件
            theme: 主题实例
            language: 编程语言
            **kwargs: 其他参数
        """
        super().__init__(
            master=master,
            theme=theme,
            with_line_numbers=True,
            **kwargs
        )
        
        self.language = language
        
        # 配置语法高亮标签
        self._setup_syntax_tags()
        
        # 绑定语法高亮
        self.bind("<KeyRelease>", self._apply_syntax_highlight)
    
    def _setup_syntax_tags(self):
        """设置语法高亮标签"""
        # Python关键字
        self.tag_config('keyword', foreground=self.theme.color_scheme['primary'])
        self.tag_config('string', foreground=self.theme.color_scheme['success'])
        self.tag_config('comment', foreground=self.theme.color_scheme['text_secondary'])
        self.tag_config('number', foreground=self.theme.color_scheme['warning'])
    
    def _apply_syntax_highlight(self, event=None):
        """应用语法高亮(简化版)"""
        # 这里只是一个示例,实际需要更复杂的词法分析
        # 可以集成pygments等库实现完整的语法高亮
        pass

class CyberLogViewer(CyberTextbox):
    """
    日志查看器
    """
    
    def __init__(self,
                 master,
                 theme: Optional[CyberpunkTheme] = None,
                 max_lines: int = 1000,
                 **kwargs):
        """
        初始化日志查看器
        
        Args:
            master: 父组件
            theme: 主题实例
            max_lines: 最大行数
            **kwargs: 其他参数
        """
        super().__init__(
            master=master,
            theme=theme,
            read_only=True,
            **kwargs
        )
        
        self.max_lines = max_lines
        
        # 配置日志级别标签
        self.tag_config('INFO', foreground=self.theme.color_scheme['info'])
        self.tag_config('WARNING', foreground=self.theme.color_scheme['warning'])
        self.tag_config('ERROR', foreground=self.theme.color_scheme['error'])
        self.tag_config('SUCCESS', foreground=self.theme.color_scheme['success'])
        self.tag_config('DEBUG', foreground=self.theme.color_scheme['text_secondary'])
    
    def log(self, message: str, level: str = 'INFO'):
        """
        添加日志
        
        Args:
            message: 日志消息
            level: 日志级别
        """
        from datetime import datetime
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_line = f"[{timestamp}] [{level}] {message}\n"
        
        # 启用编辑
        self.configure(state="normal")
        
        # 添加日志
        self.insert("end", log_line, level)
        
        # 限制行数
        lines = int(self.index('end-1c').split('.')[0])
        if lines > self.max_lines:
            self.delete("1.0", f"{lines - self.max_lines}.0")
        
        # 滚动到底部
        self.see("end")
        
        # 禁用编辑
        self.configure(state="disabled")
    
    def info(self, message: str):
        """信息日志"""
        self.log(message, 'INFO')
    
    def warning(self, message: str):
        """警告日志"""
        self.log(message, 'WARNING')
    
    def error(self, message: str):
        """错误日志"""
        self.log(message, 'ERROR')
    
    def success(self, message: str):
        """成功日志"""
        self.log(message, 'SUCCESS')
    
    def debug(self, message: str):
        """调试日志"""
        self.log(message, 'DEBUG')
    
    def clear_logs(self):
        """清空日志"""
        self.configure(state="normal")
        self.delete("0.0", "end")
        self.configure(state="disabled")

# 导出
__all__ = [
    'CyberTextbox',
    'CyberCodeEditor',
    'CyberLogViewer',
]