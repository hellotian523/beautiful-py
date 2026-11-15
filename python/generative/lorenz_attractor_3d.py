#!/usr/bin/env python3
"""
3D 洛伦兹奇异吸引子 (Lorenz Strange Attractor 3D)
技术栈: Python 标准库 turtle + math + colorsys (零外部依赖)
控制方式:
  - 鼠标左键拖拽: 自由旋转 3D 视角 (Yaw / Pitch)
  - 滚轮 / W/S: 缩放距离
  - 空格键: 切换视角自动缓慢旋转
  - C 键: 切换霓虹色彩主题 (赛博青紫 / 极光翠绿 / 太阳炽金 / 幻彩光谱)
  - R 键: 随机微扰重置轨迹 (直观展示蝴蝶效应)
  - Esc / Q: 退出
"""
from __future__ import annotations
import colorsys
import math
import random
import sys
import turtle as t

SIGMA = 10.0
RHO = 28.0
BETA = 8.0 / 3.0
DT = 0.008
MAX_POINTS = 3200

THEMES = [
    ("Cyberpunk", 0.78, 0.45),   # 霓虹紫青
    ("Aurora", 0.35, 0.60),      # 极光翠绿
    ("Solar", 0.05, 0.16),       # 炽烈金橙
    ("Spectral", 0.0, 1.0),      # 全光谱流光
]


class Lorenz3DApp:
    def __init__(self):
        self.points: list[tuple[float, float, float]] = []
        self.x, self.y, self.z = 0.1, 0.0, 0.0
        self.yaw = 0.6
        self.pitch = 0.35
        self.zoom = 13.5
        self.auto_rotate = True
        self.theme_idx = 0
        self.last_mouse_x = 0
        self.last_mouse_y = 0
        self.is_dragging = False

        self._generate_trajectory(2400)

        self.screen = t.Screen()
        self.screen.setup(960, 720)
        self.screen.bgcolor("#030712")
        self.screen.title("Lorenz Attractor 3D — 洛伦兹混沌奇异吸引子")
        self.screen.colormode(1.0)
        self.screen.tracer(0, 0)

        self.pen = t.Turtle()
        self.pen.hideturtle()
        self.pen.speed(0)

        self._bind_events()
        self.tick()

    def _generate_trajectory(self, n: int):
        self.points.clear()
        x, y, z = self.x, self.y, self.z
        for _ in range(n):
            dx = SIGMA * (y - x) * DT
            dy = (x * (RHO - z) - y) * DT
            dz = (x * y - BETA * z) * DT
            x += dx
            y += dy
            z += dz
            self.points.append((x, y, z - 25.0))
        self.x, self.y, self.z = x, y, z + 25.0

    def _bind_events(self):
        self.screen.listen()
        self.screen.onkey(self._toggle_auto, "space")
        self.screen.onkey(self._next_theme, "c")
        self.screen.onkey(self._next_theme, "C")
        self.screen.onkey(self._reset_perturbed, "r")
        self.screen.onkey(self._reset_perturbed, "R")
        self.screen.onkey(self._quit, "Escape")
        self.screen.onkey(self._quit, "q")
        self.screen.onkey(self._quit, "Q")
        self.screen.onkey(lambda: self._zoom(1.15), "w")
        self.screen.onkey(lambda: self._zoom(0.85), "s")

        canvas = self.screen.getcanvas()
        canvas.bind("<ButtonPress-1>", self._on_press)
        canvas.bind("<B1-Motion>", self._on_drag)
        canvas.bind("<ButtonRelease-1>", self._on_release)
        canvas.bind("<MouseWheel>", self._on_wheel)

    def _on_press(self, event):
        self.is_dragging = True
        self.last_mouse_x = event.x
        self.last_mouse_y = event.y

    def _on_drag(self, event):
        if self.is_dragging:
            dx = event.x - self.last_mouse_x
            dy = event.y - self.last_mouse_y
            self.yaw += dx * 0.008
            self.pitch = max(-1.4, min(1.4, self.pitch + dy * 0.008))
            self.last_mouse_x = event.x
            self.last_mouse_y = event.y

    def _on_release(self, _event):
        self.is_dragging = False

    def _on_wheel(self, event):
        factor = 1.1 if event.delta > 0 else 0.9
        self._zoom(factor)

    def _zoom(self, factor: float):
        self.zoom = max(6.0, min(30.0, self.zoom * factor))

    def _toggle_auto(self):
        self.auto_rotate = not self.auto_rotate

    def _next_theme(self):
        self.theme_idx = (self.theme_idx + 1) % len(THEMES)

    def _reset_perturbed(self):
        self.x = 0.1 + random.uniform(-0.02, 0.02)
        self.y = random.uniform(-0.02, 0.02)
        self.z = random.uniform(-0.02, 0.02)
        self._generate_trajectory(2400)

    def _quit(self):
        try:
            t.bye()
        except Exception:
            pass
        sys.exit(0)

    def project(self, x: float, y: float, z: float) -> tuple[float, float, float]:
        cos_y, sin_y = math.cos(self.yaw), math.sin(self.yaw)
        x1 = x * cos_y + z * sin_y
        z1 = -x * sin_y + z * cos_y

        cos_p, sin_p = math.cos(self.pitch), math.sin(self.pitch)
        y2 = y * cos_p - z1 * sin_p
        z2 = y * sin_p + z1 * cos_p

        dist = 70.0
        depth = dist / (dist + z2)
        sx = x1 * self.zoom * depth
        sy = y2 * self.zoom * depth
        return sx, sy, z2

    def tick(self):
        for _ in range(8):
            dx = SIGMA * (self.y - self.x) * DT
            dy = (self.x * (RHO - self.z) - self.y) * DT
            dz = (self.x * self.y - BETA * self.z) * DT
            self.x += dx
            self.y += dy
            self.z += dz
            self.points.append((self.x, self.y, self.z - 25.0))
            if len(self.points) > MAX_POINTS:
                self.points.pop(0)

        if self.auto_rotate and not self.is_dragging:
            self.yaw += 0.007

        self.pen.clear()
        theme_name, h_start, h_range = THEMES[self.theme_idx]
        total = len(self.points)

        stride = 2
        for i in range(0, total - stride, stride):
            x, y, z = self.points[i]
            sx, sy, depth = self.project(x, y, z)
            nx, ny, _ = self.points[i + stride]
            snx, sny, _ = self.project(nx, ny, _)

            t_val = i / total
            hue = (h_start + t_val * h_range) % 1.0
            bri = 0.35 + 0.65 * t_val
            r, g, b = colorsys.hsv_to_rgb(hue, 0.9, bri)

            self.pen.pencolor(r, g, b)
            self.pen.pensize(1.0 + 2.0 * t_val)
            self.pen.penup()
            self.pen.goto(sx, sy)
            self.pen.pendown()
            self.pen.goto(snx, sny)

        if self.points:
            hx, hy, _ = self.project(*self.points[-1])
            self.pen.penup()
            self.pen.goto(hx, hy - 4)
            self.pen.pencolor(1.0, 1.0, 1.0)
            self.pen.fillcolor(1.0, 1.0, 0.8)
            self.pen.begin_fill()
            self.pen.circle(4)
            self.pen.end_fill()

        self.pen.penup()
        self.pen.goto(-450, 320)
        self.pen.pencolor(0.5, 0.6, 0.75)
        self.pen.write(
            f"3D Lorenz Attractor  |  Theme: {theme_name} [C]  |  [Space] Auto-Rotate: {'ON' if self.auto_rotate else 'OFF'}  |  [R] Perturb  |  Drag: Orbit",
            font=("Segoe UI", 10, "normal")
        )

        self.screen.update()
        self.screen.ontimer(self.tick, 20)


if __name__ == "__main__":
    Lorenz3DApp()
    t.done()
