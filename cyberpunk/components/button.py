"""
赛博朋克按钮组件
提供各种样式变体的按钮
"""

import customtkinter as ctk
from typing import Optional, Callable, Any
from .base import CyberButtonBase
from ..theme import CyberpunkTheme, Dimensions

class CyberButton(CyberButtonBase):
    """
    赛博朋克风格按钮
    
    支持的变体:
    - primary: 主要按钮
    - secondary: 次要按钮
    - success: 成功按钮
    - danger: 危险按钮
    - ghost: 幽灵按钮(透明背景)
    """
    
    def __init__(self, 
                 master,
                 text: str = "Button",
                 command: Optional[Callable] = None,
                 variant: str = 'primary',
                 theme: Optional[CyberpunkTheme] = None,
                 with_glow: bool = True,
                 **kwargs):
        """
        初始化赛博朋克按钮
        
        Args:
            master: 父组件
            text: 按钮文本
            command: 点击回调函数
            variant: 按钮变体 ('primary', 'secondary', 'success', 'danger', 'ghost')
            theme: 主题实例
            with_glow: 是否添加发光效果
            **kwargs: 其他CTkButton参数
        """
        # 初始化基类
        super().__init__(
            master=master,
            text=text,
            command=command,
            theme=theme,
            variant=variant,
            **kwargs
        )
        
        # 保存参数
        self.variant = variant
        self.with_glow = with_glow
        
        # 应用额外效果
        if with_glow and variant != 'ghost':
            border_color = self.theme.color_scheme['primary']
            if variant == 'success':
                border_color = self.theme.color_scheme['success']
            elif variant == 'danger':
                border_color = self.theme.color_scheme['error']
            
            self.apply_glow_effect(self, border_color)
    
    def set_loading(self, loading: bool = True):
        """
        设置加载状态
        
        Args:
            loading: 是否加载中
        """
        if loading:
            self.configure(state="disabled", text="Loading...")
        else:
            self.configure(state="normal")
    
    def pulse(self):
        """脉冲动画效果(简化版)"""
        original_width = self.cget("border_width")
        
        def animate(step=0):
            if step < 4:
                width = original_width + (2 if step % 2 == 0 else 0)
                self.configure(border_width=width)
                self.after(100, lambda: animate(step + 1))
            else:
                self.configure(border_width=original_width)
        
        animate()

class CyberIconButton(CyberButton):
    """
    带图标的赛博朋克按钮
    """
    
    def __init__(self,
                 master,
                 text: str = "",
                 icon: str = "⚡",
                 command: Optional[Callable] = None,
                 variant: str = 'primary',
                 theme: Optional[CyberpunkTheme] = None,
                 icon_position: str = 'left',
                 **kwargs):
        """
        初始化图标按钮
        
        Args:
            master: 父组件
            text: 按钮文本
            icon: 图标字符
            command: 点击回调
            variant: 按钮变体
            theme: 主题实例
            icon_position: 图标位置 ('left', 'right', 'top', 'bottom')
            **kwargs: 其他参数
        """
        # 根据位置组合文本
        if icon_position == 'left':
            display_text = f"{icon} {text}" if text else icon
        elif icon_position == 'right':
            display_text = f"{text} {icon}" if text else icon
        elif icon_position == 'top':
            display_text = f"{icon}\n{text}" if text else icon
        else:  # bottom
            display_text = f"{text}\n{icon}" if text else icon
        
        super().__init__(
            master=master,
            text=display_text,
            command=command,
            variant=variant,
            theme=theme,
            **kwargs
        )
        
        self.icon = icon
        self.original_text = text
        self.icon_position = icon_position
    
    def set_icon(self, new_icon: str):
        """
        更换图标
        
        Args:
            new_icon: 新图标
        """
        self.icon = new_icon
        self._update_text()
    
    def set_text(self, new_text: str):
        """
        更换文本
        
        Args:
            new_text: 新文本
        """
        self.original_text = new_text
        self._update_text()
    
    def _update_text(self):
        """更新显示文本"""
        text = self.original_text
        icon = self.icon
        
        if self.icon_position == 'left':
            display_text = f"{icon} {text}" if text else icon
        elif self.icon_position == 'right':
            display_text = f"{text} {icon}" if text else icon
        elif self.icon_position == 'top':
            display_text = f"{icon}\n{text}" if text else icon
        else:  # bottom
            display_text = f"{text}\n{icon}" if text else icon
        
        self.configure(text=display_text)

class CyberToggleButton(CyberButton):
    """
    开关按钮
    """
    
    def __init__(self,
                 master,
                 text_on: str = "ON",
                 text_off: str = "OFF",
                 command: Optional[Callable] = None,
                 theme: Optional[CyberpunkTheme] = None,
                 initial_state: bool = False,
                 **kwargs):
        """
        初始化开关按钮
        
        Args:
            master: 父组件
            text_on: 开启时文本
            text_off: 关闭时文本
            command: 点击回调(接收当前状态作为参数)
            theme: 主题实例
            initial_state: 初始状态
            **kwargs: 其他参数
        """
        self.text_on = text_on
        self.text_off = text_off
        self.user_command = command
        self.is_on = initial_state
        
        # 根据初始状态选择变体
        variant = 'success' if initial_state else 'secondary'
        text = text_on if initial_state else text_off
        
        super().__init__(
            master=master,
            text=text,
            command=self._toggle,
            variant=variant,
            theme=theme,
            **kwargs
        )
    
    def _toggle(self):
        """切换状态"""
        self.is_on = not self.is_on
        
        # 更新外观
        if self.is_on:
            self.configure(text=self.text_on)
            style = self.theme.get_button_style('success')
        else:
            self.configure(text=self.text_off)
            style = self.theme.get_button_style('secondary')
        
        # 应用新样式(移除font)
        style.pop('font', None)
        self.configure(**style)
        
        # 调用用户回调
        if self.user_command:
            self.user_command(self.is_on)
    
    def set_state(self, state: bool):
        """
        设置状态
        
        Args:
            state: 新状态
        """
        if state != self.is_on:
            self._toggle()
    
    def get_state(self) -> bool:
        """获取当前状态"""
        return self.is_on

# 导出
__all__ = [
    'CyberButton',
    'CyberIconButton',
    'CyberToggleButton',
]