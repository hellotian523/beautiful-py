#!/usr/bin/env python3
"""
双星系引力碰撞与潮汐潮汐尾模拟 (Galaxy Collision N-Body 60FPS)
技术栈: Python 标准库 tkinter + math + random + colorsys (零外部依赖)
控制方式:
  - 鼠标左键点击: 在空间中放置临时额外引力奇点 (引力透镜扰动)
  - 鼠标右键点击: 清除所有用户额外引力点
  - 空格键: 暂停 / 继续物理积分计算
  - R 键: 重新生成不同偏心率的碰撞轨迹
  - C 键: 切换星光色彩方案 (经典星系蓝金 / 赛博紫红 / 翡翠翠绿 / 炽热恒星)
  - Esc / Q: 退出
"""
from __future__ import annotations
import colorsys
import math
import random
import sys
import tkinter as tk

WIDTH = 1000
HEIGHT = 720
EPS = 18.0  # Gravitational softening length
G = 1.4     # Gravitational constant

THEMES = [
    ("Cosmic Blue & Gold", 0.58, 0.11),   # 仙女座蓝 + 银河金
    ("Cyber Violet & Rose", 0.78, 0.94),  # 赛博紫 + 霓虹粉
    ("Aurora Emerald", 0.38, 0.48),       # 极光翠绿
    ("Solar Inferno", 0.04, 0.16),        # 炽烈金红
]


class Star:
    __slots__ = ("x", "y", "vx", "vy", "galaxy_id", "color_idx", "size")

    def __init__(self, x: float, y: float, vx: float, vy: float, galaxy_id: int):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.galaxy_id = galaxy_id
        self.color_idx = random.random()
        self.size = 1.0 if random.random() > 0.12 else 1.8


class Core:
    __slots__ = ("x", "y", "vx", "vy", "mass", "color", "radius")

    def __init__(self, x: float, y: float, vx: float, vy: float, mass: float, color: str):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.mass = mass
        self.color = color
        self.radius = 5.0


class GalaxyCollisionApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Galaxy Collision N-Body — 双螺旋星系引力碰撞模拟 (60FPS)")
        self.root.geometry(f"{WIDTH}x{HEIGHT}")
        self.root.configure(bg="#030712")

        self.canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg="#030712", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.paused = False
        self.theme_idx = 0
        self.attractors: list[tuple[float, float, float]] = []  # (x, y, mass)
        self.stars: list[Star] = []
        self.cores: list[Core] = []

        self._init_galaxies()
        self._bind_events()
        self.loop()

    def _init_galaxies(self):
        self.stars.clear()
        self.cores.clear()
        self.attractors.clear()

        # Core 1: Andromeda (larger)
        c1_x, c1_y = WIDTH * 0.28, HEIGHT * 0.32
        c1_vx, c1_vy = 1.25, 0.65
        core1 = Core(c1_x, c1_y, c1_vx, c1_vy, mass=3400.0, color="#38bdf8")
        self.cores.append(core1)

        # Core 2: Triangulum / Milky Way (smaller, counter orbit)
        c2_x, c2_y = WIDTH * 0.72, HEIGHT * 0.68
        c2_vx, c2_vy = -1.25, -0.65
        core2 = Core(c2_x, c2_y, c2_vx, c2_vy, mass=2500.0, color="#fbbf24")
        self.cores.append(core2)

        # Generate spiral arms for Galaxy 1 (650 stars)
        self._create_spiral(core=core1, num_stars=650, radius_max=185.0, arms=2, galaxy_id=1, spin=1.0)
        # Generate spiral arms for Galaxy 2 (550 stars, tilted)
        self._create_spiral(core=core2, num_stars=550, radius_max=155.0, arms=2, galaxy_id=2, spin=-1.0, tilt=0.85)

    def _create_spiral(self, core: Core, num_stars: int, radius_max: float, arms: int, galaxy_id: int, spin: float, tilt: float = 0.0):
        for i in range(num_stars):
            # Distance from core following exponential disc profile
            u = random.random()
            r = 18.0 + (radius_max - 18.0) * (u ** 0.68)
            # Arm angle with logarithmic spiral winding
            arm_offset = (i % arms) * (2 * math.pi / arms)
            winding = 3.2 * math.log(r / 18.0)
            theta = arm_offset + winding * spin + random.gauss(0, 0.22)

            # Circular velocity v = sqrt(G * M / r)
            v_circ = math.sqrt(G * core.mass / (r + EPS)) * spin
            dx = r * math.cos(theta)
            dy = r * math.sin(theta)

            # Apply galaxy inclination tilt
            if tilt != 0.0:
                dy *= math.cos(tilt)

            vx = -v_circ * math.sin(theta)
            vy = v_circ * math.cos(theta)
            if tilt != 0.0:
                vy *= math.cos(tilt)

            star = Star(
                x=core.x + dx,
                y=core.y + dy,
                vx=core.vx + vx + random.gauss(0, 0.1),
                vy=core.vy + vy + random.gauss(0, 0.1),
                galaxy_id=galaxy_id
            )
            self.stars.append(star)

    def _bind_events(self):
        self.root.bind("<space>", lambda _: self._toggle_pause())
        self.root.bind("<r>", lambda _: self._init_galaxies())
        self.root.bind("<R>", lambda _: self._init_galaxies())
        self.root.bind("<c>", lambda _: self._next_theme())
        self.root.bind("<C>", lambda _: self._next_theme())
        self.root.bind("<Escape>", lambda _: self.root.destroy())
        self.root.bind("<q>", lambda _: self.root.destroy())
        self.canvas.bind("<ButtonPress-1>", self._on_click)
        self.canvas.bind("<ButtonPress-3>", self._on_right_click)

    def _toggle_pause(self):
        self.paused = not self.paused

    def _next_theme(self):
        self.theme_idx = (self.theme_idx + 1) % len(THEMES)

    def _on_click(self, event):
        # Place rogue black hole attractor
        self.attractors.append((event.x, event.y, 2200.0))

    def _on_right_click(self, _event):
        self.attractors.clear()

    def update_physics(self):
        # 1. Cores attract each other
        c1, c2 = self.cores[0], self.cores[1]
        dx = c2.x - c1.x
        dy = c2.y - c1.y
        dist_sq = dx * dx + dy * dy + (EPS * EPS)
        dist = math.sqrt(dist_sq)
        f = G * (c1.mass * c2.mass) / dist_sq
        fx = f * (dx / dist)
        fy = f * (dy / dist)

        c1.vx += (fx / c1.mass)
        c1.vy += (fy / c1.mass)
        c2.vx -= (fx / c2.mass)
        c2.vy -= (fy / c2.mass)

        # Attractor pull on cores
        for ax, ay, am in self.attractors:
            for c in (c1, c2):
                adx = ax - c.x
                ady = ay - c.y
                ad_sq = adx * adx + ady * ady + (EPS * EPS)
                af = G * am / ad_sq
                c.vx += af * (adx / math.sqrt(ad_sq))
                c.vy += af * (ady / math.sqrt(ad_sq))

        c1.x += c1.vx
        c1.y += c1.vy
        c2.x += c2.vx
        c2.y += c2.vy

        # 2. Stars pulled by both galactic cores + attractors
        for s in self.stars:
            ax_total = 0.0
            ay_total = 0.0
            # From Core 1
            d1x = c1.x - s.x
            d1y = c1.y - s.y
            d1_sq = d1x * d1x + d1y * d1y + (EPS * EPS)
            f1 = G * c1.mass / d1_sq
            d1 = math.sqrt(d1_sq)
            ax_total += f1 * (d1x / d1)
            ay_total += f1 * (d1y / d1)

            # From Core 2
            d2x = c2.x - s.x
            d2y = c2.y - s.y
            d2_sq = d2x * d2x + d2y * d2y + (EPS * EPS)
            f2 = G * c2.mass / d2_sq
            d2 = math.sqrt(d2_sq)
            ax_total += f2 * (d2x / d2)
            ay_total += f2 * (d2y / d2)

            # From user attractors
            for at_x, at_y, at_m in self.attractors:
                at_dx = at_x - s.x
                at_dy = at_y - s.y
                at_sq = at_dx * at_dx + at_dy * at_dy + (EPS * EPS)
                at_f = G * at_m / at_sq
                at_d = math.sqrt(at_sq)
                ax_total += at_f * (at_dx / at_d)
                ay_total += at_f * (at_dy / at_d)

            s.vx += ax_total
            s.vy += ay_total
            s.x += s.vx
            s.y += s.vy

    def loop(self):
        if not self.paused:
            self.update_physics()

        self.canvas.delete("all")
        theme_name, h1, h2 = THEMES[self.theme_idx]

        # Draw stars
        for s in self.stars:
            x, y = s.x, s.y
            if 0 <= x <= WIDTH and 0 <= y <= HEIGHT:
                base_hue = h1 if s.galaxy_id == 1 else h2
                speed = math.hypot(s.vx, s.vy)
                hue = (base_hue + (speed * 0.04 - 0.08)) % 1.0
                lum = min(1.0, 0.4 + speed * 0.12)
                r, g, b = colorsys.hsv_to_rgb(hue, 0.75, lum)
                color = f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"
                r_rad = s.size
                self.canvas.create_oval(x - r_rad, y - r_rad, x + r_rad, y + r_rad, fill=color, outline="")

        # Draw Cores (Black Holes with glowing halo)
        for c in self.cores:
            # Halo
            self.canvas.create_oval(c.x - 16, c.y - 16, c.x + 16, c.y + 16, fill="", outline=c.color, width=1.5)
            self.canvas.create_oval(c.x - 8, c.y - 8, c.x + 8, c.y + 8, fill=c.color, outline="#ffffff", width=1.5)
            # Event horizon
            self.canvas.create_oval(c.x - 3, c.y - 3, c.x + 3, c.y + 3, fill="#030712", outline="")

        # Draw User Attractors
        for ax, ay, _ in self.attractors:
            self.canvas.create_oval(ax - 7, ay - 7, ax + 7, ay + 7, fill="#f43f5e", outline="#ffffff", width=1.5)
            self.canvas.create_oval(ax - 18, ay - 18, ax + 18, ay + 18, outline="#f43f5e", width=1.0)

        # HUD
        self.canvas.create_text(
            20, 24, anchor="w",
            text=f"🌌 N-Body Galaxy Collision  |  Theme: {theme_name} [C]  |  [Space] {'PAUSED' if self.paused else 'RUNNING'}  |  [R] Reset  |  Click: Add Gravity Singularity",
            fill="rgba(224, 242, 254, 0.75)",
            font=("Segoe UI", 10)
        )

        self.root.after(16, self.loop)


if __name__ == "__main__":
    tk_root = tk.Tk()
    GalaxyCollisionApp(tk_root)
    tk_root.mainloop()
