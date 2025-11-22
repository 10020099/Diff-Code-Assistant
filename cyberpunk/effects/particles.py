"""
粒子系统模块

提供交互式粒子特效。
"""

from typing import Optional, List, Tuple
import random
import math
import customtkinter as ctk
from .base import CanvasEffect


class Particle:
    """
    单个粒子
    
    表示粒子系统中的一个粒子。
    """
    
    def __init__(
        self,
        x: float,
        y: float,
        vx: float,
        vy: float,
        size: float,
        color: str,
        lifetime: int
    ):
        """
        初始化粒子
        
        参数:
            x: X坐标
            y: Y坐标
            vx: X方向速度
            vy: Y方向速度
            size: 粒子大小
            color: 颜色
            lifetime: 生命周期(帧数)
        """
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.size = size
        self.color = color
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.age = 0
    
    def update(self, gravity: float = 0.0, friction: float = 0.99) -> None:
        """
        更新粒子状态
        
        参数:
            gravity: 重力加速度
            friction: 摩擦系数
        """
        # 应用速度
        self.x += self.vx
        self.y += self.vy
        
        # 应用重力
        self.vy += gravity
        
        # 应用摩擦
        self.vx *= friction
        self.vy *= friction
        
        # 增加年龄
        self.age += 1
    
    def is_alive(self) -> bool:
        """
        检查粒子是否存活
        
        返回:
            是否存活
        """
        return self.age < self.lifetime
    
    def get_alpha(self) -> float:
        """
        获取当前透明度
        
        返回:
            透明度(0.0-1.0)
        """
        return 1.0 - (self.age / self.lifetime)


class ParticleSystem(CanvasEffect):
    """
    粒子系统
    
    提供交互式粒子特效,支持鼠标跟随和点击爆炸。
    
    使用示例:
        >>> particles = ParticleSystem(window, color="#00ffff")
        >>> particles.start()
    """
    
    def __init__(
        self,
        parent: ctk.CTkBaseClass,
        color: str = "#00ffff",
        particle_size: float = 3.0,
        gravity: float = 0.1,
        friction: float = 0.98,
        particle_lifetime: int = 60,
        spawn_rate: int = 5,
        fps: int = 60,
        enabled: bool = True,
        canvas: Optional[ctk.CTkCanvas] = None
    ):
        """
        初始化粒子系统
        
        参数:
            parent: 父窗口
            color: 粒子颜色
            particle_size: 粒子大小
            gravity: 重力
            friction: 摩擦系数
            particle_lifetime: 粒子生命周期
            spawn_rate: 生成速率(粒子/帧)
            fps: 帧率
            enabled: 是否启用
            canvas: 自定义Canvas
        """
        super().__init__(parent, fps, enabled, canvas)
        
        self.color = color
        self.particle_size = particle_size
        self.gravity = gravity
        self.friction = friction
        self.particle_lifetime = particle_lifetime
        self.spawn_rate = spawn_rate
        
        self._particles: List[Particle] = []
        self._mouse_x = 0
        self._mouse_y = 0
        self._is_mouse_pressed = False
        
        # 绑定鼠标事件
        self.canvas.bind('<Motion>', self._on_mouse_move)
        self.canvas.bind('<Button-1>', self._on_mouse_press)
        self.canvas.bind('<ButtonRelease-1>', self._on_mouse_release)
    
    def _create_canvas(self) -> ctk.CTkCanvas:
        """创建透明Canvas"""
        canvas = ctk.CTkCanvas(
            self.parent,
            bg='',
            highlightthickness=0
        )
        canvas.place(relx=0, rely=0, relwidth=1, relheight=1)
        return canvas
    
    def _on_mouse_move(self, event) -> None:
        """处理鼠标移动"""
        self._mouse_x = event.x
        self._mouse_y = event.y
    
    def _on_mouse_press(self, event) -> None:
        """处理鼠标按下"""
        self._is_mouse_pressed = True
        self._mouse_x = event.x
        self._mouse_y = event.y
        
        # 触发爆炸效果
        self._create_explosion(event.x, event.y, 50)
    
    def _on_mouse_release(self, event) -> None:
        """处理鼠标释放"""
        self._is_mouse_pressed = False
    
    def draw(self) -> None:
        """绘制粒子"""
        # 清空画布
        self.clear_canvas()
        
        # 生成新粒子
        if self._is_mouse_pressed:
            self._spawn_particles(self._mouse_x, self._mouse_y, self.spawn_rate)
        
        # 更新所有粒子
        alive_particles = []
        for particle in self._particles:
            particle.update(self.gravity, self.friction)
            
            if particle.is_alive():
                self._draw_particle(particle)
                alive_particles.append(particle)
        
        self._particles = alive_particles
    
    def _spawn_particles(self, x: float, y: float, count: int) -> None:
        """
        生成粒子
        
        参数:
            x: X坐标
            y: Y坐标
            count: 数量
        """
        for _ in range(count):
            # 随机速度
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1, 5)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            
            # 随机大小
            size = self.particle_size * random.uniform(0.5, 1.5)
            
            # 创建粒子
            particle = Particle(
                x=x,
                y=y,
                vx=vx,
                vy=vy,
                size=size,
                color=self.color,
                lifetime=self.particle_lifetime
            )
            self._particles.append(particle)
    
    def _create_explosion(self, x: float, y: float, count: int) -> None:
        """
        创建爆炸效果
        
        参数:
            x: X坐标
            y: Y坐标
            count: 粒子数量
        """
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(3, 10)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            
            size = self.particle_size * random.uniform(0.8, 2.0)
            
            particle = Particle(
                x=x,
                y=y,
                vx=vx,
                vy=vy,
                size=size,
                color=self.color,
                lifetime=int(self.particle_lifetime * 1.5)
            )
            self._particles.append(particle)
    
    def _draw_particle(self, particle: Particle) -> None:
        """
        绘制单个粒子
        
        参数:
            particle: 粒子对象
        """
        alpha = particle.get_alpha()
        
        # 计算带透明度的颜色
        if len(particle.color) == 7:  # #RRGGBB
            r = int(particle.color[1:3], 16)
            g = int(particle.color[3:5], 16)
            b = int(particle.color[5:7], 16)
            
            r = int(r * alpha)
            g = int(g * alpha)
            b = int(b * alpha)
            
            color = f"#{r:02x}{g:02x}{b:02x}"
        else:
            color = particle.color
        
        # 绘制粒子(圆形)
        x1 = particle.x - particle.size
        y1 = particle.y - particle.size
        x2 = particle.x + particle.size
        y2 = particle.y + particle.size
        
        self.canvas.create_oval(
            x1, y1, x2, y2,
            fill=color,
            outline='',
            tags='particle'
        )
    
    def clear_particles(self) -> None:
        """清除所有粒子"""
        self._particles.clear()
    
    def set_color(self, color: str) -> None:
        """
        设置粒子颜色
        
        参数:
            color: 颜色值
        """
        self.color = color


class TrailEffect(CanvasEffect):
    """
    轨迹特效
    
    鼠标移动时产生拖尾粒子。
    
    使用示例:
        >>> trail = TrailEffect(window, color="#ff00ff", trail_length=20)
        >>> trail.start()
    """
    
    def __init__(
        self,
        parent: ctk.CTkBaseClass,
        color: str = "#00ffff",
        trail_length: int = 20,
        particle_size: float = 2.0,
        fade_speed: float = 0.05,
        fps: int = 60,
        enabled: bool = True,
        canvas: Optional[ctk.CTkCanvas] = None
    ):
        """
        初始化轨迹特效
        
        参数:
            parent: 父窗口
            color: 颜色
            trail_length: 轨迹长度
            particle_size: 粒子大小
            fade_speed: 淡出速度
            fps: 帧率
            enabled: 是否启用
            canvas: 自定义Canvas
        """
        super().__init__(parent, fps, enabled, canvas)
        
        self.color = color
        self.trail_length = trail_length
        self.particle_size = particle_size
        self.fade_speed = fade_speed
        
        self._trail_points: List[Tuple[float, float, float]] = []  # (x, y, alpha)
        self._mouse_x = 0
        self._mouse_y = 0
        
        self.canvas.bind('<Motion>', self._on_mouse_move)
    
    def _create_canvas(self) -> ctk.CTkCanvas:
        """创建透明Canvas"""
        canvas = ctk.CTkCanvas(
            self.parent,
            bg='',
            highlightthickness=0
        )
        canvas.place(relx=0, rely=0, relwidth=1, relheight=1)
        return canvas
    
    def _on_mouse_move(self, event) -> None:
        """处理鼠标移动"""
        self._mouse_x = event.x
        self._mouse_y = event.y
        
        # 添加新点
        self._trail_points.append((event.x, event.y, 1.0))
        
        # 限制长度
        if len(self._trail_points) > self.trail_length:
            self._trail_points.pop(0)
    
    def draw(self) -> None:
        """绘制轨迹"""
        self.clear_canvas()
        
        # 更新所有点的透明度
        updated_points = []
        for x, y, alpha in self._trail_points:
            new_alpha = alpha - self.fade_speed
            if new_alpha > 0:
                updated_points.append((x, y, new_alpha))
        self._trail_points = updated_points
        
        # 绘制轨迹
        for i, (x, y, alpha) in enumerate(self._trail_points):
            size = self.particle_size * (i / len(self._trail_points))
            self._draw_trail_particle(x, y, alpha, size)
    
    def _draw_trail_particle(self, x: float, y: float, alpha: float, size: float) -> None:
        """
        绘制轨迹粒子
        
        参数:
            x: X坐标
            y: Y坐标
            alpha: 透明度
            size: 大小
        """
        # 计算颜色
        if len(self.color) == 7:
            r = int(self.color[1:3], 16)
            g = int(self.color[3:5], 16)
            b = int(self.color[5:7], 16)
            
            r = int(r * alpha)
            g = int(g * alpha)
            b = int(b * alpha)
            
            color = f"#{r:02x}{g:02x}{b:02x}"
        else:
            color = self.color
        
        # 绘制
        x1 = x - size
        y1 = y - size
        x2 = x + size
        y2 = y + size
        
        self.canvas.create_oval(
            x1, y1, x2, y2,
            fill=color,
            outline='',
            tags='trail'
        )


# 导出
__all__ = [
    'Particle',
    'ParticleSystem',
    'TrailEffect',
]