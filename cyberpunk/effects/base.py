"""
特效基类模块

提供所有特效的基础类和通用功能。
"""

from abc import ABC, abstractmethod
from typing import Optional, Callable, Any
import customtkinter as ctk


class EffectBase(ABC):
    """
    特效基类
    
    所有特效都应继承此类并实现必要的抽象方法。
    
    属性:
        parent: 父组件
        enabled: 特效是否启用
        running: 特效是否正在运行
    """
    
    def __init__(
        self,
        parent: ctk.CTkBaseClass,
        enabled: bool = True
    ):
        """
        初始化特效
        
        参数:
            parent: 父组件
            enabled: 是否立即启用
        """
        self.parent = parent
        self._enabled = enabled
        self._running = False
        self._animation_id: Optional[str] = None
        
    @property
    def enabled(self) -> bool:
        """获取特效启用状态"""
        return self._enabled
    
    @enabled.setter
    def enabled(self, value: bool) -> None:
        """设置特效启用状态"""
        self._enabled = value
        if not value and self._running:
            self.stop()
    
    @property
    def running(self) -> bool:
        """获取特效运行状态"""
        return self._running
    
    @abstractmethod
    def start(self) -> None:
        """启动特效"""
        pass
    
    @abstractmethod
    def stop(self) -> None:
        """停止特效"""
        pass
    
    @abstractmethod
    def update(self) -> None:
        """更新特效状态"""
        pass
    
    def toggle(self) -> None:
        """切换特效运行状态"""
        if self._running:
            self.stop()
        else:
            self.start()
    
    def reset(self) -> None:
        """重置特效到初始状态"""
        was_running = self._running
        self.stop()
        if was_running:
            self.start()


class AnimatedEffect(EffectBase):
    """
    动画特效基类
    
    提供基于帧的动画循环功能。
    
    属性:
        fps: 帧率
        frame_time: 每帧时间(毫秒)
    """
    
    def __init__(
        self,
        parent: ctk.CTkBaseClass,
        fps: int = 60,
        enabled: bool = True
    ):
        """
        初始化动画特效
        
        参数:
            parent: 父组件
            fps: 目标帧率
            enabled: 是否立即启用
        """
        super().__init__(parent, enabled)
        self.fps = fps
        self.frame_time = int(1000 / fps)
        self._frame_count = 0
    
    def start(self) -> None:
        """启动动画循环"""
        if not self._enabled:
            return
        
        self._running = True
        self._frame_count = 0
        self._animate()
    
    def stop(self) -> None:
        """停止动画循环"""
        self._running = False
        if self._animation_id:
            self.parent.after_cancel(self._animation_id)
            self._animation_id = None
    
    def _animate(self) -> None:
        """内部动画循环"""
        if not self._running:
            return
        
        self.update()
        self._frame_count += 1
        
        self._animation_id = self.parent.after(
            self.frame_time,
            self._animate
        )
    
    @abstractmethod
    def update(self) -> None:
        """更新动画帧"""
        pass


class CanvasEffect(AnimatedEffect):
    """
    基于Canvas的特效基类
    
    提供Canvas绘制功能的特效基类。
    
    属性:
        canvas: Canvas组件
    """
    
    def __init__(
        self,
        parent: ctk.CTkBaseClass,
        fps: int = 60,
        enabled: bool = True,
        canvas: Optional[ctk.CTkCanvas] = None
    ):
        """
        初始化Canvas特效
        
        参数:
            parent: 父组件
            fps: 目标帧率
            enabled: 是否立即启用
            canvas: 自定义Canvas(可选)
        """
        super().__init__(parent, fps, enabled)
        
        if canvas is None:
            self.canvas = self._create_canvas()
        else:
            self.canvas = canvas
    
    def _create_canvas(self) -> ctk.CTkCanvas:
        """创建默认Canvas"""
        canvas = ctk.CTkCanvas(
            self.parent,
            bg='black',
            highlightthickness=0
        )
        canvas.place(relx=0, rely=0, relwidth=1, relheight=1)
        return canvas
    
    def clear_canvas(self) -> None:
        """清空Canvas"""
        self.canvas.delete('all')
    
    @abstractmethod
    def draw(self) -> None:
        """绘制特效"""
        pass
    
    def update(self) -> None:
        """更新并绘制"""
        self.draw()


class WidgetEffect(EffectBase):
    """
    组件特效基类
    
    作用于单个组件的特效。
    
    属性:
        target: 目标组件
    """
    
    def __init__(
        self,
        target: ctk.CTkBaseClass,
        enabled: bool = True
    ):
        """
        初始化组件特效
        
        参数:
            target: 目标组件
            enabled: 是否立即启用
        """
        super().__init__(target, enabled)
        self.target = target
    
    @abstractmethod
    def apply(self) -> None:
        """应用特效到目标组件"""
        pass
    
    @abstractmethod
    def remove(self) -> None:
        """从目标组件移除特效"""
        pass
    
    def start(self) -> None:
        """启动特效"""
        if not self._enabled:
            return
        
        self._running = True
        self.apply()
    
    def stop(self) -> None:
        """停止特效"""
        self._running = False
        self.remove()


# 导出所有类
__all__ = [
    'EffectBase',
    'AnimatedEffect',
    'CanvasEffect',
    'WidgetEffect',
]