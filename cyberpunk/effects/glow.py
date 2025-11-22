"""
霓虹发光特效模块

提供赛博朋克风格的霓虹发光效果。
"""

from typing import Optional, List, Tuple
import customtkinter as ctk
from .base import WidgetEffect, AnimatedEffect


class NeonGlow(WidgetEffect):
    """
    霓虹发光特效
    
    为组件添加多层霓虹发光效果。
    
    使用示例:
        >>> button = CyberButton(window, text="Glow")
        >>> glow = NeonGlow(button, color="#00ffff", intensity=0.8)
        >>> glow.start()
    """
    
    def __init__(
        self,
        target: ctk.CTkBaseClass,
        color: str = "#00ffff",
        intensity: float = 0.6,
        blur_radius: int = 10,
        layers: int = 3,
        enabled: bool = True
    ):
        """
        初始化霓虹发光
        
        参数:
            target: 目标组件
            color: 发光颜色
            intensity: 发光强度(0.0-1.0)
            blur_radius: 模糊半径
            layers: 发光层数
            enabled: 是否启用
        """
        super().__init__(target, enabled)
        
        self.color = color
        self.intensity = max(0.0, min(1.0, intensity))
        self.blur_radius = blur_radius
        self.layers = layers
        
        self._original_fg_color = None
    
    def apply(self) -> None:
        """应用发光效果"""
        try:
            # 保存原始颜色
            if hasattr(self.target, 'cget'):
                try:
                    self._original_fg_color = self.target.cget('fg_color')
                except:
                    self._original_fg_color = None
            
            # 构建阴影字符串
            shadows = self._build_shadow_string()
            
            # 应用发光效果(通过border实现)
            if hasattr(self.target, 'configure'):
                try:
                    self.target.configure(
                        border_color=self.color,
                        border_width=self.blur_radius
                    )
                except:
                    pass
        except Exception as e:
            print(f"应用发光效果失败: {e}")
    
    def remove(self) -> None:
        """移除发光效果"""
        try:
            if hasattr(self.target, 'configure'):
                try:
                    self.target.configure(
                        border_width=0
                    )
                    
                    # 恢复原始颜色
                    if self._original_fg_color:
                        self.target.configure(fg_color=self._original_fg_color)
                except:
                    pass
        except Exception as e:
            print(f"移除发光效果失败: {e}")
    
    def _build_shadow_string(self) -> str:
        """构建多层阴影字符串"""
        shadows = []
        for i in range(1, self.layers + 1):
            offset = i * (self.blur_radius // self.layers)
            alpha = int((self.intensity / self.layers) * 255)
            shadow_color = f"{self.color}{alpha:02x}"
            shadows.append(f"{offset}px {offset}px {offset}px {shadow_color}")
        return ", ".join(shadows)
    
    def set_intensity(self, intensity: float) -> None:
        """
        设置发光强度
        
        参数:
            intensity: 强度(0.0-1.0)
        """
        self.intensity = max(0.0, min(1.0, intensity))
        if self._running:
            self.apply()
    
    def set_color(self, color: str) -> None:
        """
        设置发光颜色
        
        参数:
            color: 颜色值
        """
        self.color = color
        if self._running:
            self.apply()
    
    def update(self) -> None:
        """更新特效"""
        pass


class PulsingGlow(AnimatedEffect):
    """
    脉冲发光特效
    
    发光强度随时间脉动变化。
    
    使用示例:
        >>> glow = PulsingGlow(button, color="#ff00ff", min_intensity=0.3, max_intensity=0.9)
        >>> glow.start()
    """
    
    def __init__(
        self,
        target: ctk.CTkBaseClass,
        color: str = "#00ffff",
        min_intensity: float = 0.3,
        max_intensity: float = 0.9,
        pulse_speed: float = 2.0,
        blur_radius: int = 10,
        fps: int = 30,
        enabled: bool = True
    ):
        """
        初始化脉冲发光
        
        参数:
            target: 目标组件
            color: 发光颜色
            min_intensity: 最小强度
            max_intensity: 最大强度
            pulse_speed: 脉冲速度
            blur_radius: 模糊半径
            fps: 帧率
            enabled: 是否启用
        """
        super().__init__(target, fps, enabled)
        
        self.target = target
        self.color = color
        self.min_intensity = max(0.0, min(1.0, min_intensity))
        self.max_intensity = max(0.0, min(1.0, max_intensity))
        self.pulse_speed = pulse_speed
        self.blur_radius = blur_radius
        
        self._phase = 0.0
        self._base_glow = NeonGlow(
            target,
            color=color,
            intensity=min_intensity,
            blur_radius=blur_radius,
            enabled=False
        )
    
    def start(self) -> None:
        """启动脉冲"""
        self._base_glow.start()
        super().start()
    
    def stop(self) -> None:
        """停止脉冲"""
        super().stop()
        self._base_glow.stop()
    
    def update(self) -> None:
        """更新脉冲"""
        import math
        
        # 计算当前强度
        intensity_range = self.max_intensity - self.min_intensity
        intensity = self.min_intensity + (
            intensity_range * (math.sin(self._phase) + 1) / 2
        )
        
        # 应用强度
        self._base_glow.set_intensity(intensity)
        
        # 更新相位
        self._phase += self.pulse_speed * 0.1
        if self._phase > 2 * math.pi:
            self._phase -= 2 * math.pi


class RainbowGlow(AnimatedEffect):
    """
    彩虹发光特效
    
    发光颜色循环变化。
    
    使用示例:
        >>> glow = RainbowGlow(button, intensity=0.7, speed=1.0)
        >>> glow.start()
    """
    
    def __init__(
        self,
        target: ctk.CTkBaseClass,
        intensity: float = 0.6,
        speed: float = 1.0,
        blur_radius: int = 10,
        fps: int = 30,
        enabled: bool = True
    ):
        """
        初始化彩虹发光
        
        参数:
            target: 目标组件
            intensity: 发光强度
            speed: 变化速度
            blur_radius: 模糊半径
            fps: 帧率
            enabled: 是否启用
        """
        super().__init__(target, fps, enabled)
        
        self.target = target
        self.intensity = max(0.0, min(1.0, intensity))
        self.speed = speed
        self.blur_radius = blur_radius
        
        self._hue = 0.0
        self._base_glow = NeonGlow(
            target,
            color="#ff0000",
            intensity=intensity,
            blur_radius=blur_radius,
            enabled=False
        )
    
    def start(self) -> None:
        """启动彩虹效果"""
        self._base_glow.start()
        super().start()
    
    def stop(self) -> None:
        """停止彩虹效果"""
        super().stop()
        self._base_glow.stop()
    
    def update(self) -> None:
        """更新彩虹颜色"""
        # 计算当前颜色
        color = self._hsv_to_rgb(self._hue, 1.0, 1.0)
        self._base_glow.set_color(color)
        
        # 更新色相
        self._hue += self.speed * 0.01
        if self._hue >= 1.0:
            self._hue -= 1.0
    
    @staticmethod
    def _hsv_to_rgb(h: float, s: float, v: float) -> str:
        """
        HSV转RGB
        
        参数:
            h: 色相(0.0-1.0)
            s: 饱和度(0.0-1.0)
            v: 明度(0.0-1.0)
        
        返回:
            RGB颜色字符串
        """
        import colorsys
        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        return f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"


class MultiColorGlow(AnimatedEffect):
    """
    多色发光特效
    
    在多个预设颜色间循环变化。
    
    使用示例:
        >>> colors = ["#ff0000", "#00ff00", "#0000ff"]
        >>> glow = MultiColorGlow(button, colors=colors, transition_time=1000)
        >>> glow.start()
    """
    
    def __init__(
        self,
        target: ctk.CTkBaseClass,
        colors: List[str],
        intensity: float = 0.6,
        transition_time: int = 1000,
        blur_radius: int = 10,
        fps: int = 30,
        enabled: bool = True
    ):
        """
        初始化多色发光
        
        参数:
            target: 目标组件
            colors: 颜色列表
            intensity: 发光强度
            transition_time: 过渡时间(毫秒)
            blur_radius: 模糊半径
            fps: 帧率
            enabled: 是否启用
        """
        super().__init__(target, fps, enabled)
        
        self.target = target
        self.colors = colors if len(colors) > 0 else ["#00ffff"]
        self.intensity = max(0.0, min(1.0, intensity))
        self.transition_time = transition_time
        self.blur_radius = blur_radius
        
        self._current_index = 0
        self._elapsed_time = 0
        
        self._base_glow = NeonGlow(
            target,
            color=self.colors[0],
            intensity=intensity,
            blur_radius=blur_radius,
            enabled=False
        )
    
    def start(self) -> None:
        """启动多色效果"""
        self._base_glow.start()
        super().start()
    
    def stop(self) -> None:
        """停止多色效果"""
        super().stop()
        self._base_glow.stop()
    
    def update(self) -> None:
        """更新颜色"""
        self._elapsed_time += self.frame_time
        
        if self._elapsed_time >= self.transition_time:
            # 切换到下一个颜色
            self._current_index = (self._current_index + 1) % len(self.colors)
            self._base_glow.set_color(self.colors[self._current_index])
            self._elapsed_time = 0


# 导出
__all__ = [
    'NeonGlow',
    'PulsingGlow',
    'RainbowGlow',
    'MultiColorGlow',
]