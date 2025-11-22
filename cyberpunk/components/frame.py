"""
赛博朋克框架组件
提供各种容器框架
"""

import customtkinter as ctk
from typing import Optional
from .base import CyberFrameBase
from ..theme import CyberpunkTheme

class CyberFrame(CyberFrameBase):
    """
    赛博朋克风格框架
    
    支持的变体:
    - default: 默认框架
    - card: 卡片样式
    - panel: 面板样式
    - highlight: 高亮框架
    """
    
    def __init__(self,
                 master,
                 variant: str = 'default',
                 theme: Optional[CyberpunkTheme] = None,
                 with_glow: bool = False,
                 **kwargs):
        """
        初始化框架
        
        Args:
            master: 父组件
            variant: 框架变体
            theme: 主题实例
            with_glow: 是否添加发光边框
            **kwargs: 其他CTkFrame参数
        """
        super().__init__(
            master=master,
            theme=theme,
            variant=variant,
            **kwargs
        )
        
        self.variant = variant
        self.with_glow = with_glow
        
        # 应用发光效果
        if with_glow:
            glow_color = self.theme.color_scheme['primary']
            self.apply_glow_effect(self, glow_color)
    
    def set_variant(self, variant: str):
        """
        更改框架变体
        
        Args:
            variant: 新变体
        """
        self.variant = variant
        style = self.theme.get_frame_style(variant)
        self.configure(**style)

class CyberCard(CyberFrame):
    """
    卡片容器
    带标题和内容区域的卡片式框架
    """
    
    def __init__(self,
                 master,
                 title: str = "",
                 theme: Optional[CyberpunkTheme] = None,
                 **kwargs):
        """
        初始化卡片
        
        Args:
            master: 父组件
            title: 卡片标题
            theme: 主题实例
            **kwargs: 其他参数
        """
        super().__init__(
            master=master,
            variant='card',
            theme=theme,
            **kwargs
        )
        
        # 创建标题区域
        if title:
            self.title_frame = ctk.CTkFrame(
                self,
                fg_color="transparent"
            )
            self.title_frame.pack(fill="x", padx=10, pady=(10, 5))
            
            self.title_label = ctk.CTkLabel(
                self.title_frame,
                text=title,
                font=("Arial", 14, "bold"),
                text_color=self.theme.color_scheme['primary']
            )
            self.title_label.pack(side="left")
            
            # 分隔线
            self.separator = ctk.CTkFrame(
                self,
                height=2,
                fg_color=self.theme.color_scheme['border']
            )
            self.separator.pack(fill="x", padx=10, pady=5)
        
        # 内容区域
        self.content = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )
        self.content.pack(fill="both", expand=True, padx=10, pady=10)
    
    def set_title(self, title: str):
        """
        设置标题
        
        Args:
            title: 新标题
        """
        if hasattr(self, 'title_label'):
            self.title_label.configure(text=title)
    
    def get_content_frame(self) -> ctk.CTkFrame:
        """获取内容框架"""
        return self.content

class CyberPanel(CyberFrame):
    """
    可折叠面板
    """
    
    def __init__(self,
                 master,
                 title: str = "Panel",
                 theme: Optional[CyberpunkTheme] = None,
                 collapsible: bool = True,
                 initially_collapsed: bool = False,
                 **kwargs):
        """
        初始化面板
        
        Args:
            master: 父组件
            title: 面板标题
            theme: 主题实例
            collapsible: 是否可折叠
            initially_collapsed: 初始是否折叠
            **kwargs: 其他参数
        """
        super().__init__(
            master=master,
            variant='panel',
            theme=theme,
            **kwargs
        )
        
        self.collapsible = collapsible
        self.is_collapsed = initially_collapsed
        
        # 标题栏
        self.header = ctk.CTkFrame(
            self,
            fg_color=self.theme.color_scheme['surface'],
            corner_radius=0
        )
        self.header.pack(fill="x")
        
        # 标题文本
        self.title_label = ctk.CTkLabel(
            self.header,
            text=title,
            font=("Arial", 12, "bold"),
            text_color=self.theme.color_scheme['text_primary']
        )
        self.title_label.pack(side="left", padx=10, pady=8)
        
        # 折叠按钮
        if collapsible:
            self.toggle_btn = ctk.CTkButton(
                self.header,
                text="▼" if not initially_collapsed else "▶",
                width=30,
                height=30,
                command=self.toggle_collapse,
                fg_color="transparent",
                text_color=self.theme.color_scheme['primary']
            )
            self.toggle_btn.pack(side="right", padx=5)
        
        # 内容区域
        self.content = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )
        
        if not initially_collapsed:
            self.content.pack(fill="both", expand=True, padx=10, pady=10)
    
    def toggle_collapse(self):
        """切换折叠状态"""
        if self.is_collapsed:
            self.expand()
        else:
            self.collapse()
    
    def collapse(self):
        """折叠面板"""
        if not self.collapsible:
            return
        
        self.content.pack_forget()
        self.is_collapsed = True
        if hasattr(self, 'toggle_btn'):
            self.toggle_btn.configure(text="▶")
    
    def expand(self):
        """展开面板"""
        if not self.collapsible:
            return
        
        self.content.pack(fill="both", expand=True, padx=10, pady=10)
        self.is_collapsed = False
        if hasattr(self, 'toggle_btn'):
            self.toggle_btn.configure(text="▼")
    
    def get_content_frame(self) -> ctk.CTkFrame:
        """获取内容框架"""
        return self.content

class CyberContainer(CyberFrame):
    """
    通用容器
    提供边距和间距管理
    """
    
    def __init__(self,
                 master,
                 padding: int = 10,
                 spacing: int = 5,
                 theme: Optional[CyberpunkTheme] = None,
                 **kwargs):
        """
        初始化容器
        
        Args:
            master: 父组件
            padding: 内边距
            spacing: 子组件间距
            theme: 主题实例
            **kwargs: 其他参数
        """
        super().__init__(
            master=master,
            theme=theme,
            **kwargs
        )
        
        self.padding = padding
        self.spacing = spacing
        self.children_widgets = []
    
    def add_widget(self, widget, **pack_kwargs):
        """
        添加子组件
        
        Args:
            widget: 要添加的组件
            **pack_kwargs: pack参数
        """
        default_pack = {
            'padx': self.padding,
            'pady': self.spacing
        }
        default_pack.update(pack_kwargs)
        
        widget.pack(**default_pack)
        self.children_widgets.append(widget)
    
    def clear(self):
        """清空所有子组件"""
        for widget in self.children_widgets:
            widget.destroy()
        self.children_widgets.clear()

# 导出
__all__ = [
    'CyberFrame',
    'CyberCard',
    'CyberPanel',
    'CyberContainer',
]