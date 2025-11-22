"""
特效管理器模块

提供统一的特效管理和控制。
"""

from typing import Dict, List, Optional, Any
import customtkinter as ctk
from .base import EffectBase


class EffectManager:
    """
    特效管理器
    
    统一管理和控制所有特效。
    
    使用示例:
        >>> manager = EffectManager(window)
        >>> manager.add_effect('scanlines', scanline_effect)
        >>> manager.add_effect('glow', glow_effect)
        >>> manager.start_all()
    """
    
    def __init__(self, parent: ctk.CTkBaseClass):
        """
        初始化特效管理器
        
        参数:
            parent: 父窗口
        """
        self.parent = parent
        self._effects: Dict[str, EffectBase] = {}
        self._groups: Dict[str, List[str]] = {}
    
    def add_effect(self, name: str, effect: EffectBase) -> None:
        """
        添加特效
        
        参数:
            name: 特效名称
            effect: 特效对象
        """
        self._effects[name] = effect
    
    def remove_effect(self, name: str) -> None:
        """
        移除特效
        
        参数:
            name: 特效名称
        """
        if name in self._effects:
            effect = self._effects[name]
            if effect.running:
                effect.stop()
            del self._effects[name]
    
    def get_effect(self, name: str) -> Optional[EffectBase]:
        """
        获取特效
        
        参数:
            name: 特效名称
        
        返回:
            特效对象或None
        """
        return self._effects.get(name)
    
    def start_effect(self, name: str) -> bool:
        """
        启动特效
        
        参数:
            name: 特效名称
        
        返回:
            是否成功
        """
        effect = self._effects.get(name)
        if effect:
            effect.start()
            return True
        return False
    
    def stop_effect(self, name: str) -> bool:
        """
        停止特效
        
        参数:
            name: 特效名称
        
        返回:
            是否成功
        """
        effect = self._effects.get(name)
        if effect:
            effect.stop()
            return True
        return False
    
    def toggle_effect(self, name: str) -> bool:
        """
        切换特效状态
        
        参数:
            name: 特效名称
        
        返回:
            是否成功
        """
        effect = self._effects.get(name)
        if effect:
            effect.toggle()
            return True
        return False
    
    def start_all(self) -> None:
        """启动所有特效"""
        for effect in self._effects.values():
            effect.start()
    
    def stop_all(self) -> None:
        """停止所有特效"""
        for effect in self._effects.values():
            effect.stop()
    
    def enable_effect(self, name: str) -> bool:
        """
        启用特效
        
        参数:
            name: 特效名称
        
        返回:
            是否成功
        """
        effect = self._effects.get(name)
        if effect:
            effect.enabled = True
            return True
        return False
    
    def disable_effect(self, name: str) -> bool:
        """
        禁用特效
        
        参数:
            name: 特效名称
        
        返回:
            是否成功
        """
        effect = self._effects.get(name)
        if effect:
            effect.enabled = False
            return True
        return False
    
    def is_running(self, name: str) -> bool:
        """
        检查特效是否运行中
        
        参数:
            name: 特效名称
        
        返回:
            是否运行中
        """
        effect = self._effects.get(name)
        return effect.running if effect else False
    
    def is_enabled(self, name: str) -> bool:
        """
        检查特效是否启用
        
        参数:
            name: 特效名称
        
        返回:
            是否启用
        """
        effect = self._effects.get(name)
        return effect.enabled if effect else False
    
    def list_effects(self) -> List[str]:
        """
        列出所有特效名称
        
        返回:
            特效名称列表
        """
        return list(self._effects.keys())
    
    def create_group(self, group_name: str, effect_names: List[str]) -> None:
        """
        创建特效组
        
        参数:
            group_name: 组名称
            effect_names: 特效名称列表
        """
        self._groups[group_name] = effect_names
    
    def start_group(self, group_name: str) -> bool:
        """
        启动特效组
        
        参数:
            group_name: 组名称
        
        返回:
            是否成功
        """
        if group_name not in self._groups:
            return False
        
        for name in self._groups[group_name]:
            self.start_effect(name)
        return True
    
    def stop_group(self, group_name: str) -> bool:
        """
        停止特效组
        
        参数:
            group_name: 组名称
        
        返回:
            是否成功
        """
        if group_name not in self._groups:
            return False
        
        for name in self._groups[group_name]:
            self.stop_effect(name)
        return True
    
    def get_status(self) -> Dict[str, Dict[str, Any]]:
        """
        获取所有特效状态
        
        返回:
            状态字典
        """
        status = {}
        for name, effect in self._effects.items():
            status[name] = {
                'enabled': effect.enabled,
                'running': effect.running,
                'type': type(effect).__name__
            }
        return status
    
    def clear(self) -> None:
        """清除所有特效"""
        self.stop_all()
        self._effects.clear()
        self._groups.clear()


class PresetManager:
    """
    预设管理器
    
    管理特效预设配置。
    
    使用示例:
        >>> preset_mgr = PresetManager(effect_manager)
        >>> preset_mgr.apply_preset('cyberpunk_full')
    """
    
    def __init__(self, effect_manager: EffectManager):
        """
        初始化预设管理器
        
        参数:
            effect_manager: 特效管理器
        """
        self.effect_manager = effect_manager
        self._presets: Dict[str, Dict[str, bool]] = {}
        self._init_default_presets()
    
    def _init_default_presets(self) -> None:
        """初始化默认预设"""
        # 完整赛博朋克效果
        self._presets['cyberpunk_full'] = {
            'scanlines': True,
            'glow': True,
            'glitch': True,
            'matrix_rain': True,
            'breathing': True,
            'particles': True
        }
        
        # 最小效果
        self._presets['minimal'] = {
            'scanlines': True,
            'glow': True,
            'glitch': False,
            'matrix_rain': False,
            'breathing': False,
            'particles': False
        }
        
        # 性能模式
        self._presets['performance'] = {
            'scanlines': True,
            'glow': False,
            'glitch': True,
            'matrix_rain': False,
            'breathing': True,
            'particles': False
        }
        
        # Matrix主题
        self._presets['matrix'] = {
            'scanlines': True,
            'glow': False,
            'glitch': True,
            'matrix_rain': True,
            'breathing': False,
            'particles': False
        }
        
        # 无特效
        self._presets['none'] = {
            'scanlines': False,
            'glow': False,
            'glitch': False,
            'matrix_rain': False,
            'breathing': False,
            'particles': False
        }
    
    def add_preset(self, name: str, config: Dict[str, bool]) -> None:
        """
        添加自定义预设
        
        参数:
            name: 预设名称
            config: 配置字典
        """
        self._presets[name] = config
    
    def remove_preset(self, name: str) -> None:
        """
        移除预设
        
        参数:
            name: 预设名称
        """
        if name in self._presets:
            del self._presets[name]
    
    def apply_preset(self, name: str) -> bool:
        """
        应用预设
        
        参数:
            name: 预设名称
        
        返回:
            是否成功
        """
        if name not in self._presets:
            return False
        
        config = self._presets[name]
        
        # 首先停止所有特效
        self.effect_manager.stop_all()
        
        # 根据配置启动特效
        for effect_name, should_enable in config.items():
            if should_enable:
                self.effect_manager.start_effect(effect_name)
            else:
                self.effect_manager.stop_effect(effect_name)
        
        return True
    
    def list_presets(self) -> List[str]:
        """
        列出所有预设
        
        返回:
            预设名称列表
        """
        return list(self._presets.keys())
    
    def get_preset_config(self, name: str) -> Optional[Dict[str, bool]]:
        """
        获取预设配置
        
        参数:
            name: 预设名称
        
        返回:
            配置字典或None
        """
        return self._presets.get(name)
    
    def save_current_as_preset(self, name: str) -> None:
        """
        将当前状态保存为预设
        
        参数:
            name: 预设名称
        """
        config = {}
        for effect_name in self.effect_manager.list_effects():
            config[effect_name] = self.effect_manager.is_running(effect_name)
        
        self._presets[name] = config


# 导出
__all__ = [
    'EffectManager',
    'PresetManager',
]