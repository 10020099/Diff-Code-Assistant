"""
赛博朋克UI系统

一个完整的赛博朋克风格UI框架,基于CustomTkinter。

主要功能:
- 完整的配色系统
- 主题管理
- 26个UI组件
- 6类视觉特效
- 动画和验证工具

使用示例:
    >>> import cyberpunk as cp
    >>> from cyberpunk.components import CyberButton, CyberFrame
    >>> from cyberpunk.effects import ScanlineEffect, NeonGlow
    >>> 
    >>> # 创建窗口
    >>> app = ctk.CTk()
    >>> 
    >>> # 使用组件
    >>> button = CyberButton(app, text="开始")
    >>> button.pack()
    >>> 
    >>> # 添加特效
    >>> glow = NeonGlow(button, color=cp.CyberpunkColors.CYAN)
    >>> glow.start()
"""

# 版本信息
__version__ = '1.0.0'
__author__ = 'Cyberpunk UI Team'
__license__ = 'MIT'

# 核心模块
from . import colors
from .colors import ColorScheme
from .theme import CyberpunkTheme

# 组件基类
from .components.base import (
    CyberWidgetBase,
    CyberButtonBase,
    CyberFrameBase,
    CyberEntryBase,
    CyberLabelBase
)

# 按钮组件
from .components.button import (
    CyberButton,
    CyberIconButton,
    CyberToggleButton
)

# 输入框组件
from .components.entry import (
    CyberEntry,
    CyberPasswordEntry,
    CyberSearchEntry,
    CyberNumberEntry
)

# 框架组件
from .components.frame import (
    CyberFrame,
    CyberCard,
    CyberPanel,
    CyberContainer
)

# 标签组件
from .components.label import (
    CyberLabel,
    CyberBadge,
    CyberStatusLabel,
    CyberLinkLabel
)

# 进度组件
from .components.progress import (
    CyberProgressBar,
    CyberCircularProgress,
    CyberLoadingSpinner
)

# 文本框组件
from .components.textbox import (
    CyberTextbox,
    CyberCodeEditor,
    CyberLogViewer
)

# 特效系统
from .effects import (
    # 基础类
    EffectBase,
    AnimatedEffect,
    CanvasEffect,
    WidgetEffect,
    
    # 扫描线
    ScanlineEffect,
    StaticScanlines,
    
    # 发光
    NeonGlow,
    PulsingGlow,
    RainbowGlow,
    MultiColorGlow,
    
    # 故障
    GlitchEffect,
    TextGlitch,
    ColorGlitch,
    
    # 数字雨
    MatrixRain,
    BinaryRain,
    
    # 呼吸灯
    BreathingLight,
    SyncedBreathing,
    PulseEffect,
    
    # 粒子
    ParticleSystem,
    TrailEffect,
    
    # 管理器
    EffectManager,
    PresetManager
)

# 工具函数
from .utils import animations
from .utils import validators

# 导出列表
__all__ = [
    # 版本信息
    '__version__',
    '__author__',
    '__license__',
    
    # 核心
    'colors',
    'ColorScheme',
    'CyberpunkTheme',
    
    # 基类
    'CyberWidgetBase',
    'CyberButtonBase',
    'CyberFrameBase',
    'CyberEntryBase',
    'CyberLabelBase',
    
    # 按钮
    'CyberButton',
    'CyberIconButton',
    'CyberToggleButton',
    
    # 输入框
    'CyberEntry',
    'CyberPasswordEntry',
    'CyberSearchEntry',
    'CyberNumberEntry',
    
    # 框架
    'CyberFrame',
    'CyberCard',
    'CyberPanel',
    'CyberContainer',
    
    # 标签
    'CyberLabel',
    'CyberBadge',
    'CyberStatusLabel',
    'CyberLinkLabel',
    
    # 进度
    'CyberProgressBar',
    'CyberCircularProgress',
    'CyberLoadingSpinner',
    
    # 文本框
    'CyberTextbox',
    'CyberCodeEditor',
    'CyberLogViewer',
    
    # 特效基类
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
    
    # 呼吸灯
    'BreathingLight',
    'SyncedBreathing',
    'PulseEffect',
    
    # 粒子
    'ParticleSystem',
    'TrailEffect',
    
    # 管理器
    'EffectManager',
    'PresetManager',
    
    # 工具
    'animations',
    'validators',
]

# 快捷访问
# colors is already available as a module
theme = CyberpunkTheme