"""
动画工具函数
提供各种缓动函数和动画辅助功能
"""

import math
from typing import Callable

# ================================
# 缓动函数
# ================================

def linear(t: float) -> float:
    """线性缓动"""
    return t

def ease_in(t: float) -> float:
    """淡入缓动 (加速)"""
    return t * t

def ease_out(t: float) -> float:
    """淡出缓动 (减速)"""
    return t * (2 - t)

def ease_in_out(t: float) -> float:
    """淡入淡出缓动 (先加速后减速)"""
    if t < 0.5:
        return 2 * t * t
    return -1 + (4 - 2 * t) * t

def ease_in_cubic(t: float) -> float:
    """三次淡入"""
    return t * t * t

def ease_out_cubic(t: float) -> float:
    """三次淡出"""
    return (--t) * t * t + 1

def ease_in_out_cubic(t: float) -> float:
    """三次淡入淡出"""
    if t < 0.5:
        return 4 * t * t * t
    return (t - 1) * (2 * t - 2) * (2 * t - 2) + 1

def ease_in_sine(t: float) -> float:
    """正弦淡入"""
    return 1 - math.cos(t * math.pi / 2)

def ease_out_sine(t: float) -> float:
    """正弦淡出"""
    return math.sin(t * math.pi / 2)

def ease_in_out_sine(t: float) -> float:
    """正弦淡入淡出"""
    return -(math.cos(math.pi * t) - 1) / 2

def ease_in_bounce(t: float) -> float:
    """弹跳淡入"""
    return 1 - ease_out_bounce(1 - t)

def ease_out_bounce(t: float) -> float:
    """弹跳淡出"""
    if t < 1 / 2.75:
        return 7.5625 * t * t
    elif t < 2 / 2.75:
        t -= 1.5 / 2.75
        return 7.5625 * t * t + 0.75
    elif t < 2.5 / 2.75:
        t -= 2.25 / 2.75
        return 7.5625 * t * t + 0.9375
    else:
        t -= 2.625 / 2.75
        return 7.5625 * t * t + 0.984375

def ease_in_out_bounce(t: float) -> float:
    """弹跳淡入淡出"""
    if t < 0.5:
        return ease_in_bounce(t * 2) * 0.5
    return ease_out_bounce(t * 2 - 1) * 0.5 + 0.5

# ================================
# 动画辅助函数
# ================================

def animate_value(start: float, end: float, progress: float, 
                 easing: Callable[[float], float] = ease_in_out) -> float:
    """
    根据进度插值计算动画值
    
    Args:
        start: 起始值
        end: 结束值
        progress: 进度 (0.0-1.0)
        easing: 缓动函数
    
    Returns:
        插值后的值
    """
    progress = max(0.0, min(1.0, progress))  # 限制在0-1之间
    eased_progress = easing(progress)
    return start + (end - start) * eased_progress

def animate_color(start_color: tuple, end_color: tuple, progress: float,
                 easing: Callable[[float], float] = ease_in_out) -> tuple:
    """
    颜色动画插值
    
    Args:
        start_color: 起始RGB颜色 (r, g, b)
        end_color: 结束RGB颜色 (r, g, b)
        progress: 进度 (0.0-1.0)
        easing: 缓动函数
    
    Returns:
        插值后的RGB颜色
    """
    r = animate_value(start_color[0], end_color[0], progress, easing)
    g = animate_value(start_color[1], end_color[1], progress, easing)
    b = animate_value(start_color[2], end_color[2], progress, easing)
    return (int(r), int(g), int(b))

def get_pulse_value(time: float, frequency: float = 1.0, 
                   min_val: float = 0.5, max_val: float = 1.0) -> float:
    """
    获取脉冲/呼吸效果的值
    
    Args:
        time: 当前时间 (秒)
        frequency: 频率 (Hz)
        min_val: 最小值
        max_val: 最大值
    
    Returns:
        脉冲值
    """
    # 使用正弦波生成平滑的脉冲
    normalized = (math.sin(time * frequency * 2 * math.pi) + 1) / 2
    return min_val + (max_val - min_val) * normalized

def get_wave_offset(time: float, index: int, wave_length: float = 1.0,
                   amplitude: float = 10.0, speed: float = 1.0) -> float:
    """
    获取波浪效果的偏移量
    
    Args:
        time: 当前时间 (秒)
        index: 元素索引
        wave_length: 波长
        amplitude: 振幅
        speed: 速度
    
    Returns:
        偏移量
    """
    return amplitude * math.sin(2 * math.pi * (index / wave_length - time * speed))

# ================================
# 粒子系统辅助
# ================================

class Particle:
    """粒子数据类"""
    
    def __init__(self, x: float, y: float, vx: float, vy: float,
                 lifetime: float, color: str, size: float):
        self.x = x
        self.y = y
        self.vx = vx  # x方向速度
        self.vy = vy  # y方向速度
        self.lifetime = lifetime  # 生命周期
        self.age = 0.0  # 当前年龄
        self.color = color
        self.size = size
        self.alpha = 1.0
    
    def update(self, dt: float):
        """更新粒子状态"""
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.age += dt
        
        # 根据年龄计算透明度
        if self.lifetime > 0:
            self.alpha = 1.0 - (self.age / self.lifetime)
        
        # 应用重力或其他力
        self.vy += 9.8 * dt  # 简单的重力效果
    
    def is_alive(self) -> bool:
        """检查粒子是否存活"""
        return self.age < self.lifetime

# ================================
# 测试代码
# ================================

if __name__ == "__main__":
    print("🎬 动画工具函数测试")
    print("=" * 50)
    
    # 测试缓动函数
    print("\n缓动函数测试 (进度=0.5):")
    print(f"  线性: {linear(0.5):.3f}")
    print(f"  淡入: {ease_in(0.5):.3f}")
    print(f"  淡出: {ease_out(0.5):.3f}")
    print(f"  淡入淡出: {ease_in_out(0.5):.3f}")
    
    # 测试值动画
    print("\n值动画测试 (0->100, 进度=0.5):")
    for name, func in [
        ("线性", linear),
        ("淡入", ease_in),
        ("淡出", ease_out),
        ("淡入淡出", ease_in_out),
    ]:
        value = animate_value(0, 100, 0.5, func)
        print(f"  {name}: {value:.2f}")
    
    # 测试颜色动画
    print("\n颜色动画测试:")
    start = (0, 243, 255)  # NEON_CYAN的RGB
    end = (255, 0, 229)    # NEON_MAGENTA的RGB
    for progress in [0.0, 0.25, 0.5, 0.75, 1.0]:
        color = animate_color(start, end, progress)
        print(f"  进度 {progress}: RGB{color}")
    
    # 测试脉冲效果
    print("\n脉冲效果测试 (频率=1Hz):")
    for t in [0.0, 0.25, 0.5, 0.75, 1.0]:
        value = get_pulse_value(t, frequency=1.0)
        print(f"  时间 {t}s: {value:.3f}")
    
    print("\n✅ 动画工具函数测试完成")