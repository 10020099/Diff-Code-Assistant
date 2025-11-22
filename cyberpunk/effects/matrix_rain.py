"""
数字雨背景特效模块

提供Matrix风格的字符下落背景效果。
"""

from typing import Optional, List
import random
import customtkinter as ctk
from .base import CanvasEffect


class MatrixRain(CanvasEffect):
    """
    数字雨背景特效
    
    模拟《黑客帝国》风格的字符下落效果。
    
    使用示例:
        >>> rain = MatrixRain(window, color="#00ff00", density=0.7)
        >>> rain.start()
    """
    
    def __init__(
        self,
        parent: ctk.CTkBaseClass,
        color: str = "#00ff00",
        density: float = 0.5,
        speed: float = 1.0,
        char_set: Optional[str] = None,
        font_size: int = 14,
        trail_length: int = 15,
        fps: int = 30,
        enabled: bool = True,
        canvas: Optional[ctk.CTkCanvas] = None
    ):
        """
        初始化数字雨
        
        参数:
            parent: 父窗口
            color: 字符颜色
            density: 密度(0.0-1.0)
            speed: 下落速度
            char_set: 字符集(None使用默认)
            font_size: 字体大小
            trail_length: 拖尾长度
            fps: 帧率
            enabled: 是否启用
            canvas: 自定义Canvas
        """
        super().__init__(parent, fps, enabled, canvas)
        
        self.color = color
        self.density = max(0.0, min(1.0, density))
        self.speed = speed
        self.font_size = font_size
        self.trail_length = trail_length
        
        # 设置字符集
        if char_set is None:
            self.char_set = self._get_default_charset()
        else:
            self.char_set = char_set
        
        self._columns: List['RainColumn'] = []
        self._canvas_width = 0
        self._canvas_height = 0
        
        self.canvas.bind('<Configure>', self._on_resize)
    
    def _get_default_charset(self) -> str:
        """获取默认字符集"""
        # 数字、字母、日文片假名
        chars = []
        
        # 数字
        chars.extend([str(i) for i in range(10)])
        
        # 大写字母
        chars.extend([chr(i) for i in range(65, 91)])
        
        # 一些特殊字符
        chars.extend(['@', '#', '$', '%', '&', '*'])
        
        # 日文片假名(部分)
        chars.extend(['ｱ', 'ｲ', 'ｳ', 'ｴ', 'ｵ', 'ｶ', 'ｷ', 'ｸ', 'ｹ', 'ｺ'])
        
        return ''.join(chars)
    
    def _on_resize(self, event) -> None:
        """处理窗口大小变化"""
        self._canvas_width = event.width
        self._canvas_height = event.height
        self._initialize_columns()
    
    def _create_canvas(self) -> ctk.CTkCanvas:
        """创建Canvas"""
        canvas = ctk.CTkCanvas(
            self.parent,
            bg='black',
            highlightthickness=0
        )
        canvas.place(relx=0, rely=0, relwidth=1, relheight=1)
        return canvas
    
    def _initialize_columns(self) -> None:
        """初始化字符列"""
        if self._canvas_width <= 0 or self._canvas_height <= 0:
            return
        
        self._columns.clear()
        
        # 计算列数
        column_width = self.font_size
        num_columns = int(self._canvas_width / column_width)
        
        # 创建列
        for i in range(num_columns):
            if random.random() < self.density:
                column = RainColumn(
                    x=i * column_width,
                    canvas_height=self._canvas_height,
                    speed=self.speed * (0.5 + random.random()),
                    char_set=self.char_set,
                    font_size=self.font_size,
                    trail_length=self.trail_length,
                    color=self.color
                )
                self._columns.append(column)
    
    def start(self) -> None:
        """启动数字雨"""
        if self._canvas_width == 0:
            self._canvas_width = self.canvas.winfo_width()
            self._canvas_height = self.canvas.winfo_height()
        
        self._initialize_columns()
        super().start()
    
    def draw(self) -> None:
        """绘制数字雨"""
        # 清空画布
        self.clear_canvas()
        
        # 更新并绘制所有列
        for column in self._columns:
            column.update()
            column.draw(self.canvas)
            
            # 如果列完成,重置它
            if column.is_finished():
                column.reset()
    
    def set_density(self, density: float) -> None:
        """
        设置密度
        
        参数:
            density: 密度(0.0-1.0)
        """
        self.density = max(0.0, min(1.0, density))
        self._initialize_columns()
    
    def set_speed(self, speed: float) -> None:
        """
        设置速度
        
        参数:
            speed: 速度倍数
        """
        self.speed = speed
        for column in self._columns:
            column.speed = speed * (0.5 + random.random())


class RainColumn:
    """
    数字雨字符列
    
    表示一列下落的字符。
    """
    
    def __init__(
        self,
        x: int,
        canvas_height: int,
        speed: float,
        char_set: str,
        font_size: int,
        trail_length: int,
        color: str
    ):
        """
        初始化字符列
        
        参数:
            x: X坐标
            canvas_height: Canvas高度
            speed: 下落速度
            char_set: 字符集
            font_size: 字体大小
            trail_length: 拖尾长度
            color: 颜色
        """
        self.x = x
        self.canvas_height = canvas_height
        self.speed = speed
        self.char_set = char_set
        self.font_size = font_size
        self.trail_length = trail_length
        self.color = color
        
        self.y = -trail_length * font_size
        self.chars: List[str] = []
        self._generate_chars()
    
    def _generate_chars(self) -> None:
        """生成字符序列"""
        self.chars = [
            random.choice(self.char_set)
            for _ in range(self.trail_length)
        ]
    
    def update(self) -> None:
        """更新位置"""
        self.y += self.speed
        
        # 偶尔改变头部字符
        if random.random() < 0.05:
            self.chars[0] = random.choice(self.char_set)
    
    def draw(self, canvas: ctk.CTkCanvas) -> None:
        """
        绘制字符列
        
        参数:
            canvas: Canvas对象
        """
        for i, char in enumerate(self.chars):
            char_y = self.y + i * self.font_size
            
            if char_y < 0 or char_y > self.canvas_height:
                continue
            
            # 计算透明度(头部最亮)
            alpha = 1.0 - (i / self.trail_length)
            alpha = max(0.1, alpha)
            
            # 头部字符更亮
            if i == 0:
                char_color = '#ffffff'
            else:
                # 转换颜色为带透明度的格式
                char_color = self._color_with_alpha(self.color, alpha)
            
            # 绘制字符
            try:
                canvas.create_text(
                    self.x,
                    char_y,
                    text=char,
                    fill=char_color,
                    font=('Consolas', self.font_size, 'bold'),
                    anchor='nw'
                )
            except:
                pass
    
    def is_finished(self) -> bool:
        """
        检查是否完成
        
        返回:
            是否已完全离开屏幕
        """
        return self.y > self.canvas_height + self.font_size
    
    def reset(self) -> None:
        """重置到顶部"""
        self.y = -self.trail_length * self.font_size
        self._generate_chars()
    
    @staticmethod
    def _color_with_alpha(color: str, alpha: float) -> str:
        """
        为颜色添加透明度
        
        参数:
            color: 颜色值
            alpha: 透明度
        
        返回:
            带透明度的颜色
        """
        if len(color) == 7:  # #RRGGBB
            # 简化:通过降低RGB值模拟透明度
            r = int(color[1:3], 16)
            g = int(color[3:5], 16)
            b = int(color[5:7], 16)
            
            r = int(r * alpha)
            g = int(g * alpha)
            b = int(b * alpha)
            
            return f"#{r:02x}{g:02x}{b:02x}"
        return color


class BinaryRain(MatrixRain):
    """
    二进制雨
    
    仅使用0和1的简化版数字雨。
    
    使用示例:
        >>> rain = BinaryRain(window, color="#00ff00")
        >>> rain.start()
    """
    
    def __init__(
        self,
        parent: ctk.CTkBaseClass,
        color: str = "#00ff00",
        density: float = 0.5,
        speed: float = 1.0,
        font_size: int = 14,
        trail_length: int = 15,
        fps: int = 30,
        enabled: bool = True,
        canvas: Optional[ctk.CTkCanvas] = None
    ):
        """
        初始化二进制雨
        
        参数:
            parent: 父窗口
            color: 颜色
            density: 密度
            speed: 速度
            font_size: 字体大小
            trail_length: 拖尾长度
            fps: 帧率
            enabled: 是否启用
            canvas: 自定义Canvas
        """
        super().__init__(
            parent=parent,
            color=color,
            density=density,
            speed=speed,
            char_set="01",  # 仅使用0和1
            font_size=font_size,
            trail_length=trail_length,
            fps=fps,
            enabled=enabled,
            canvas=canvas
        )


# 导出
__all__ = [
    'MatrixRain',
    'BinaryRain',
    'RainColumn',
]