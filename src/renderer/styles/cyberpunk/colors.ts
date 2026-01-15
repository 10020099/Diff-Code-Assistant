/**
 * 赛博朋克配色系统
 * 从 Python 版本移植
 */

// ================================
// 主色系
// ================================

// 霓虹色系 - 主要UI元素
export const NEON_CYAN = '#00f3ff'           // 霓虹青 - 主色
export const NEON_MAGENTA = '#ff00e5'        // 霓虹品红 - 次色
export const NEON_PURPLE = '#b300ff'         // 霓虹紫 - 辅色
export const NEON_BLUE = '#0080ff'           // 霓虹蓝 - 辅助色
export const NEON_GREEN = '#00ff88'          // 霓虹绿 - 成功色

// 深色背景系
export const DEEP_SPACE = '#0a0e1a'          // 深空黑 - 主背景
export const DARK_VOID = '#151b2e'           // 暗黑虚空 - 次背景
export const NIGHT_BLUE = '#1a2332'          // 夜蓝 - 组件背景
export const SHADOW_GRAY = '#1e2738'         // 阴影灰 - 边框/分隔

// 中性色系 - 文本和辅助
export const CYBER_GRAY = '#8892b0'          // 赛博灰 - 次要文本
export const STEEL_BLUE = '#a8b2d1'          // 钢蓝 - 普通文本
export const GHOST_WHITE = '#e6f1ff'         // 幽灵白 - 主要文本
export const MUTED_CYAN = '#64ffda'          // 柔和青 - 高亮文本

// 功能色系
export const ERROR_RED = '#ff3366'           // 错误红
export const WARNING_ORANGE = '#ffaa00'      // 警告橙
export const SUCCESS_GREEN = '#00ff88'       // 成功绿
export const INFO_BLUE = '#00b8ff'           // 信息蓝

// ================================
// 渐变配色
// ================================

export const GRADIENT_CYBER = [NEON_CYAN, NEON_PURPLE]      // 赛博渐变
export const GRADIENT_MATRIX = [NEON_GREEN, NEON_CYAN]      // 矩阵渐变
export const GRADIENT_SUNSET = [NEON_MAGENTA, NEON_PURPLE]  // 日落渐变
export const GRADIENT_OCEAN = [NEON_BLUE, NEON_CYAN]        // 海洋渐变

// ================================
// 配色方案
// ================================

export interface ColorScheme {
  primary: string
  secondary: string
  accent: string
  background: string
  surface: string
  textPrimary: string
  textSecondary: string
  border: string
  success: string
  error: string
  warning: string
  info: string
}

export const DEFAULT_SCHEME: ColorScheme = {
  primary: NEON_CYAN,
  secondary: NEON_MAGENTA,
  accent: NEON_PURPLE,
  background: DEEP_SPACE,
  surface: NIGHT_BLUE,
  textPrimary: GHOST_WHITE,
  textSecondary: CYBER_GRAY,
  border: SHADOW_GRAY,
  success: SUCCESS_GREEN,
  error: ERROR_RED,
  warning: WARNING_ORANGE,
  info: INFO_BLUE
}

export const MATRIX_SCHEME: ColorScheme = {
  ...DEFAULT_SCHEME,
  primary: NEON_GREEN,
  secondary: NEON_CYAN,
  accent: NEON_BLUE
}

export const MAGENTA_SCHEME: ColorScheme = {
  ...DEFAULT_SCHEME,
  primary: NEON_MAGENTA,
  secondary: NEON_PURPLE,
  accent: NEON_CYAN
}

export const COLOR_SCHEMES: Record<string, ColorScheme> = {
  default: DEFAULT_SCHEME,
  matrix: MATRIX_SCHEME,
  magenta: MAGENTA_SCHEME
}

// ================================
// Diff 显示配色
// ================================

export const DIFF_COLORS = {
  add: SUCCESS_GREEN,
  delete: ERROR_RED,
  context: CYBER_GRAY,
  header: NEON_CYAN,
  hunk: NEON_PURPLE,
  backgroundAdd: 'rgba(0, 255, 136, 0.1)',
  backgroundDelete: 'rgba(255, 51, 102, 0.1)'
}

// ================================
// 工具函数
// ================================

/**
 * 将十六进制颜色转换为 RGBA
 */
export function hexToRgba(hex: string, alpha: number): string {
  const cleanHex = hex.replace('#', '')
  const r = parseInt(cleanHex.slice(0, 2), 16)
  const g = parseInt(cleanHex.slice(2, 4), 16)
  const b = parseInt(cleanHex.slice(4, 6), 16)
  return `rgba(${r}, ${g}, ${b}, ${alpha})`
}

/**
 * 在两个颜色之间插值
 */
export function interpolateColor(color1: string, color2: string, ratio: number): string {
  const c1 = color1.replace('#', '')
  const c2 = color2.replace('#', '')

  const r1 = parseInt(c1.slice(0, 2), 16)
  const g1 = parseInt(c1.slice(2, 4), 16)
  const b1 = parseInt(c1.slice(4, 6), 16)

  const r2 = parseInt(c2.slice(0, 2), 16)
  const g2 = parseInt(c2.slice(2, 4), 16)
  const b2 = parseInt(c2.slice(4, 6), 16)

  const r = Math.round(r1 + (r2 - r1) * ratio)
  const g = Math.round(g1 + (g2 - g1) * ratio)
  const b = Math.round(b1 + (b2 - b1) * ratio)

  return `#${r.toString(16).padStart(2, '0')}${g.toString(16).padStart(2, '0')}${b.toString(16).padStart(2, '0')}`
}

/**
 * 使颜色变暗
 */
export function darkenColor(color: string, amount: number = 0.2): string {
  return interpolateColor(color, '#000000', amount)
}

/**
 * 使颜色变亮
 */
export function lightenColor(color: string, amount: number = 0.2): string {
  return interpolateColor(color, '#ffffff', amount)
}

/**
 * 生成渐变色系列
 */
export function getGradientColors(start: string, end: string, steps: number): string[] {
  return Array.from({ length: steps }, (_, i) => 
    interpolateColor(start, end, i / (steps - 1))
  )
}

/**
 * 生成霓虹发光 CSS
 */
export function getNeonGlow(color: string, intensity: 'soft' | 'medium' | 'strong' = 'medium'): string {
  const configs = {
    soft: `0 0 5px ${color}, 0 0 10px ${hexToRgba(color, 0.5)}`,
    medium: `0 0 5px ${color}, 0 0 10px ${color}, 0 0 20px ${hexToRgba(color, 0.5)}`,
    strong: `0 0 5px ${color}, 0 0 10px ${color}, 0 0 20px ${color}, 0 0 30px ${hexToRgba(color, 0.5)}`
  }
  return configs[intensity]
}
