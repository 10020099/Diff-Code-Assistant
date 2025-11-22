"""
赛博朋克进度条组件
提供各种进度显示组件
"""

import customtkinter as ctk
from typing import Optional
from ..theme import CyberpunkTheme, Dimensions

class CyberProgressBar(ctk.CTkProgressBar):
    """
    赛博朋克风格进度条
    """
    
    def __init__(self,
                 master,
                 theme: Optional[CyberpunkTheme] = None,
                 mode: str = 'determinate',
                 show_percentage: bool = False,
                 **kwargs):
        """
        初始化进度条
        
        Args:
            master: 父组件
            theme: 主题实例
            mode: 模式 ('determinate' 确定, 'indeterminate' 不确定)
            show_percentage: 是否显示百分比
            **kwargs: 其他CTkProgressBar参数
        """
        self.theme = theme or CyberpunkTheme()
        
        # 获取样式
        style = self.theme.get_progressbar_style()
        merged_kwargs = {**style, **kwargs}
        
        super().__init__(master, **merged_kwargs)
        
        self.mode = mode
        self.show_percentage = show_percentage
        self._current_value = 0
        self._animation_running = False
        
        # 百分比标签
        if show_percentage:
            self.percentage_label = ctk.CTkLabel(
                master,
                text="0%",
                font=("Arial", 10),
                text_color=self.theme.color_scheme['text_secondary']
            )
    
    def set_value(self, value: float):
        """
        设置进度值
        
        Args:
            value: 进度值 (0.0-1.0)
        """
        self._current_value = max(0.0, min(1.0, value))
        self.set(self._current_value)
        
        if self.show_percentage:
            percentage = int(self._current_value * 100)
            self.percentage_label.configure(text=f"{percentage}%")
    
    def start_indeterminate(self):
        """开始不确定模式动画"""
        if self._animation_running:
            return
        
        self._animation_running = True
        self.mode = 'indeterminate'
        self.start()
    
    def stop_indeterminate(self):
        """停止不确定模式动画"""
        if not self._animation_running:
            return
        
        self._animation_running = False
        self.stop()
        self.set(0)
    
    def animate_to(self, target: float, duration: int = 500):
        """
        动画过渡到目标值
        
        Args:
            target: 目标值 (0.0-1.0)
            duration: 持续时间(毫秒)
        """
        steps = 20
        delay = duration // steps
        start = self._current_value
        diff = target - start
        step_value = diff / steps
        
        def animate(step=0):
            if step < steps:
                new_value = start + (step_value * step)
                self.set_value(new_value)
                self.after(delay, lambda: animate(step + 1))
            else:
                self.set_value(target)
        
        animate()

class CyberCircularProgress(ctk.CTkFrame):
    """
    圆形进度条 (简化实现)
    """
    
    def __init__(self,
                 master,
                 size: int = 100,
                 theme: Optional[CyberpunkTheme] = None,
                 **kwargs):
        """
        初始化圆形进度条
        
        Args:
            master: 父组件
            size: 尺寸
            theme: 主题实例
            **kwargs: 其他参数
        """
        self.theme = theme or CyberpunkTheme()
        
        super().__init__(
            master,
            width=size,
            height=size,
            fg_color="transparent",
            **kwargs
        )
        
        self.size = size
        self._value = 0
        
        # 使用标签模拟(CustomTkinter不原生支持圆形进度)
        self.label = ctk.CTkLabel(
            self,
            text="0%",
            font=("Arial", int(size * 0.2), "bold"),
            text_color=self.theme.color_scheme['primary']
        )
        self.label.place(relx=0.5, rely=0.5, anchor="center")
        
        # 背景圆
        self.bg_circle = ctk.CTkProgressBar(
            self,
            width=size - 20,
            height=10,
            corner_radius=size
        )
        self.bg_circle.place(relx=0.5, rely=0.5, anchor="center")
    
    def set_value(self, value: float):
        """
        设置进度值
        
        Args:
            value: 进度值 (0.0-1.0)
        """
        self._value = max(0.0, min(1.0, value))
        percentage = int(self._value * 100)
        self.label.configure(text=f"{percentage}%")
        self.bg_circle.set(self._value)

class CyberLoadingSpinner(ctk.CTkFrame):
    """
    加载旋转器
    """
    
    def __init__(self,
                 master,
                 size: int = 50,
                 theme: Optional[CyberpunkTheme] = None,
                 **kwargs):
        """
        初始化加载旋转器
        
        Args:
            master: 父组件
            size: 尺寸
            theme: 主题实例
            **kwargs: 其他参数
        """
        self.theme = theme or CyberpunkTheme()
        
        super().__init__(
            master,
            width=size,
            height=size,
            fg_color="transparent",
            **kwargs
        )
        
        self.size = size
        self._running = False
        self._rotation = 0
        
        # 使用进度条模拟旋转
        self.spinner = ctk.CTkProgressBar(
            self,
            width=size,
            mode="indeterminate"
        )
        self.spinner.place(relx=0.5, rely=0.5, anchor="center")
    
    def start(self):
        """开始旋转"""
        if not self._running:
            self._running = True
            self.spinner.start()
    
    def stop(self):
        """停止旋转"""
        if self._running:
            self._running = False
            self.spinner.stop()

# 导出
__all__ = [
    'CyberProgressBar',
    'CyberCircularProgress',
    'CyberLoadingSpinner',
]