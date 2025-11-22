"""
赛博朋克配色系统
定义所有UI使用的颜色常量和配色方案
"""

from typing import Dict, Tuple

# ================================
# 主色系
# ================================

# 霓虹色系 - 主要UI元素
NEON_CYAN = "#00f3ff"           # 霓虹青 - 主色
NEON_MAGENTA = "#ff00e5"        # 霓虹品红 - 次色
NEON_PURPLE = "#b300ff"         # 霓虹紫 - 辅色
NEON_BLUE = "#0080ff"           # 霓虹蓝 - 辅助色
NEON_GREEN = "#00ff88"          # 霓虹绿 - 成功色

# 深色背景系
DEEP_SPACE = "#0a0e1a"          # 深空黑 - 主背景
DARK_VOID = "#151b2e"           # 暗黑虚空 - 次背景
NIGHT_BLUE = "#1a2332"          # 夜蓝 - 组件背景
SHADOW_GRAY = "#1e2738"         # 阴影灰 - 边框/分隔

# 中性色系 - 文本和辅助
CYBER_GRAY = "#8892b0"          # 赛博灰 - 次要文本
STEEL_BLUE = "#a8b2d1"          # 钢蓝 - 普通文本
GHOST_WHITE = "#e6f1ff"         # 幽灵白 - 主要文本
MUTED_CYAN = "#64ffda"          # 柔和青 - 高亮文本

# 功能色系
ERROR_RED = "#ff3366"           # 错误红
WARNING_ORANGE = "#ffaa00"      # 警告橙
SUCCESS_GREEN = "#00ff88"       # 成功绿
INFO_BLUE = "#00b8ff"           # 信息蓝

# ================================
# 渐变配色
# ================================

# 渐变定义 (起始色, 结束色)
GRADIENT_CYBER = (NEON_CYAN, NEON_PURPLE)      # 赛博渐变
GRADIENT_MATRIX = (NEON_GREEN, NEON_CYAN)       # 矩阵渐变
GRADIENT_SUNSET = (NEON_MAGENTA, NEON_PURPLE)   # 日落渐变
GRADIENT_OCEAN = (NEON_BLUE, NEON_CYAN)         # 海洋渐变

# ================================
# 发光效果参数
# ================================

class GlowConfig:
    """霓虹发光配置"""
    
    # 发光强度等级
    GLOW_SOFT = {
        'blur': 5,
        'spread': 2,
        'opacity': 0.6
    }
    
    GLOW_MEDIUM = {
        'blur': 10,
        'spread': 3,
        'opacity': 0.8
    }
    
    GLOW_STRONG = {
        'blur': 15,
        'spread': 5,
        'opacity': 1.0
    }
    
    # 多层发光效果
    @staticmethod
    def get_multi_layer_glow(color: str, intensity: str = 'medium') -> list:
        """
        获取多层发光效果配置
        
        Args:
            color: 基础颜色
            intensity: 强度 ('soft', 'medium', 'strong')
        
        Returns:
            包含多层阴影配置的列表
        """
        configs = {
            'soft': [
                {'offset': (0, 0), 'blur': 5, 'color': color, 'opacity': 0.4},
                {'offset': (0, 0), 'blur': 10, 'color': color, 'opacity': 0.2},
            ],
            'medium': [
                {'offset': (0, 0), 'blur': 5, 'color': color, 'opacity': 0.6},
                {'offset': (0, 0), 'blur': 10, 'color': color, 'opacity': 0.4},
                {'offset': (0, 0), 'blur': 20, 'color': color, 'opacity': 0.2},
            ],
            'strong': [
                {'offset': (0, 0), 'blur': 5, 'color': color, 'opacity': 0.8},
                {'offset': (0, 0), 'blur': 10, 'color': color, 'opacity': 0.6},
                {'offset': (0, 0), 'blur': 20, 'color': color, 'opacity': 0.4},
                {'offset': (0, 0), 'blur': 30, 'color': color, 'opacity': 0.2},
            ]
        }
        return configs.get(intensity, configs['medium'])

# ================================
# 透明度变体
# ================================

def hex_to_rgba(hex_color: str, alpha: float) -> str:
    """
    将十六进制颜色转换为RGBA格式
    
    Args:
        hex_color: 十六进制颜色 (如 '#00f3ff')
        alpha: 透明度 (0.0-1.0)
    
    Returns:
        RGBA颜色字符串
    """
    hex_color = hex_color.lstrip('#')
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return f"rgba({r}, {g}, {b}, {alpha})"

# 预定义透明度变体
NEON_CYAN_10 = hex_to_rgba(NEON_CYAN, 0.1)
NEON_CYAN_20 = hex_to_rgba(NEON_CYAN, 0.2)
NEON_CYAN_50 = hex_to_rgba(NEON_CYAN, 0.5)
NEON_CYAN_80 = hex_to_rgba(NEON_CYAN, 0.8)

NEON_MAGENTA_10 = hex_to_rgba(NEON_MAGENTA, 0.1)
NEON_MAGENTA_20 = hex_to_rgba(NEON_MAGENTA, 0.2)
NEON_MAGENTA_50 = hex_to_rgba(NEON_MAGENTA, 0.5)

NEON_PURPLE_10 = hex_to_rgba(NEON_PURPLE, 0.1)
NEON_PURPLE_20 = hex_to_rgba(NEON_PURPLE, 0.2)
NEON_PURPLE_50 = hex_to_rgba(NEON_PURPLE, 0.5)

# ================================
# 配色方案组合
# ================================

class ColorScheme:
    """配色方案集合"""
    
    # 默认主题
    DEFAULT = {
        'primary': NEON_CYAN,
        'secondary': NEON_MAGENTA,
        'accent': NEON_PURPLE,
        'background': DEEP_SPACE,
        'surface': NIGHT_BLUE,
        'text_primary': GHOST_WHITE,
        'text_secondary': CYBER_GRAY,
        'border': SHADOW_GRAY,
        'success': SUCCESS_GREEN,
        'error': ERROR_RED,
        'warning': WARNING_ORANGE,
        'info': INFO_BLUE,
    }
    
    # 矩阵主题 (绿色为主)
    MATRIX = {
        'primary': NEON_GREEN,
        'secondary': NEON_CYAN,
        'accent': NEON_BLUE,
        'background': DEEP_SPACE,
        'surface': NIGHT_BLUE,
        'text_primary': GHOST_WHITE,
        'text_secondary': CYBER_GRAY,
        'border': SHADOW_GRAY,
        'success': SUCCESS_GREEN,
        'error': ERROR_RED,
        'warning': WARNING_ORANGE,
        'info': INFO_BLUE,
    }
    
    # 品红主题
    MAGENTA = {
        'primary': NEON_MAGENTA,
        'secondary': NEON_PURPLE,
        'accent': NEON_CYAN,
        'background': DEEP_SPACE,
        'surface': NIGHT_BLUE,
        'text_primary': GHOST_WHITE,
        'text_secondary': CYBER_GRAY,
        'border': SHADOW_GRAY,
        'success': SUCCESS_GREEN,
        'error': ERROR_RED,
        'warning': WARNING_ORANGE,
        'info': INFO_BLUE,
    }
    
    @staticmethod
    def get_scheme(name: str = 'default') -> Dict[str, str]:
        """
        获取指定配色方案
        
        Args:
            name: 方案名称 ('default', 'matrix', 'magenta')
        
        Returns:
            配色方案字典
        """
        schemes = {
            'default': ColorScheme.DEFAULT,
            'matrix': ColorScheme.MATRIX,
            'magenta': ColorScheme.MAGENTA,
        }
        return schemes.get(name.lower(), ColorScheme.DEFAULT)

# ================================
# Diff显示配色
# ================================

DIFF_COLORS = {
    'add': SUCCESS_GREEN,           # 添加的行
    'delete': ERROR_RED,            # 删除的行
    'context': CYBER_GRAY,          # 上下文行
    'header': NEON_CYAN,            # 文件头
    'hunk': NEON_PURPLE,            # Hunk头
    'background_add': hex_to_rgba(SUCCESS_GREEN, 0.1),     # 添加行背景
    'background_delete': hex_to_rgba(ERROR_RED, 0.1),      # 删除行背景
}

# ================================
# 工具函数
# ================================

def interpolate_color(color1: str, color2: str, ratio: float) -> str:
    """
    在两个颜色之间插值
    
    Args:
        color1: 起始颜色 (十六进制)
        color2: 结束颜色 (十六进制)
        ratio: 插值比例 (0.0-1.0)
    
    Returns:
        插值后的颜色 (十六进制)
    """
    c1 = color1.lstrip('#')
    c2 = color2.lstrip('#')
    
    r1, g1, b1 = int(c1[0:2], 16), int(c1[2:4], 16), int(c1[4:6], 16)
    r2, g2, b2 = int(c2[0:2], 16), int(c2[2:4], 16), int(c2[4:6], 16)
    
    r = int(r1 + (r2 - r1) * ratio)
    g = int(g1 + (g2 - g1) * ratio)
    b = int(b1 + (b2 - b1) * ratio)
    
    return f"#{r:02x}{g:02x}{b:02x}"

def get_gradient_colors(start: str, end: str, steps: int) -> list:
    """
    生成渐变色系列
    
    Args:
        start: 起始颜色
        end: 结束颜色
        steps: 渐变步数
    
    Returns:
        颜色列表
    """
    return [interpolate_color(start, end, i / (steps - 1)) for i in range(steps)]

def darken_color(color: str, amount: float = 0.2) -> str:
    """
    使颜色变暗
    
    Args:
        color: 原始颜色
        amount: 变暗程度 (0.0-1.0)
    
    Returns:
        变暗后的颜色
    """
    return interpolate_color(color, "#000000", amount)

def lighten_color(color: str, amount: float = 0.2) -> str:
    """
    使颜色变亮
    
    Args:
        color: 原始颜色
        amount: 变亮程度 (0.0-1.0)
    
    Returns:
        变亮后的颜色
    """
    return interpolate_color(color, "#ffffff", amount)

# ================================
# 测试和演示
# ================================

if __name__ == "__main__":
    print("🎨 赛博朋克配色系统")
    print("=" * 50)
    
    print("\n主色系:")
    print(f"  霓虹青: {NEON_CYAN}")
    print(f"  霓虹品红: {NEON_MAGENTA}")
    print(f"  霓虹紫: {NEON_PURPLE}")
    
    print("\n背景色系:")
    print(f"  深空黑: {DEEP_SPACE}")
    print(f"  暗黑虚空: {DARK_VOID}")
    print(f"  夜蓝: {NIGHT_BLUE}")
    
    print("\n功能色系:")
    print(f"  错误: {ERROR_RED}")
    print(f"  警告: {WARNING_ORANGE}")
    print(f"  成功: {SUCCESS_GREEN}")
    print(f"  信息: {INFO_BLUE}")
    
    print("\n渐变示例:")
    gradient = get_gradient_colors(NEON_CYAN, NEON_PURPLE, 5)
    for i, color in enumerate(gradient):
        print(f"  步骤 {i+1}: {color}")
    
    print("\n透明度变体:")
    print(f"  青色 50%: {NEON_CYAN_50}")
    print(f"  品红 50%: {NEON_MAGENTA_50}")
    
    print("\n配色方案:")
    for scheme_name in ['default', 'matrix', 'magenta']:
        scheme = ColorScheme.get_scheme(scheme_name)
        print(f"  {scheme_name.title()}: 主色={scheme['primary']}")