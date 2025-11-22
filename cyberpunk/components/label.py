"""
赛博朋克标签组件
提供各种文本显示组件
"""

import customtkinter as ctk
from typing import Optional
from .base import CyberLabelBase
from ..theme import CyberpunkTheme
from ..colors import NEON_CYAN

class CyberLabel(CyberLabelBase):
    """
    赛博朋克风格标签
    
    支持的变体:
    - normal: 普通文本
    - title: 标题文本
    - subtitle: 副标题
    - caption: 说明文字
    - highlight: 高亮文本
    """
    
    def __init__(self,
                 master,
                 text: str = "",
                 variant: str = 'normal',
                 theme: Optional[CyberpunkTheme] = None,
                 animated: bool = False,
                 **kwargs):
        """
        初始化标签
        
        Args:
            master: 父组件
            text: 标签文本
            variant: 标签变体
            theme: 主题实例
            animated: 是否启用动画效果
            **kwargs: 其他CTkLabel参数
        """
        super().__init__(
            master=master,
            text=text,
            theme=theme,
            variant=variant,
            **kwargs
        )
        
        self.variant = variant
        self.animated = animated
        self._animation_id = None
    
    def set_variant(self, variant: str):
        """
        更改标签变体
        
        Args:
            variant: 新变体
        """
        self.variant = variant
        style = self.theme.get_label_style(variant)
        style.pop('font', None)
        self.configure(**style)
    
    def pulse_animation(self, duration: int = 1000):
        """
        脉冲动画效果
        
        Args:
            duration: 持续时间(毫秒)
        """
        if not self.animated:
            return
        
        original_color = self.cget("text_color")
        highlight_color = self.theme.color_scheme['primary']
        
        def animate(step=0):
            if step < 4:
                color = highlight_color if step % 2 == 0 else original_color
                self.configure(text_color=color)
                self._animation_id = self.after(duration // 4, lambda: animate(step + 1))
            else:
                self.configure(text_color=original_color)
                self._animation_id = None
        
        animate()
    
    def stop_animation(self):
        """停止动画"""
        if self._animation_id:
            self.after_cancel(self._animation_id)
            self._animation_id = None

class CyberBadge(CyberLabel):
    """
    徽章标签
    用于显示状态或计数
    """
    
    def __init__(self,
                 master,
                 text: str = "0",
                 badge_type: str = 'info',
                 theme: Optional[CyberpunkTheme] = None,
                 **kwargs):
        """
        初始化徽章
        
        Args:
            master: 父组件
            text: 徽章文本
            badge_type: 徽章类型 ('info', 'success', 'warning', 'error')
            theme: 主题实例
            **kwargs: 其他参数
        """
        self.badge_type = badge_type
        theme = theme or CyberpunkTheme()
        
        # 根据类型选择颜色
        colors = {
            'info': theme.color_scheme['info'],
            'success': theme.color_scheme['success'],
            'warning': theme.color_scheme['warning'],
            'error': theme.color_scheme['error'],
        }
        
        fg_color = colors.get(badge_type, colors['info'])
        
        super().__init__(
            master=master,
            text=text,
            variant='caption',
            theme=theme,
            fg_color=fg_color,
            corner_radius=10,
            width=40,
            height=20,
            **kwargs
        )
    
    def set_count(self, count: int):
        """
        设置计数
        
        Args:
            count: 计数值
        """
        self.configure(text=str(count))
    
    def set_type(self, badge_type: str):
        """
        更改徽章类型
        
        Args:
            badge_type: 新类型
        """
        self.badge_type = badge_type
        colors = {
            'info': self.theme.color_scheme['info'],
            'success': self.theme.color_scheme['success'],
            'warning': self.theme.color_scheme['warning'],
            'error': self.theme.color_scheme['error'],
        }
        self.configure(fg_color=colors.get(badge_type, colors['info']))

class CyberStatusLabel(CyberLabel):
    """
    状态标签
    显示实时状态信息
    """
    
    def __init__(self,
                 master,
                 status: str = "Ready",
                 theme: Optional[CyberpunkTheme] = None,
                 **kwargs):
        """
        初始化状态标签
        
        Args:
            master: 父组件
            status: 初始状态
            theme: 主题实例
            **kwargs: 其他参数
        """
        super().__init__(
            master=master,
            text=f"● {status}",
            variant='normal',
            theme=theme,
            **kwargs
        )
        
        self.current_status = status
        self.status_colors = {
            'ready': self.theme.color_scheme['success'],
            'working': self.theme.color_scheme['primary'],
            'error': self.theme.color_scheme['error'],
            'warning': self.theme.color_scheme['warning'],
            'idle': self.theme.color_scheme['text_secondary'],
        }
    
    def set_status(self, status: str, status_type: str = 'ready'):
        """
        设置状态
        
        Args:
            status: 状态文本
            status_type: 状态类型 ('ready', 'working', 'error', 'warning', 'idle')
        """
        self.current_status = status
        self.configure(
            text=f"● {status}",
            text_color=self.status_colors.get(status_type, self.status_colors['ready'])
        )
    
    def set_ready(self, text: str = "Ready"):
        """设置为就绪状态"""
        self.set_status(text, 'ready')
    
    def set_working(self, text: str = "Working..."):
        """设置为工作状态"""
        self.set_status(text, 'working')
    
    def set_error(self, text: str = "Error"):
        """设置为错误状态"""
        self.set_status(text, 'error')
    
    def set_warning(self, text: str = "Warning"):
        """设置为警告状态"""
        self.set_status(text, 'warning')

class CyberLinkLabel(CyberLabel):
    """
    链接样式标签
    可点击的文本标签
    """
    
    def __init__(self,
                 master,
                 text: str = "Link",
                 command: Optional[callable] = None,
                 theme: Optional[CyberpunkTheme] = None,
                 **kwargs):
        """
        初始化链接标签
        
        Args:
            master: 父组件
            text: 链接文本
            command: 点击回调
            theme: 主题实例
            **kwargs: 其他参数
        """
        super().__init__(
            master=master,
            text=text,
            variant='highlight',
            theme=theme,
            cursor="hand2",
            **kwargs
        )
        
        self.command = command
        self.original_color = self.cget("text_color")
        self.hover_color = self.theme.color_scheme['primary']
        
        # 绑定事件
        self.bind("<Button-1>", self._on_click)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
    
    def _on_click(self, event):
        """点击事件"""
        if self.command:
            self.command()
    
    def _on_enter(self, event):
        """鼠标进入"""
        self.configure(text_color=self.hover_color)
    
    def _on_leave(self, event):
        """鼠标离开"""
        self.configure(text_color=self.original_color)

# 导出
__all__ = [
    'CyberLabel',
    'CyberBadge',
    'CyberStatusLabel',
    'CyberLinkLabel',
]