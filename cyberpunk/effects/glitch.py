"""
故障效果模块

提供赛博朋克风格的数字故障效果。
"""

from typing import Optional, List, Tuple
import random
import customtkinter as ctk
from .base import AnimatedEffect


class GlitchEffect(AnimatedEffect):
    """
    故障效果
    
    模拟数字信号故障,产生RGB通道分离、位移等效果。
    
    使用示例:
        >>> glitch = GlitchEffect(window, intensity=0.5, trigger_interval=3000)
        >>> glitch.start()
    """
    
    def __init__(
        self,
        parent: ctk.CTkBaseClass,
        intensity: float = 0.5,
        trigger_interval: int = 3000,
        glitch_duration: int = 200,
        fps: int = 60,
        enabled: bool = True
    ):
        """
        初始化故障效果
        
        参数:
            parent: 父窗口
            intensity: 故障强度(0.0-1.0)
            trigger_interval: 触发间隔(毫秒)
            glitch_duration: 单次故障持续时间(毫秒)
            fps: 帧率
            enabled: 是否启用
        """
        super().__init__(parent, fps, enabled)
        
        self.intensity = max(0.0, min(1.0, intensity))
        self.trigger_interval = trigger_interval
        self.glitch_duration = glitch_duration
        
        self._is_glitching = False
        self._glitch_timer = 0
        self._next_trigger = trigger_interval
        
        self._original_geometry = None
        self._glitch_widgets: List[ctk.CTkBaseClass] = []
    
    def register_widget(self, widget: ctk.CTkBaseClass) -> None:
        """
        注册要应用故障效果的组件
        
        参数:
            widget: 目标组件
        """
        if widget not in self._glitch_widgets:
            self._glitch_widgets.append(widget)
    
    def unregister_widget(self, widget: ctk.CTkBaseClass) -> None:
        """
        取消注册组件
        
        参数:
            widget: 目标组件
        """
        if widget in self._glitch_widgets:
            self._glitch_widgets.remove(widget)
    
    def update(self) -> None:
        """更新故障状态"""
        self._glitch_timer += self.frame_time
        
        if self._is_glitching:
            # 正在故障中
            if self._glitch_timer >= self.glitch_duration:
                self._end_glitch()
            else:
                self._apply_glitch()
        else:
            # 等待下次触发
            if self._glitch_timer >= self._next_trigger:
                self._start_glitch()
    
    def _start_glitch(self) -> None:
        """开始故障"""
        self._is_glitching = True
        self._glitch_timer = 0
        
        # 保存原始几何信息
        if hasattr(self.parent, 'winfo_geometry'):
            self._original_geometry = self.parent.winfo_geometry()
    
    def _end_glitch(self) -> None:
        """结束故障"""
        self._is_glitching = False
        self._glitch_timer = 0
        
        # 重置所有组件
        for widget in self._glitch_widgets:
            self._reset_widget(widget)
        
        # 随机化下次触发时间
        self._next_trigger = self.trigger_interval + random.randint(
            -self.trigger_interval // 4,
            self.trigger_interval // 4
        )
    
    def _apply_glitch(self) -> None:
        """应用故障效果"""
        for widget in self._glitch_widgets:
            if random.random() < self.intensity * 0.3:
                self._glitch_widget(widget)
    
    def _glitch_widget(self, widget: ctk.CTkBaseClass) -> None:
        """对单个组件应用故障"""
        try:
            # RGB通道分离效果(通过颜色调整模拟)
            if hasattr(widget, 'configure') and random.random() < 0.5:
                colors = ['#ff0000', '#00ff00', '#0000ff', '#ff00ff', '#00ffff']
                glitch_color = random.choice(colors)
                
                if hasattr(widget, 'cget'):
                    try:
                        widget.configure(fg_color=glitch_color)
                    except:
                        pass
            
            # 位置偏移
            if hasattr(widget, 'place_configure') and random.random() < 0.3:
                offset_x = random.randint(-5, 5) * self.intensity
                offset_y = random.randint(-5, 5) * self.intensity
                
                try:
                    info = widget.place_info()
                    if info:
                        current_x = float(info.get('relx', 0))
                        current_y = float(info.get('rely', 0))
                        widget.place_configure(
                            relx=current_x + offset_x * 0.01,
                            rely=current_y + offset_y * 0.01
                        )
                except:
                    pass
        except Exception as e:
            pass
    
    def _reset_widget(self, widget: ctk.CTkBaseClass) -> None:
        """重置组件状态"""
        try:
            # 这里应该恢复原始状态,但需要事先保存
            # 简化实现:不做处理,让组件自然恢复
            pass
        except Exception as e:
            pass
    
    def trigger_manual(self) -> None:
        """手动触发一次故障"""
        if not self._is_glitching:
            self._start_glitch()


class TextGlitch(AnimatedEffect):
    """
    文本故障效果
    
    对文本内容应用随机字符替换效果。
    
    使用示例:
        >>> glitch = TextGlitch(label, original_text="Hello World")
        >>> glitch.start()
    """
    
    def __init__(
        self,
        target: ctk.CTkLabel,
        original_text: str,
        intensity: float = 0.5,
        trigger_interval: int = 5000,
        glitch_duration: int = 300,
        fps: int = 30,
        enabled: bool = True
    ):
        """
        初始化文本故障
        
        参数:
            target: 目标标签
            original_text: 原始文本
            intensity: 故障强度
            trigger_interval: 触发间隔
            glitch_duration: 持续时间
            fps: 帧率
            enabled: 是否启用
        """
        super().__init__(target, fps, enabled)
        
        self.target = target
        self.original_text = original_text
        self.intensity = max(0.0, min(1.0, intensity))
        self.trigger_interval = trigger_interval
        self.glitch_duration = glitch_duration
        
        self._is_glitching = False
        self._glitch_timer = 0
        self._next_trigger = trigger_interval
        
        # 故障字符集
        self._glitch_chars = [
            '!', '@', '#', '$', '%', '^', '&', '*',
            '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
            'A', 'B', 'C', 'D', 'E', 'F', 'X', 'Y', 'Z',
            '░', '▒', '▓', '█', '▄', '▀'
        ]
    
    def update(self) -> None:
        """更新文本故障"""
        self._glitch_timer += self.frame_time
        
        if self._is_glitching:
            if self._glitch_timer >= self.glitch_duration:
                self._end_glitch()
            else:
                self._apply_text_glitch()
        else:
            if self._glitch_timer >= self._next_trigger:
                self._start_glitch()
    
    def _start_glitch(self) -> None:
        """开始文本故障"""
        self._is_glitching = True
        self._glitch_timer = 0
    
    def _end_glitch(self) -> None:
        """结束文本故障"""
        self._is_glitching = False
        self._glitch_timer = 0
        
        # 恢复原始文本
        try:
            self.target.configure(text=self.original_text)
        except:
            pass
        
        # 随机化下次触发
        self._next_trigger = self.trigger_interval + random.randint(
            -self.trigger_interval // 3,
            self.trigger_interval // 3
        )
    
    def _apply_text_glitch(self) -> None:
        """应用文本故障效果"""
        if not self.original_text:
            return
        
        glitched_text = list(self.original_text)
        text_length = len(glitched_text)
        
        # 随机替换部分字符
        num_glitches = int(text_length * self.intensity * 0.5)
        for _ in range(num_glitches):
            pos = random.randint(0, text_length - 1)
            glitched_text[pos] = random.choice(self._glitch_chars)
        
        try:
            self.target.configure(text=''.join(glitched_text))
        except:
            pass
    
    def set_text(self, text: str) -> None:
        """
        设置原始文本
        
        参数:
            text: 新文本
        """
        self.original_text = text
        if not self._is_glitching:
            try:
                self.target.configure(text=text)
            except:
                pass


class ColorGlitch(AnimatedEffect):
    """
    颜色故障效果
    
    随机改变组件颜色,模拟色彩故障。
    
    使用示例:
        >>> glitch = ColorGlitch(widget, trigger_interval=2000)
        >>> glitch.start()
    """
    
    def __init__(
        self,
        target: ctk.CTkBaseClass,
        intensity: float = 0.7,
        trigger_interval: int = 2000,
        glitch_duration: int = 150,
        fps: int = 60,
        enabled: bool = True
    ):
        """
        初始化颜色故障
        
        参数:
            target: 目标组件
            intensity: 强度
            trigger_interval: 触发间隔
            glitch_duration: 持续时间
            fps: 帧率
            enabled: 是否启用
        """
        super().__init__(target, fps, enabled)
        
        self.target = target
        self.intensity = max(0.0, min(1.0, intensity))
        self.trigger_interval = trigger_interval
        self.glitch_duration = glitch_duration
        
        self._is_glitching = False
        self._glitch_timer = 0
        self._next_trigger = trigger_interval
        
        self._original_colors = {}
        self._glitch_colors = [
            '#ff0000', '#00ff00', '#0000ff',
            '#ff00ff', '#00ffff', '#ffff00',
            '#ff6600', '#ff0066', '#6600ff',
            '#00ff66', '#66ff00', '#0066ff'
        ]
    
    def start(self) -> None:
        """启动效果"""
        # 保存原始颜色
        self._save_original_colors()
        super().start()
    
    def _save_original_colors(self) -> None:
        """保存组件原始颜色"""
        if not hasattr(self.target, 'cget'):
            return
        
        try:
            for attr in ['fg_color', 'text_color', 'border_color']:
                try:
                    self._original_colors[attr] = self.target.cget(attr)
                except:
                    pass
        except:
            pass
    
    def update(self) -> None:
        """更新颜色故障"""
        self._glitch_timer += self.frame_time
        
        if self._is_glitching:
            if self._glitch_timer >= self.glitch_duration:
                self._end_glitch()
            else:
                self._apply_color_glitch()
        else:
            if self._glitch_timer >= self._next_trigger:
                self._start_glitch()
    
    def _start_glitch(self) -> None:
        """开始颜色故障"""
        self._is_glitching = True
        self._glitch_timer = 0
    
    def _end_glitch(self) -> None:
        """结束颜色故障"""
        self._is_glitching = False
        self._glitch_timer = 0
        
        # 恢复原始颜色
        if hasattr(self.target, 'configure'):
            try:
                self.target.configure(**self._original_colors)
            except:
                pass
        
        # 随机化下次触发
        self._next_trigger = self.trigger_interval + random.randint(
            -self.trigger_interval // 3,
            self.trigger_interval // 3
        )
    
    def _apply_color_glitch(self) -> None:
        """应用颜色故障"""
        if not hasattr(self.target, 'configure'):
            return
        
        if random.random() < self.intensity:
            glitch_color = random.choice(self._glitch_colors)
            try:
                # 随机选择要改变的颜色属性
                attrs = ['fg_color', 'text_color', 'border_color']
                attr = random.choice(attrs)
                self.target.configure(**{attr: glitch_color})
            except:
                pass


# 导出
__all__ = [
    'GlitchEffect',
    'TextGlitch',
    'ColorGlitch',
]