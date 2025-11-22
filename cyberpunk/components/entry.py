"""
赛博朋克输入框组件
提供增强的输入框功能
"""

import customtkinter as ctk
import tkinter as tk
from typing import Optional, Callable
from .base import CyberEntryBase
from ..theme import CyberpunkTheme

class CyberEntry(CyberEntryBase):
    """
    赛博朋克风格输入框
    """
    
    def __init__(self,
                 master,
                 placeholder_text: str = "",
                 theme: Optional[CyberpunkTheme] = None,
                 with_glow: bool = True,
                 validate_func: Optional[Callable[[str], bool]] = None,
                 **kwargs):
        """
        初始化输入框
        
        Args:
            master: 父组件
            placeholder_text: 占位符文本
            theme: 主题实例
            with_glow: 是否添加发光效果
            validate_func: 验证函数,接收文本返回是否有效
            **kwargs: 其他CTkEntry参数
        """
        super().__init__(
            master=master,
            placeholder_text=placeholder_text,
            theme=theme,
            **kwargs
        )
        
        self.validate_func = validate_func
        self.with_glow = with_glow
        
        # 应用发光效果
        if with_glow:
            self.apply_glow_effect(self, self.theme.color_scheme['primary'])
        
        # 绑定验证事件
        if validate_func:
            self.bind("<KeyRelease>", self._on_text_change)
    
    def _on_text_change(self, event):
        """文本改变时验证"""
        if self.validate_func:
            text = self.get()
            is_valid = self.validate_func(text)
            
            # 根据验证结果改变边框颜色
            if is_valid:
                border_color = self.theme.color_scheme['success']
            else:
                border_color = self.theme.color_scheme['error']
            
            self.configure(border_color=border_color)
    
    def set_error(self, has_error: bool = True):
        """
        设置错误状态
        
        Args:
            has_error: 是否有错误
        """
        if has_error:
            self.configure(border_color=self.theme.color_scheme['error'])
        else:
            self.configure(border_color=self.theme.color_scheme['border'])
    
    def clear(self):
        """清空输入框"""
        self.delete(0, "end")
    
    def set_text(self, text: str):
        """
        设置文本
        
        Args:
            text: 要设置的文本
        """
        self.clear()
        self.insert(0, text)

class CyberPasswordEntry(CyberEntry):
    """密码输入框"""
    
    def __init__(self,
                 master,
                 placeholder_text: str = "Password",
                 theme: Optional[CyberpunkTheme] = None,
                 show_toggle: bool = True,
                 **kwargs):
        """
        初始化密码输入框
        
        Args:
            master: 父组件
            placeholder_text: 占位符文本
            theme: 主题实例
            show_toggle: 是否显示切换按钮
            **kwargs: 其他参数
        """
        super().__init__(
            master=master,
            placeholder_text=placeholder_text,
            theme=theme,
            show="•",
            **kwargs
        )
        
        self.show_toggle = show_toggle
        self.is_visible = False
        
        if show_toggle:
            self._create_toggle_button()
    
    def _create_toggle_button(self):
        """创建显示/隐藏切换按钮"""
        # 注意:这里简化实现,实际应该使用overlay或特殊布局
        # CustomTkinter的Entry不直接支持按钮集成
        pass
    
    def toggle_visibility(self):
        """切换密码可见性"""
        if self.is_visible:
            self.configure(show="•")
        else:
            self.configure(show="")
        self.is_visible = not self.is_visible

class CyberSearchEntry(CyberEntry):
    """搜索输入框"""
    
    def __init__(self,
                 master,
                 placeholder_text: str = "Search...",
                 search_callback: Optional[Callable[[str], None]] = None,
                 theme: Optional[CyberpunkTheme] = None,
                 **kwargs):
        """
        初始化搜索输入框
        
        Args:
            master: 父组件
            placeholder_text: 占位符文本
            search_callback: 搜索回调函数
            theme: 主题实例
            **kwargs: 其他参数
        """
        super().__init__(
            master=master,
            placeholder_text=placeholder_text,
            theme=theme,
            **kwargs
        )
        
        self.search_callback = search_callback
        self._search_timer = None
        
        # 绑定搜索事件(延迟搜索)
        self.bind("<KeyRelease>", self._on_search_change)
        self.bind("<Return>", self._on_search_enter)
    
    def _on_search_change(self, event):
        """文本改变时延迟搜索"""
        if self._search_timer:
            self.after_cancel(self._search_timer)
        
        # 延迟300ms执行搜索
        self._search_timer = self.after(300, self._do_search)
    
    def _on_search_enter(self, event):
        """按回车立即搜索"""
        if self._search_timer:
            self.after_cancel(self._search_timer)
        self._do_search()
    
    def _do_search(self):
        """执行搜索"""
        if self.search_callback:
            text = self.get()
            self.search_callback(text)

class CyberNumberEntry(CyberEntry):
    """数字输入框"""
    
    def __init__(self,
                 master,
                 min_value: Optional[float] = None,
                 max_value: Optional[float] = None,
                 decimal_places: int = 0,
                 theme: Optional[CyberpunkTheme] = None,
                 **kwargs):
        """
        初始化数字输入框
        
        Args:
            master: 父组件
            min_value: 最小值
            max_value: 最大值
            decimal_places: 小数位数(0表示整数)
            theme: 主题实例
            **kwargs: 其他参数
        """
        self.min_value = min_value
        self.max_value = max_value
        self.decimal_places = decimal_places
        
        super().__init__(
            master=master,
            theme=theme,
            validate_func=self._validate_number,
            **kwargs
        )
        
        # 只允许输入数字和小数点
        self.bind("<KeyPress>", self._on_key_press)
    
    def _on_key_press(self, event):
        """按键过滤"""
        char = event.char
        
        # 允许控制字符
        if event.keysym in ['BackSpace', 'Delete', 'Left', 'Right', 'Home', 'End']:
            return
        
        # 允许数字
        if char.isdigit():
            return
        
        # 允许小数点(如果设置了小数位)
        if char == '.' and self.decimal_places > 0:
            current_text = self.get()
            if '.' not in current_text:
                return
        
        # 允许负号(在开头)
        if char == '-':
            current_text = self.get()
            if len(current_text) == 0 or self.index(tk.INSERT) == 0:
                return
        
        # 阻止其他字符
        return "break"
    
    def _validate_number(self, text: str) -> bool:
        """验证数字"""
        if not text:
            return True
        
        try:
            value = float(text)
            
            # 检查范围
            if self.min_value is not None and value < self.min_value:
                return False
            if self.max_value is not None and value > self.max_value:
                return False
            
            return True
        except ValueError:
            return False
    
    def get_number(self) -> Optional[float]:
        """
        获取数字值
        
        Returns:
            数字值,如果无效返回None
        """
        text = self.get()
        try:
            return float(text) if text else None
        except ValueError:
            return None
    
    def set_number(self, value: float):
        """
        设置数字值
        
        Args:
            value: 数字值
        """
        if self.decimal_places == 0:
            text = str(int(value))
        else:
            text = f"{value:.{self.decimal_places}f}"
        
        self.set_text(text)

# 导出
__all__ = [
    'CyberEntry',
    'CyberPasswordEntry',
    'CyberSearchEntry',
    'CyberNumberEntry',
]