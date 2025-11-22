"""
扫描线特效模块

提供经典的CRT显示器扫描线效果。
"""

from typing import Optional
import customtkinter as ctk
from .base import CanvasEffect


class ScanlineEffect(CanvasEffect):
    """
    扫描线特效
    
    模拟CRT显示器的水平扫描线效果,营造复古科幻氛围。
    
    使用示例:
        >>> scanlines = ScanlineEffect(window, line_spacing=4, opacity=0.3)
        >>> scanlines.start()
    """
    
    def __init__(
        self,
        parent: ctk.CTkBaseClass,
        line_spacing: int = 4,
        line_width: int = 1,
        opacity: float = 0.2,
        scroll_speed: float = 0.5,
        color: str = "#00ffff",
        fps: int = 60,
        enabled: bool = True,
        canvas: Optional[ctk.CTkCanvas] = None
    ):
        """
        初始化扫描线特效
        
        参数:
            parent: 父窗口
            line_spacing: 扫描线间距(像素)
            line_width: 扫描线宽度(像素)
            opacity: 透明度(0.0-1.0)
            scroll_speed: 滚动速度(像素/帧)
            color: 扫描线颜色
            fps: 帧率
            enabled: 是否启用
            canvas: 自定义Canvas
        """
        super().__init__(parent, fps, enabled, canvas)
        
        self.line_spacing = line_spacing
        self.line_width = line_width
        self.opacity = max(0.0, min(1.0, opacity))
        self.scroll_speed = scroll_speed
        self.color = color
        
        self._offset = 0.0
        self._canvas_width = 0
        self._canvas_height = 0
        
        # 绑定窗口大小变化事件
        self.canvas.bind('<Configure>', self._on_resize)
    
    def _on_resize(self, event) -> None:
        """处理窗口大小变化"""
        self._canvas_width = event.width
        self._canvas_height = event.height
        if self._running:
            self.clear_canvas()
    
    def _create_canvas(self) -> ctk.CTkCanvas:
        """创建透明Canvas"""
        canvas = ctk.CTkCanvas(
            self.parent,
            bg='black',
            highlightthickness=0
        )
        # 设置Canvas为透明
        canvas.configure(bg='')
        canvas.place(relx=0, rely=0, relwidth=1, relheight=1)
        return canvas
    
    def draw(self) -> None:
        """绘制扫描线"""
        if self._canvas_width == 0 or self._canvas_height == 0:
            self._canvas_width = self.canvas.winfo_width()
            self._canvas_height = self.canvas.winfo_height()
        
        # 清空画布
        self.clear_canvas()
        
        # 计算透明度对应的颜色
        alpha = int(self.opacity * 255)
        line_color = f"{self.color}{alpha:02x}" if len(self.color) == 7 else self.color
        
        # 绘制扫描线
        y = self._offset
        while y < self._canvas_height + self.line_spacing:
            self.canvas.create_line(
                0, y,
                self._canvas_width, y,
                fill=line_color,
                width=self.line_width,
                tags='scanline'
            )
            y += self.line_spacing
        
        # 更新偏移量实现滚动效果
        self._offset += self.scroll_speed
        if self._offset >= self.line_spacing:
            self._offset = 0.0
    
    def set_opacity(self, opacity: float) -> None:
        """
        设置透明度
        
        参数:
            opacity: 透明度(0.0-1.0)
        """
        self.opacity = max(0.0, min(1.0, opacity))
    
    def set_scroll_speed(self, speed: float) -> None:
        """
        设置滚动速度
        
        参数:
            speed: 速度(像素/帧)
        """
        self.scroll_speed = speed
    
    def set_line_spacing(self, spacing: int) -> None:
        """
        设置扫描线间距
        
        参数:
            spacing: 间距(像素)
        """
        self.line_spacing = max(1, spacing)
    
    def pause_scroll(self) -> None:
        """暂停滚动(保持扫描线显示)"""
        self.scroll_speed = 0.0
    
    def resume_scroll(self, speed: Optional[float] = None) -> None:
        """
        恢复滚动
        
        参数:
            speed: 新速度(可选,使用初始速度)
        """
        if speed is not None:
            self.scroll_speed = speed
        elif self.scroll_speed == 0.0:
            self.scroll_speed = 0.5  # 默认速度


class StaticScanlines(CanvasEffect):
    """
    静态扫描线特效
    
    不滚动的扫描线,性能更好。
    
    使用示例:
        >>> scanlines = StaticScanlines(window, line_spacing=3, opacity=0.15)
        >>> scanlines.start()
    """
    
    def __init__(
        self,
        parent: ctk.CTkBaseClass,
        line_spacing: int = 3,
        line_width: int = 1,
        opacity: float = 0.15,
        color: str = "#00ffff",
        enabled: bool = True,
        canvas: Optional[ctk.CTkCanvas] = None
    ):
        """
        初始化静态扫描线
        
        参数:
            parent: 父窗口
            line_spacing: 扫描线间距
            line_width: 扫描线宽度
            opacity: 透明度
            color: 颜色
            enabled: 是否启用
            canvas: 自定义Canvas
        """
        super().__init__(parent, 1, enabled, canvas)  # FPS=1足够
        
        self.line_spacing = line_spacing
        self.line_width = line_width
        self.opacity = max(0.0, min(1.0, opacity))
        self.color = color
        
        self._drawn = False
        self.canvas.bind('<Configure>', self._on_resize)
    
    def _on_resize(self, event) -> None:
        """处理窗口大小变化"""
        self._drawn = False
    
    def _create_canvas(self) -> ctk.CTkCanvas:
        """创建透明Canvas"""
        canvas = ctk.CTkCanvas(
            self.parent,
            bg='',
            highlightthickness=0
        )
        canvas.place(relx=0, rely=0, relwidth=1, relheight=1)
        return canvas
    
    def draw(self) -> None:
        """绘制静态扫描线"""
        if self._drawn:
            return
        
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        
        if width <= 1 or height <= 1:
            return
        
        # 清空画布
        self.clear_canvas()
        
        # 计算颜色
        alpha = int(self.opacity * 255)
        line_color = f"{self.color}{alpha:02x}" if len(self.color) == 7 else self.color
        
        # 绘制扫描线
        y = 0
        while y < height:
            self.canvas.create_line(
                0, y,
                width, y,
                fill=line_color,
                width=self.line_width,
                tags='scanline'
            )
            y += self.line_spacing
        
        self._drawn = True
    
    def start(self) -> None:
        """启动特效"""
        if not self._enabled:
            return
        
        self._running = True
        self.draw()


# 导出
__all__ = [
    'ScanlineEffect',
    'StaticScanlines',
]