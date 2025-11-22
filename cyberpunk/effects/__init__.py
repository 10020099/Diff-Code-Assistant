"""
赛博朋克特效系统

提供各种赛博朋克风格的视觉特效:
- 扫描线效果
- 霓虹发光
- 故障效果
- 数字雨背景
- 呼吸灯动画
- 粒子系统

使用示例:
    >>> from cyberpunk.effects import ScanlineEffect, NeonGlow, EffectManager
    >>> 
    >>> # 创建特效管理器
    >>> manager = EffectManager(window)
    >>> 
    >>> # 创建扫描线特效
    >>> scanlines = ScanlineEffect(window)
    >>> manager.add_effect('scanlines', scanlines)
    >>> 
    >>> # 添加霓虹发光
    >>> glow = NeonGlow(button, color="cyan", intensity=0.8)
    >>> manager.add_effect('glow', glow)
    >>> 
    >>> # 启动所有特效
    >>> manager.start_all()
"""

# 基础类
from .base import (
    EffectBase,
    AnimatedEffect,
    CanvasEffect,
    WidgetEffect
)

# 扫描线效果
from .scanlines import (
    ScanlineEffect,
    StaticScanlines
)

# 霓虹发光
from .glow import (
    NeonGlow,
    PulsingGlow,
    RainbowGlow,
    MultiColorGlow
)

# 故障效果
from .glitch import (
    GlitchEffect,
    TextGlitch,
    ColorGlitch
)

# 数字雨
from .matrix_rain import (
    MatrixRain,
    BinaryRain,
    RainColumn
)

# 呼吸灯
from .breathing import (
    BreathingLight,
    SyncedBreathing,
    PulseEffect
)

# 粒子系统
from .particles import (
    Particle,
    ParticleSystem,
    TrailEffect
)

# 管理器
from .manager import (
    EffectManager,
    PresetManager
)

__all__ = [
    # 基础类
    'EffectBase',
    'AnimatedEffect',
    'CanvasEffect',
    'WidgetEffect',
    
    # 扫描线
    'ScanlineEffect',
    'StaticScanlines',
    
    # 发光
    'NeonGlow',
    'PulsingGlow',
    'RainbowGlow',
    'MultiColorGlow',
    
    # 故障
    'GlitchEffect',
    'TextGlitch',
    'ColorGlitch',
    
    # 数字雨
    'MatrixRain',
    'BinaryRain',
    'RainColumn',
    
    # 呼吸灯
    'BreathingLight',
    'SyncedBreathing',
    'PulseEffect',
    
    # 粒子
    'Particle',
    'ParticleSystem',
    'TrailEffect',
    
    # 管理器
    'EffectManager',
    'PresetManager',
]

__version__ = '1.0.0'
__author__ = 'Cyberpunk UI Team'