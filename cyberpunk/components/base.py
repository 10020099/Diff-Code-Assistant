"""
赛博朋克UI组件基类
为所有自定义组件提供统一的基础功能
"""

import customtkinter as ctk
from typing import Optional, Dict, Any, Callable
from ..theme import get_theme, CyberpunkTheme
from ..colors import NEON_CYAN

class CyberWidgetBase:
    """
    赛博朋克组件基类
    提供统一的样式应用和事件处理
    """
    
    def __init__(self, theme: Optional[CyberpunkTheme] = None):
        """
        初始化基类
        
        Args:
            theme: 主题实例,如果为None则使用默认主题
        """
        self.theme = theme or get_theme()
        self._hover_bindings = []
        self._animation_running = False
    
    def apply_hover_effect(self, widget: ctk.CTkBaseClass, 
                          hover_color: Optional[str] = None):
        """
        应用悬停效果
        
        Args:
            widget: 要应用效果的组件
            hover_color: 悬停时的颜色,如果为None则自动计算
        """
        original_color = widget.cget("fg_color")
        hover_col = hover_color or self._lighten_color(original_color)
        
        def on_enter(e):
            widget.configure(fg_color=hover_col)
        
        def on_leave(e):
            widget.configure(fg_color=original_color)
        
        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)
        
        self._hover_bindings.append((widget, on_enter, on_leave))
    
    def apply_glow_effect(self, widget: ctk.CTkBaseClass, 
                         glow_color: str = NEON_CYAN):
        """
        应用发光效果(通过边框模拟)
        
        Args:
            widget: 要应用效果的组件
            glow_color: 发光颜色
        """
        try:
            widget.configure(
                border_width=2,
                border_color=glow_color
            )
        except:
            pass  # 某些组件可能不支持边框
    
    def animate_opacity(self, widget: ctk.CTkBaseClass, 
                       from_alpha: float, to_alpha: float,
                       duration: int = 300, callback: Optional[Callable] = None):
        """
        透明度动画(简化版,CustomTkinter支持有限)
        
        Args:
            widget: 要动画的组件
            from_alpha: 起始透明度
            to_alpha: 结束透明度
            duration: 持续时间(毫秒)
            callback: 完成回调
        """
        # CustomTkinter不直接支持透明度动画
        # 这里提供一个接口,实际效果有限
        if callback:
            widget.after(duration, callback)
    
    def cleanup(self):
        """清理资源"""
        # 解绑所有悬停事件
        for widget, on_enter, on_leave in self._hover_bindings:
            try:
                widget.unbind("<Enter>")
                widget.unbind("<Leave>")
            except:
                pass
        self._hover_bindings.clear()
    
    @staticmethod
    def _lighten_color(color: str, amount: float = 0.1) -> str:
        """使颜色变亮"""
        if not color or color == "transparent":
            return color
        
        # 简单的颜色变亮算法
        if color.startswith("#"):
            try:
                r = int(color[1:3], 16)
                g = int(color[3:5], 16)
                b = int(color[5:7], 16)
                
                r = min(255, int(r + (255 - r) * amount))
                g = min(255, int(g + (255 - g) * amount))
                b = min(255, int(b + (255 - b) * amount))
                
                return f"#{r:02x}{g:02x}{b:02x}"
            except:
                return color
        return color

class CyberButtonBase(ctk.CTkButton, CyberWidgetBase):
    """赛博朋克按钮基类"""
    
    def __init__(self, master, theme: Optional[CyberpunkTheme] = None, 
                 variant: str = 'primary', **kwargs):
        """
        初始化按钮
        
        Args:
            master: 父组件
            theme: 主题实例
            variant: 按钮变体
            **kwargs: 其他参数
        """
        CyberWidgetBase.__init__(self, theme)
        
        # 获取样式
        style = self.theme.get_button_style(variant)
        
        # 合并样式和用户参数
        merged_kwargs = {**style, **kwargs}
        
        # 移除font参数(如果存在),因为可能导致问题
        merged_kwargs.pop('font', None)
        
        ctk.CTkButton.__init__(self, master, **merged_kwargs)

class CyberFrameBase(ctk.CTkFrame, CyberWidgetBase):
    """赛博朋克框架基类"""
    
    def __init__(self, master, theme: Optional[CyberpunkTheme] = None,
                 variant: str = 'default', **kwargs):
        """
        初始化框架
        
        Args:
            master: 父组件
            theme: 主题实例
            variant: 框架变体
            **kwargs: 其他参数
        """
        CyberWidgetBase.__init__(self, theme)
        
        # 获取样式
        style = self.theme.get_frame_style(variant)
        
        # 合并样式和用户参数
        merged_kwargs = {**style, **kwargs}
        
        ctk.CTkFrame.__init__(self, master, **merged_kwargs)

class CyberEntryBase(ctk.CTkEntry, CyberWidgetBase):
    """赛博朋克输入框基类"""
    
    def __init__(self, master, theme: Optional[CyberpunkTheme] = None, **kwargs):
        """
        初始化输入框
        
        Args:
            master: 父组件
            theme: 主题实例
            **kwargs: 其他参数
        """
        CyberWidgetBase.__init__(self, theme)
        
        # 获取样式
        style = self.theme.get_entry_style()
        
        # 合并样式和用户参数
        merged_kwargs = {**style, **kwargs}
        merged_kwargs.pop('font', None)
        
        ctk.CTkEntry.__init__(self, master, **merged_kwargs)

class CyberLabelBase(ctk.CTkLabel, CyberWidgetBase):
    """赛博朋克标签基类"""
    
    def __init__(self, master, theme: Optional[CyberpunkTheme] = None,
                 variant: str = 'normal', **kwargs):
        """
        初始化标签
        
        Args:
            master: 父组件
            theme: 主题实例
            variant: 标签变体
            **kwargs: 其他参数
        """
        CyberWidgetBase.__init__(self, theme)
        
        # 获取样式
        style = self.theme.get_label_style(variant)
        
        # 合并样式和用户参数
        merged_kwargs = {**style, **kwargs}
        merged_kwargs.pop('font', None)
        
        ctk.CTkLabel.__init__(self, master, **merged_kwargs)

# 便捷导出
__all__ = [
    'CyberWidgetBase',
    'CyberButtonBase',
    'CyberFrameBase',
    'CyberEntryBase',
    'CyberLabelBase',
]