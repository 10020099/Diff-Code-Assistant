"""
赛博朋克主题管理系统
管理整体UI主题配置、字体、间距等
"""

import customtkinter as ctk
from typing import Dict, Any, Optional
from . import colors

# ================================
# 字体配置
# ================================

class Fonts:
    """字体配置类"""
    
    # 等宽字体系列 (优先级从高到低)
    MONOSPACE_FAMILIES = [
        "Consolas",
        "Monaco", 
        "Courier New",
        "monospace"
    ]
    
    # 无衬线字体系列
    SANS_SERIF_FAMILIES = [
        "Segoe UI",
        "Arial",
        "Helvetica",
        "sans-serif"
    ]
    
    # 字体大小
    SIZE_SMALL = 10
    SIZE_NORMAL = 12
    SIZE_MEDIUM = 14
    SIZE_LARGE = 16
    SIZE_XLARGE = 20
    SIZE_TITLE = 24
    
    @staticmethod
    def get_monospace(size: int = SIZE_NORMAL, weight: str = "normal") -> tuple:
        """获取等宽字体配置"""
        return (Fonts.MONOSPACE_FAMILIES[0], size, weight)
    
    @staticmethod
    def get_sans_serif(size: int = SIZE_NORMAL, weight: str = "normal") -> tuple:
        """获取无衬线字体配置"""
        return (Fonts.SANS_SERIF_FAMILIES[0], size, weight)
    
    @staticmethod
    def get_ctk_font(size: int = SIZE_NORMAL, weight: str = "normal", 
                     family: str = "sans") -> ctk.CTkFont:
        """获取CustomTkinter字体对象"""
        if family == "mono":
            return ctk.CTkFont(family=Fonts.MONOSPACE_FAMILIES[0], size=size, weight=weight)
        else:
            return ctk.CTkFont(family=Fonts.SANS_SERIF_FAMILIES[0], size=size, weight=weight)

# ================================
# 间距和尺寸配置
# ================================

class Spacing:
    """间距配置类"""
    
    # 基础间距单位
    UNIT = 4
    
    # 预定义间距
    XS = UNIT * 1      # 4px
    SM = UNIT * 2      # 8px
    MD = UNIT * 3      # 12px
    LG = UNIT * 4      # 16px
    XL = UNIT * 6      # 24px
    XXL = UNIT * 8     # 32px
    
    # 组件内边距
    PADDING_SM = (SM, SM)
    PADDING_MD = (MD, MD)
    PADDING_LG = (LG, LG)
    
    # 组件外边距
    MARGIN_SM = SM
    MARGIN_MD = MD
    MARGIN_LG = LG

class Dimensions:
    """尺寸配置类"""
    
    # 边框宽度
    BORDER_THIN = 1
    BORDER_NORMAL = 2
    BORDER_THICK = 3
    
    # 圆角半径
    RADIUS_NONE = 0
    RADIUS_SM = 4
    RADIUS_MD = 8
    RADIUS_LG = 12
    RADIUS_XL = 16
    RADIUS_FULL = 999
    
    # 按钮高度
    BUTTON_SM = 28
    BUTTON_MD = 36
    BUTTON_LG = 44
    
    # 输入框高度
    INPUT_SM = 28
    INPUT_MD = 36
    INPUT_LG = 44
    
    # 滚动条宽度
    SCROLLBAR_WIDTH = 12

# ================================
# 阴影和特效配置
# ================================

class Effects:
    """特效配置类"""
    
    # 阴影配置
    SHADOW_SM = {
        'offset': (0, 2),
        'blur': 4,
        'color': colors.hex_to_rgba(colors.DEEP_SPACE, 0.3)
    }
    
    SHADOW_MD = {
        'offset': (0, 4),
        'blur': 8,
        'color': colors.hex_to_rgba(colors.DEEP_SPACE, 0.4)
    }
    
    SHADOW_LG = {
        'offset': (0, 8),
        'blur': 16,
        'color': colors.hex_to_rgba(colors.DEEP_SPACE, 0.5)
    }
    
    # 霓虹发光效果
    NEON_GLOW = colors.GlowConfig.GLOW_MEDIUM
    
    # 悬停效果配置
    HOVER_SCALE = 1.05
    HOVER_BRIGHTNESS = 1.2
    
    # 动画配置
    ANIMATION_FAST = 150      # 毫秒
    ANIMATION_NORMAL = 300
    ANIMATION_SLOW = 500

# ================================
# 主题类
# ================================

class CyberpunkTheme:
    """赛博朋克主题管理器"""
    
    def __init__(self, scheme_name: str = 'default'):
        """
        初始化主题
        
        Args:
            scheme_name: 配色方案名称
        """
        self.scheme_name = scheme_name
        self.color_scheme = colors.ColorScheme.get_scheme(scheme_name)
        self._apply_ctk_theme()
    
    def _apply_ctk_theme(self):
        """应用CustomTkinter主题配置"""
        # 设置外观模式为深色
        ctk.set_appearance_mode("dark")
        
        # 注意: CustomTkinter的主题系统比较固定
        # 我们主要通过组件级别的配置来实现赛博朋克风格
    
    def get_button_style(self, variant: str = 'primary') -> Dict[str, Any]:
        """
        获取按钮样式配置
        
        Args:
            variant: 按钮变体 ('primary', 'secondary', 'success', 'danger')
        
        Returns:
            样式配置字典
        """
        base_style = {
            'corner_radius': Dimensions.RADIUS_MD,
            'border_width': Dimensions.BORDER_NORMAL,
            'font': Fonts.get_ctk_font(Fonts.SIZE_NORMAL, "bold"),
            'height': Dimensions.BUTTON_MD,
        }
        
        variants = {
            'primary': {
                'fg_color': self.color_scheme['primary'],
                'hover_color': colors.lighten_color(self.color_scheme['primary'], 0.1),
                'border_color': self.color_scheme['primary'],
                'text_color': colors.DEEP_SPACE,
            },
            'secondary': {
                'fg_color': self.color_scheme['surface'],
                'hover_color': colors.lighten_color(self.color_scheme['surface'], 0.1),
                'border_color': self.color_scheme['secondary'],
                'text_color': self.color_scheme['text_primary'],
            },
            'success': {
                'fg_color': self.color_scheme['success'],
                'hover_color': colors.lighten_color(self.color_scheme['success'], 0.1),
                'border_color': self.color_scheme['success'],
                'text_color': colors.DEEP_SPACE,
            },
            'danger': {
                'fg_color': self.color_scheme['error'],
                'hover_color': colors.lighten_color(self.color_scheme['error'], 0.1),
                'border_color': self.color_scheme['error'],
                'text_color': colors.GHOST_WHITE,
            },
            'ghost': {
                'fg_color': 'transparent',
                'hover_color': colors.hex_to_rgba(self.color_scheme['primary'], 0.1),
                'border_color': self.color_scheme['primary'],
                'text_color': self.color_scheme['primary'],
            }
        }
        
        style = base_style.copy()
        style.update(variants.get(variant, variants['primary']))
        return style
    
    def get_entry_style(self) -> Dict[str, Any]:
        """获取输入框样式配置"""
        return {
            'fg_color': self.color_scheme['surface'],
            'border_color': self.color_scheme['border'],
            'text_color': self.color_scheme['text_primary'],
            'placeholder_text_color': self.color_scheme['text_secondary'],
            'corner_radius': Dimensions.RADIUS_SM,
            'border_width': Dimensions.BORDER_NORMAL,
            'height': Dimensions.INPUT_MD,
            'font': Fonts.get_ctk_font(Fonts.SIZE_NORMAL),
        }
    
    def get_frame_style(self, variant: str = 'default') -> Dict[str, Any]:
        """
        获取框架样式配置
        
        Args:
            variant: 框架变体 ('default', 'card', 'panel')
        """
        variants = {
            'default': {
                'fg_color': self.color_scheme['surface'],
                'corner_radius': Dimensions.RADIUS_MD,
                'border_width': 0,
            },
            'card': {
                'fg_color': self.color_scheme['surface'],
                'corner_radius': Dimensions.RADIUS_LG,
                'border_width': Dimensions.BORDER_THIN,
                'border_color': self.color_scheme['border'],
            },
            'panel': {
                'fg_color': colors.hex_to_rgba(self.color_scheme['surface'], 0.5),
                'corner_radius': Dimensions.RADIUS_MD,
                'border_width': Dimensions.BORDER_THIN,
                'border_color': colors.hex_to_rgba(self.color_scheme['primary'], 0.3),
            },
            'highlight': {
                'fg_color': self.color_scheme['surface'],
                'corner_radius': Dimensions.RADIUS_MD,
                'border_width': Dimensions.BORDER_NORMAL,
                'border_color': self.color_scheme['primary'],
            }
        }
        
        return variants.get(variant, variants['default'])
    
    def get_textbox_style(self) -> Dict[str, Any]:
        """获取文本框样式配置"""
        return {
            'fg_color': self.color_scheme['surface'],
            'text_color': self.color_scheme['text_primary'],
            'border_color': self.color_scheme['border'],
            'corner_radius': Dimensions.RADIUS_SM,
            'border_width': Dimensions.BORDER_NORMAL,
            'font': Fonts.get_ctk_font(Fonts.SIZE_NORMAL, family="mono"),
        }
    
    def get_label_style(self, variant: str = 'normal') -> Dict[str, Any]:
        """
        获取标签样式配置
        
        Args:
            variant: 标签变体 ('normal', 'title', 'subtitle', 'caption')
        """
        variants = {
            'normal': {
                'text_color': self.color_scheme['text_primary'],
                'font': Fonts.get_ctk_font(Fonts.SIZE_NORMAL),
            },
            'title': {
                'text_color': self.color_scheme['primary'],
                'font': Fonts.get_ctk_font(Fonts.SIZE_TITLE, "bold"),
            },
            'subtitle': {
                'text_color': self.color_scheme['text_primary'],
                'font': Fonts.get_ctk_font(Fonts.SIZE_LARGE, "bold"),
            },
            'caption': {
                'text_color': self.color_scheme['text_secondary'],
                'font': Fonts.get_ctk_font(Fonts.SIZE_SMALL),
            },
            'highlight': {
                'text_color': self.color_scheme['primary'],
                'font': Fonts.get_ctk_font(Fonts.SIZE_NORMAL, "bold"),
            }
        }
        
        return variants.get(variant, variants['normal'])
    
    def get_checkbox_style(self) -> Dict[str, Any]:
        """获取复选框样式配置"""
        return {
            'fg_color': self.color_scheme['primary'],
            'hover_color': colors.lighten_color(self.color_scheme['primary'], 0.1),
            'border_color': self.color_scheme['border'],
            'text_color': self.color_scheme['text_primary'],
            'corner_radius': Dimensions.RADIUS_SM,
            'border_width': Dimensions.BORDER_NORMAL,
            'font': Fonts.get_ctk_font(Fonts.SIZE_NORMAL),
        }
    
    def get_progressbar_style(self) -> Dict[str, Any]:
        """获取进度条样式配置"""
        return {
            'fg_color': self.color_scheme['surface'],
            'progress_color': self.color_scheme['primary'],
            'corner_radius': Dimensions.RADIUS_FULL,
            'border_width': 0,
            'height': 8,
        }
    
    def get_tabview_style(self) -> Dict[str, Any]:
        """获取选项卡样式配置"""
        return {
            'fg_color': self.color_scheme['surface'],
            'segmented_button_fg_color': self.color_scheme['background'],
            'segmented_button_selected_color': self.color_scheme['primary'],
            'segmented_button_selected_hover_color': colors.lighten_color(self.color_scheme['primary'], 0.1),
            'segmented_button_unselected_color': self.color_scheme['surface'],
            'segmented_button_unselected_hover_color': colors.lighten_color(self.color_scheme['surface'], 0.1),
            'text_color': self.color_scheme['text_primary'],
            'text_color_disabled': self.color_scheme['text_secondary'],
            'corner_radius': Dimensions.RADIUS_MD,
            'border_width': 0,
        }
    
    def get_scrollbar_style(self) -> Dict[str, Any]:
        """获取滚动条样式配置"""
        return {
            'fg_color': self.color_scheme['surface'],
            'button_color': self.color_scheme['border'],
            'button_hover_color': self.color_scheme['primary'],
            'corner_radius': Dimensions.RADIUS_SM,
        }
    
    def switch_scheme(self, scheme_name: str):
        """
        切换配色方案
        
        Args:
            scheme_name: 新的配色方案名称
        """
        self.scheme_name = scheme_name
        self.color_scheme = colors.ColorScheme.get_scheme(scheme_name)
        self._apply_ctk_theme()

# ================================
# 全局主题实例
# ================================

# 默认主题实例
_default_theme: Optional[CyberpunkTheme] = None

def get_theme(scheme_name: str = 'default') -> CyberpunkTheme:
    """
    获取主题实例 (单例模式)
    
    Args:
        scheme_name: 配色方案名称
    
    Returns:
        主题实例
    """
    global _default_theme
    if _default_theme is None or _default_theme.scheme_name != scheme_name:
        _default_theme = CyberpunkTheme(scheme_name)
    return _default_theme

def apply_widget_style(widget: ctk.CTkBaseClass, style: Dict[str, Any]):
    """
    应用样式到组件
    
    Args:
        widget: CTk组件实例
        style: 样式配置字典
    """
    for key, value in style.items():
        try:
            widget.configure(**{key: value})
        except Exception as e:
            print(f"警告: 无法应用样式属性 {key}: {e}")

# ================================
# 测试和演示
# ================================

if __name__ == "__main__":
    print("🎨 赛博朋克主题系统")
    print("=" * 50)
    
    # 创建主题实例
    theme = get_theme('default')
    
    print("\n字体配置:")
    print(f"  等宽字体: {Fonts.MONOSPACE_FAMILIES[0]}")
    print(f"  无衬线字体: {Fonts.SANS_SERIF_FAMILIES[0]}")
    print(f"  普通大小: {Fonts.SIZE_NORMAL}px")
    
    print("\n间距配置:")
    print(f"  小间距: {Spacing.SM}px")
    print(f"  中等间距: {Spacing.MD}px")
    print(f"  大间距: {Spacing.LG}px")
    
    print("\n尺寸配置:")
    print(f"  边框: {Dimensions.BORDER_NORMAL}px")
    print(f"  圆角: {Dimensions.RADIUS_MD}px")
    print(f"  按钮高度: {Dimensions.BUTTON_MD}px")
    
    print("\n按钮样式变体:")
    for variant in ['primary', 'secondary', 'success', 'danger', 'ghost']:
        style = theme.get_button_style(variant)
        print(f"  {variant}: {style['fg_color']}")
    
    print("\n框架样式变体:")
    for variant in ['default', 'card', 'panel', 'highlight']:
        style = theme.get_frame_style(variant)
        print(f"  {variant}: 圆角={style['corner_radius']}px")
    
    print("\n✅ 主题系统测试完成")