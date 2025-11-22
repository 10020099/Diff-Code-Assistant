"""
验证工具函数
提供各种数据验证功能
"""

import re
from typing import Tuple, Optional

# ================================
# 颜色验证
# ================================

def validate_hex_color(color: str) -> bool:
    """
    验证十六进制颜色格式
    
    Args:
        color: 颜色字符串 (如 '#00f3ff' 或 '00f3ff')
    
    Returns:
        是否有效
    """
    if not color:
        return False
    
    # 移除可能的 # 前缀
    color = color.lstrip('#')
    
    # 检查长度和字符
    if len(color) not in [3, 6]:
        return False
    
    return bool(re.match(r'^[0-9a-fA-F]+$', color))

def validate_rgb(r: int, g: int, b: int) -> bool:
    """
    验证RGB颜色值
    
    Args:
        r: 红色通道 (0-255)
        g: 绿色通道 (0-255)
        b: 蓝色通道 (0-255)
    
    Returns:
        是否有效
    """
    return all(0 <= val <= 255 for val in [r, g, b])

def validate_rgba(r: int, g: int, b: int, a: float) -> bool:
    """
    验证RGBA颜色值
    
    Args:
        r: 红色通道 (0-255)
        g: 绿色通道 (0-255)
        b: 蓝色通道 (0-255)
        a: 透明度 (0.0-1.0)
    
    Returns:
        是否有效
    """
    return validate_rgb(r, g, b) and 0.0 <= a <= 1.0

def parse_hex_color(color: str) -> Optional[Tuple[int, int, int]]:
    """
    解析十六进制颜色为RGB
    
    Args:
        color: 十六进制颜色
    
    Returns:
        RGB元组或None
    """
    if not validate_hex_color(color):
        return None
    
    color = color.lstrip('#')
    
    # 处理短格式 (如 #abc -> #aabbcc)
    if len(color) == 3:
        color = ''.join([c * 2 for c in color])
    
    try:
        r = int(color[0:2], 16)
        g = int(color[2:4], 16)
        b = int(color[4:6], 16)
        return (r, g, b)
    except ValueError:
        return None

# ================================
# 数值验证
# ================================

def validate_range(value: float, min_val: float, max_val: float) -> bool:
    """
    验证数值是否在范围内
    
    Args:
        value: 要验证的值
        min_val: 最小值
        max_val: 最大值
    
    Returns:
        是否在范围内
    """
    return min_val <= value <= max_val

def clamp(value: float, min_val: float, max_val: float) -> float:
    """
    限制数值在范围内
    
    Args:
        value: 原始值
        min_val: 最小值
        max_val: 最大值
    
    Returns:
        限制后的值
    """
    return max(min_val, min(max_val, value))

def normalize(value: float, min_val: float, max_val: float) -> float:
    """
    归一化数值到0-1范围
    
    Args:
        value: 原始值
        min_val: 最小值
        max_val: 最大值
    
    Returns:
        归一化后的值 (0.0-1.0)
    """
    if max_val == min_val:
        return 0.0
    return (value - min_val) / (max_val - min_val)

# ================================
# 字符串验证
# ================================

def validate_not_empty(text: str) -> bool:
    """验证字符串非空"""
    return bool(text and text.strip())

def validate_length(text: str, min_len: int = 0, max_len: int = None) -> bool:
    """
    验证字符串长度
    
    Args:
        text: 文本
        min_len: 最小长度
        max_len: 最大长度
    
    Returns:
        是否满足长度要求
    """
    length = len(text)
    if length < min_len:
        return False
    if max_len is not None and length > max_len:
        return False
    return True

# ================================
# 测试代码
# ================================

if __name__ == "__main__":
    print("✅ 验证工具函数测试")
    print("=" * 50)
    
    # 测试颜色验证
    print("\n颜色验证测试:")
    test_colors = [
        "#00f3ff",  # 有效
        "00f3ff",   # 有效
        "#abc",     # 有效 (短格式)
        "abc",      # 有效 (短格式)
        "#gggggg",  # 无效
        "12345",    # 无效
    ]
    for color in test_colors:
        valid = validate_hex_color(color)
        rgb = parse_hex_color(color)
        print(f"  {color:12} -> 有效: {valid}, RGB: {rgb}")
    
    # 测试RGB验证
    print("\nRGB验证测试:")
    test_rgb = [
        (0, 243, 255),    # 有效
        (255, 0, 229),    # 有效
        (256, 0, 0),      # 无效
        (-1, 100, 100),   # 无效
    ]
    for r, g, b in test_rgb:
        valid = validate_rgb(r, g, b)
        print(f"  RGB({r:3}, {g:3}, {b:3}) -> {valid}")
    
    # 测试数值验证
    print("\n数值验证测试:")
    print(f"  10在[0,100]内: {validate_range(10, 0, 100)}")
    print(f"  150在[0,100]内: {validate_range(150, 0, 100)}")
    print(f"  限制150到[0,100]: {clamp(150, 0, 100)}")
    print(f"  归一化50在[0,100]: {normalize(50, 0, 100)}")
    
    print("\n✅ 验证工具函数测试完成")