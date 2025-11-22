"""
呼吸灯动画模块

提供周期性透明度变化的呼吸灯效果。
"""

from typing import Optional, List, Callable
import math
import customtkinter as ctk
from .base import AnimatedEffect


class BreathingLight(AnimatedEffect):
    """
    呼吸灯动画
    
    组件透明度周期性变化,模拟呼吸效果。
    
    使用示例:
        >>> breathing = BreathingLight(label, min_alpha=0.3, max_alpha=1.0, period=2000)
        >>> breathing.start()
    """
    
    def __init__(
        self,
        target: ctk.CTkBaseClass,
        min_alpha: float = 0.3,
        max_alpha: float = 1.0,
        period: int = 2000,
        easing: str = "sine",
        fps: int = 30,
        enabled: bool = True
    ):
        """
        初始化呼吸灯
        
        参数:
            target: 目标组件
            min_alpha: 最小透明度(0.0-1.0)
            max_alpha: 最大透明度(0.0-1.0)
            period: 呼吸周期(毫秒)
            easing: 缓动函数('sine', 'linear', 'quad')
            fps: 帧率
            enabled: 是否启用
        """
        super().__init__(target, fps, enabled)
        
        self.target = target
        self.min_alpha = max(0.0, min(1.0, min_alpha))
        self.max_alpha = max(0.0, min(1.0, max_alpha))
        self.period = period
        self.easing = easing
        
        self._phase = 0.0
        self._original_colors = {}
        
        # 保存原始颜色
        self._save_colors()
    
    def _save_colors(self) -> None:
        """保存组件原始颜色"""
        if not hasattr(self.target, 'cget'):
            return
        
        try:
            for attr in ['fg_color', 'text_color', 'border_color']:
                try:
                    color = self.target.cget(attr)
                    if color:
                        self._original_colors[attr] = color
                except:
                    pass
        except:
            pass
    
    def update(self) -> None:
        """更新呼吸状态"""
        # 计算当前透明度
        alpha = self._calculate_alpha()
        
        # 应用透明度
        self._apply_alpha(alpha)
        
        # 更新相位
        phase_increment = (2 * math.pi) / (self.period / self.frame_time)
        self._phase += phase_increment
        
        if self._phase >= 2 * math.pi:
            self._phase -= 2 * math.pi
    
    def _calculate_alpha(self) -> float:
        """
        计算当前透明度
        
        返回:
            当前透明度值
        """
        # 归一化相位到0-1
        normalized = self._phase / (2 * math.pi)
        
        # 应用缓动函数
        if self.easing == "sine":
            factor = (math.sin(self._phase - math.pi / 2) + 1) / 2
        elif self.easing == "linear":
            factor = 0.5 - abs(normalized - 0.5)
            factor *= 2
        elif self.easing == "quad":
            if normalized < 0.5:
                factor = 2 * normalized * normalized
            else:
                factor = 1 - 2 * (1 - normalized) * (1 - normalized)
        else:
            factor = (math.sin(self._phase - math.pi / 2) + 1) / 2
        
        # 映射到透明度范围
        alpha_range = self.max_alpha - self.min_alpha
        return self.min_alpha + alpha_range * factor
    
    def _apply_alpha(self, alpha: float) -> None:
        """
        应用透明度到组件
        
        参数:
            alpha: 透明度值
        """
        if not hasattr(self.target, 'configure'):
            return
        
        try:
            # 对每个保存的颜色应用透明度
            for attr, original_color in self._original_colors.items():
                new_color = self._add_alpha_to_color(original_color, alpha)
                self.target.configure(**{attr: new_color})
        except Exception as e:
            pass
    
    @staticmethod
    def _add_alpha_to_color(color: str, alpha: float) -> str:
        """
        为颜色添加透明度
        
        参数:
            color: 原始颜色
            alpha: 透明度
        
        返回:
            带透明度的颜色
        """
        if not color or not isinstance(color, str):
            return color
        
        # 如果是元组格式,转换为hex
        if isinstance(color, tuple):
            color = f"#{int(color[0]*255):02x}{int(color[1]*255):02x}{int(color[2]*255):02x}"
        
        # 提取RGB值
        if color.startswith('#'):
            if len(color) == 7:  # #RRGGBB
                r = int(color[1:3], 16)
                g = int(color[3:5], 16)
                b = int(color[5:7], 16)
                
                # 应用透明度
                r = int(r * alpha)
                g = int(g * alpha)
                b = int(b * alpha)
                
                return f"#{r:02x}{g:02x}{b:02x}"
        
        return color
    
    def set_period(self, period: int) -> None:
        """
        设置呼吸周期
        
        参数:
            period: 周期(毫秒)
        """
        self.period = max(100, period)
    
    def set_alpha_range(self, min_alpha: float, max_alpha: float) -> None:
        """
        设置透明度范围
        
        参数:
            min_alpha: 最小透明度
            max_alpha: 最大透明度
        """
        self.min_alpha = max(0.0, min(1.0, min_alpha))
        self.max_alpha = max(0.0, min(1.0, max_alpha))


class SyncedBreathing:
    """
    同步呼吸灯
    
    使多个组件同步呼吸。
    
    使用示例:
        >>> synced = SyncedBreathing([label1, label2, label3])
        >>> synced.start()
    """
    
    def __init__(
        self,
        targets: List[ctk.CTkBaseClass],
        min_alpha: float = 0.3,
        max_alpha: float = 1.0,
        period: int = 2000,
        easing: str = "sine",
        fps: int = 30
    ):
        """
        初始化同步呼吸灯
        
        参数:
            targets: 目标组件列表
            min_alpha: 最小透明度
            max_alpha: 最大透明度
            period: 周期
            easing: 缓动函数
            fps: 帧率
        """
        self.targets = targets
        self.breathings: List[BreathingLight] = []
        
        # 为每个目标创建呼吸灯
        for target in targets:
            breathing = BreathingLight(
                target,
                min_alpha=min_alpha,
                max_alpha=max_alpha,
                period=period,
                easing=easing,
                fps=fps,
                enabled=False
            )
            self.breathings.append(breathing)
    
    def start(self) -> None:
        """启动所有呼吸灯"""
        for breathing in self.breathings:
            breathing.start()
    
    def stop(self) -> None:
        """停止所有呼吸灯"""
        for breathing in self.breathings:
            breathing.stop()
    
    def toggle(self) -> None:
        """切换状态"""
        if self.breathings and self.breathings[0].running:
            self.stop()
        else:
            self.start()
    
    def set_period(self, period: int) -> None:
        """
        设置周期
        
        参数:
            period: 周期(毫秒)
        """
        for breathing in self.breathings:
            breathing.set_period(period)


class PulseEffect(AnimatedEffect):
    """
    脉冲效果
    
    单次脉冲动画,从最小到最大再回到最小。
    
    使用示例:
        >>> pulse = PulseEffect(button, on_complete=lambda: print("Done"))
        >>> pulse.trigger()
    """
    
    def __init__(
        self,
        target: ctk.CTkBaseClass,
        min_alpha: float = 0.5,
        max_alpha: float = 1.0,
        duration: int = 500,
        on_complete: Optional[Callable] = None,
        fps: int = 60,
        enabled: bool = True
    ):
        """
        初始化脉冲效果
        
        参数:
            target: 目标组件
            min_alpha: 起始透明度
            max_alpha: 峰值透明度
            duration: 持续时间(毫秒)
            on_complete: 完成回调
            fps: 帧率
            enabled: 是否启用
        """
        super().__init__(target, fps, enabled)
        
        self.target = target
        self.min_alpha = max(0.0, min(1.0, min_alpha))
        self.max_alpha = max(0.0, min(1.0, max_alpha))
        self.duration = duration
        self.on_complete = on_complete
        
        self._elapsed_time = 0
        self._original_colors = {}
        self._is_pulsing = False
        
        self._save_colors()
    
    def _save_colors(self) -> None:
        """保存原始颜色"""
        if not hasattr(self.target, 'cget'):
            return
        
        try:
            for attr in ['fg_color', 'text_color', 'border_color']:
                try:
                    color = self.target.cget(attr)
                    if color:
                        self._original_colors[attr] = color
                except:
                    pass
        except:
            pass
    
    def trigger(self) -> None:
        """触发一次脉冲"""
        if not self._is_pulsing:
            self._elapsed_time = 0
            self._is_pulsing = True
            if not self._running:
                self.start()
    
    def update(self) -> None:
        """更新脉冲"""
        if not self._is_pulsing:
            return
        
        self._elapsed_time += self.frame_time
        
        # 计算进度(0-1)
        progress = min(1.0, self._elapsed_time / self.duration)
        
        # 使用sin曲线实现脉冲
        alpha = self.min_alpha + (self.max_alpha - self.min_alpha) * math.sin(progress * math.pi)
        
        # 应用透明度
        self._apply_alpha(alpha)
        
        # 检查是否完成
        if progress >= 1.0:
            self._is_pulsing = False
            self._restore_colors()
            
            if self.on_complete:
                self.on_complete()
            
            self.stop()
    
    def _apply_alpha(self, alpha: float) -> None:
        """应用透明度"""
        if not hasattr(self.target, 'configure'):
            return
        
        try:
            for attr, original_color in self._original_colors.items():
                new_color = BreathingLight._add_alpha_to_color(original_color, alpha)
                self.target.configure(**{attr: new_color})
        except:
            pass
    
    def _restore_colors(self) -> None:
        """恢复原始颜色"""
        if not hasattr(self.target, 'configure'):
            return
        
        try:
            self.target.configure(**self._original_colors)
        except:
            pass


# 导出
__all__ = [
    'BreathingLight',
    'SyncedBreathing',
    'PulseEffect',
]