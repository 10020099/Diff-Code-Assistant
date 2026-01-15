/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './src/renderer/**/*.{js,ts,jsx,tsx,html}',
  ],
  theme: {
    extend: {
      colors: {
        // 霓虹色系 - 主要UI元素
        'neon-cyan': '#00f3ff',
        'neon-magenta': '#ff00e5',
        'neon-purple': '#b300ff',
        'neon-blue': '#0080ff',
        'neon-green': '#00ff88',
        
        // 深色背景系
        'deep-space': '#0a0e1a',
        'dark-void': '#151b2e',
        'night-blue': '#1a2332',
        'shadow-gray': '#1e2738',
        
        // 中性色系
        'cyber-gray': '#8892b0',
        'steel-blue': '#a8b2d1',
        'ghost-white': '#e6f1ff',
        'muted-cyan': '#64ffda',
        
        // 功能色系
        'error-red': '#ff3366',
        'warning-orange': '#ffaa00',
        'success-green': '#00ff88',
        'info-blue': '#00b8ff',
      },
      fontFamily: {
        mono: ['Consolas', 'Monaco', 'Courier New', 'monospace'],
        sans: ['Segoe UI', 'Arial', 'Helvetica', 'sans-serif'],
      },
      boxShadow: {
        'neon-cyan': '0 0 5px #00f3ff, 0 0 10px #00f3ff, 0 0 20px #00f3ff',
        'neon-magenta': '0 0 5px #ff00e5, 0 0 10px #ff00e5, 0 0 20px #ff00e5',
        'neon-purple': '0 0 5px #b300ff, 0 0 10px #b300ff, 0 0 20px #b300ff',
        'neon-green': '0 0 5px #00ff88, 0 0 10px #00ff88, 0 0 20px #00ff88',
      },
      animation: {
        'pulse-neon': 'pulse-neon 2s ease-in-out infinite',
        'glow': 'glow 2s ease-in-out infinite alternate',
        'scanline': 'scanline 8s linear infinite',
        'glitch': 'glitch 0.3s ease-in-out infinite',
        'matrix-rain': 'matrix-rain 20s linear infinite',
      },
      keyframes: {
        'pulse-neon': {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.5' },
        },
        'glow': {
          '0%': { boxShadow: '0 0 5px currentColor, 0 0 10px currentColor' },
          '100%': { boxShadow: '0 0 10px currentColor, 0 0 20px currentColor, 0 0 30px currentColor' },
        },
        'scanline': {
          '0%': { transform: 'translateY(-100%)' },
          '100%': { transform: 'translateY(100vh)' },
        },
        'glitch': {
          '0%, 100%': { transform: 'translate(0)' },
          '20%': { transform: 'translate(-2px, 2px)' },
          '40%': { transform: 'translate(-2px, -2px)' },
          '60%': { transform: 'translate(2px, 2px)' },
          '80%': { transform: 'translate(2px, -2px)' },
        },
      },
    },
  },
  plugins: [],
}
