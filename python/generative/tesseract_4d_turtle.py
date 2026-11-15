#!/usr/bin/env python3
"""
4D 超立方体四维投影旋转 (4D Tesseract Hypercube Projection)
技术栈: Python 标准库 turtle + math + colorsys (零外部依赖)
控制方式:
  - 鼠标左键拖拽: 自由旋转 3D 视角 (Yaw / Pitch)
  - 滚轮 / W/S: 缩放距离
  - 空格键: 暂停 / 继续四维自动翻转
  - 1 / 2 / 3 / 4: 切换激活不同的四维旋转平面 (XW / YW / ZW / XY)
  - C 键: 切换霓虹色彩主题 (赛博青紫 / 极光翠绿 / 太阳炽金 / 幻彩光谱)
  - R 键: 重置旋转角度与视角
  - Esc / Q: 退出
"""
from __future__ import annotations
import colorsys
import math
import sys
import turtle as t

THEMES = [
    ("Cyberpunk", (0.52, 0.85)),   # 赛博电青 -> 霓虹紫红
    ("Aurora", (0.38, 0.58)),      # 极光翡翠 -> 冰川青
    ("Solar", (0.05, 0.16)),       # 太阳金橙 -> 耀斑绯红
    ("Spectral", (0.0, 1.0)),      # 全光谱渐变
]


class Tesseract4DApp:
    def __init__(self):
        # 4D 超立方体 16 个顶点坐标 (x, y, z, w)
        self.vertices_4d: list[tuple[float, float, float, float]] = [
            (x, y, z, w)
            for x in (-1.0, 1.0)
            for y in (-1.0, 1.0)
            for z in (-1.0, 1.0)
            for w in (-1.0, 1.0)
        ]

        # 32 条 4D 边 (两顶点汉明距离为 1)
        self.edges: list[tuple[int, int]] = []
        for i in range(16):
            for j in range(i + 1, 16):
                diff = sum(
                    1 for k in range(4)
                    if abs(self.vertices_4d[i][k] - self.vertices_4d[j][k]) > 0.1
                )
                if diff == 1:
                    self.edges.append((i, j))

        # 4D 旋转角
        self.angle_xw = 0.0
        self.angle_yw = 0.0
        self.angle_zw = 0.0
        self.angle_xy = 0.0

        # 启用的 4D 旋转平面
        self.active_planes = {"xw": True, "zw": True, "yw": False, "xy": True}

        # 3D 观察相机
        self.yaw = 0.55
        self.pitch = 0.32
        self.zoom = 1.0
        self.auto_rotate = True
        self.theme_idx = 0

        # 鼠标交互
        self.is_dragging = False
        self.last_x = 0
        self.last_y = 0

        # 初始化 Turtle
        self.screen = t.Screen()
        self.screen.setup(960, 720)
        self.screen.bgcolor("#030712")
        self.screen.title("4D Tesseract Hypercube — 四维超立方体立体投影")
        self.screen.colormode(1.0)
        self.screen.tracer(0, 0)

        self.pen = t.Turtle()
        self.pen.hideturtle()
        self.pen.speed(0)

        self.hud = t.Turtle()
        self.hud.hideturtle()
        self.hud.speed(0)

        self._bind_events()
        self.tick()

    def _bind_events(self):
        self.screen.listen()
        self.screen.onkey(self._toggle_auto, "space")
        self.screen.onkey(self._next_theme, "c")
        self.screen.onkey(self._next_theme, "C")
        self.screen.onkey(self._reset, "r")
        self.screen.onkey(self._reset, "R")
        self.screen.onkey(self._quit, "Escape")
        self.screen.onkey(self._quit, "q")
        self.screen.onkey(self._quit, "Q")
        self.screen.onkey(lambda: self._zoom_step(1.1), "w")
        self.screen.onkey(lambda: self._zoom_step(0.9), "s")
        self.screen.onkey(lambda: self._toggle_plane("xw"), "1")
        self.screen.onkey(lambda: self._toggle_plane("yw"), "2")
        self.screen.onkey(lambda: self._toggle_plane("zw"), "3")
        self.screen.onkey(lambda: self._toggle_plane("xy"), "4")

        canvas = self.screen.getcanvas()
        canvas.bind("<ButtonPress-1>", self._on_press)
        canvas.bind("<B1-Motion>", self._on_drag)
        canvas.bind("<ButtonRelease-1>", self._on_release)
        canvas.bind("<MouseWheel>", self._on_wheel)

    def _on_press(self, event):
        self.is_dragging = True
        self.last_x = event.x
        self.last_y = event.y

    def _on_drag(self, event):
        if self.is_dragging:
            dx = event.x - self.last_x
            dy = event.y - self.last_y
            self.yaw += dx * 0.008
            self.pitch = max(-1.4, min(1.4, self.pitch + dy * 0.008))
            self.last_x = event.x
            self.last_y = event.y

    def _on_release(self, _event):
        self.is_dragging = False

    def _on_wheel(self, event):
        self._zoom_step(1.1 if event.delta > 0 else 0.9)

    def _zoom_step(self, factor: float):
        self.zoom = max(0.5, min(2.5, self.zoom * factor))

    def _toggle_auto(self):
        self.auto_rotate = not self.auto_rotate

    def _toggle_plane(self, plane: str):
        self.active_planes[plane] = not self.active_planes[plane]

    def _next_theme(self):
        self.theme_idx = (self.theme_idx + 1) % len(THEMES)

    def _reset(self):
        self.angle_xw = 0.0
        self.angle_yw = 0.0
        self.angle_zw = 0.0
        self.angle_xy = 0.0
        self.yaw = 0.55
        self.pitch = 0.32
        self.zoom = 1.0

    def _quit(self):
        try:
            t.bye()
        except Exception:
            pass
        sys.exit(0)

    def _rotate_4d(self, v: tuple[float, float, float, float]) -> tuple[float, float, float, float]:
        x, y, z, w = v
        # Plane XW
        if self.angle_xw:
            c, s = math.cos(self.angle_xw), math.sin(self.angle_xw)
            x, w = x * c - w * s, x * s + w * c
        # Plane YW
        if self.angle_yw:
            c, s = math.cos(self.angle_yw), math.sin(self.angle_yw)
            y, w = y * c - w * s, y * s + w * c
        # Plane ZW
        if self.angle_zw:
            c, s = math.cos(self.angle_zw), math.sin(self.angle_zw)
            z, w = z * c - w * s, z * s + w * c
        # Plane XY
        if self.angle_xy:
            c, s = math.cos(self.angle_xy), math.sin(self.angle_xy)
            x, y = x * c - y * s, x * s + y * c
        return (x, y, z, w)

    def _project_4d_to_screen(
        self, v4: tuple[float, float, float, float]
    ) -> tuple[float, float, float, float]:
        x, y, z, w = v4
        # 4D 透视投影到 3D
        d4 = 2.4
        p4 = 1.0 / max(0.2, (d4 - w))
        x3 = x * p4
        y3 = y * p4
        z3 = z * p4

        # 3D 观察相机偏航 (Yaw) 与俯仰 (Pitch)
        cy, sy = math.cos(self.yaw), math.sin(self.yaw)
        xc = x3 * cy - z3 * sy
        z_mid = x3 * sy + z3 * cy

        cp, sp = math.cos(self.pitch), math.sin(self.pitch)
        yc = y3 * cp - z_mid * sp
        zc = y3 * sp + z_mid * cp

        # 3D 透视投影到屏幕
        d3 = 3.6
        scale = self.zoom * 420.0
        p3 = scale / max(0.5, (d3 - zc))
        sx = xc * p3
        sy = yc * p3
        return (sx, sy, zc, w)

    def _get_color(self, w: float) -> tuple[float, float, float]:
        # 根据 4D 坐标 w 映射到色相
        _, (h_min, h_max) = THEMES[self.theme_idx]
        t_val = (w + 1.5) / 3.0
        t_val = max(0.0, min(1.0, t_val))
        h = (h_min + t_val * (h_max - h_min)) % 1.0
        s = 0.85
        v = 0.55 + 0.45 * (1.0 - abs(w) / 1.8)
        return colorsys.hsv_to_rgb(h, s, max(0.2, min(1.0, v)))

    def tick(self):
        if self.auto_rotate:
            if self.active_planes["xw"]:
                self.angle_xw += 0.016
            if self.active_planes["zw"]:
                self.angle_zw += 0.012
            if self.active_planes["yw"]:
                self.angle_yw += 0.010
            if self.active_planes["xy"]:
                self.angle_xy += 0.008

        # 计算并投影全部 16 个顶点
        proj_vertices: list[tuple[float, float, float, float]] = []
        for v in self.vertices_4d:
            rot = self._rotate_4d(v)
            proj = self._project_4d_to_screen(rot)
            proj_vertices.append(proj)

        # 绘制
        self.pen.clear()

        # 按深度排序 32 条边 (由远及近画家算法)
        sorted_edges = sorted(
            self.edges,
            key=lambda e: (proj_vertices[e[0]][2] + proj_vertices[e[1]][2]) / 2.0,
            reverse=False,
        )

        for i, j in sorted_edges:
            p1 = proj_vertices[i]
            p2 = proj_vertices[j]
            avg_w = (p1[3] + p2[3]) / 2.0
            r, g, b = self._get_color(avg_w)

            # 根据深度设置线宽
            avg_z = (p1[2] + p2[2]) / 2.0
            width = max(1.2, min(3.8, 2.2 + avg_z * 0.8))

            self.pen.pensize(width)
            self.pen.pencolor(r, g, b)
            self.pen.penup()
            self.pen.goto(p1[0], p1[1])
            self.pen.pendown()
            self.pen.goto(p2[0], p2[1])

        # 绘制顶点发光圆点
        for p in proj_vertices:
            r, g, b = self._get_color(p[3])
            size = max(3.0, min(8.0, 5.0 + p[2] * 1.5))
            self.pen.penup()
            self.pen.goto(p[0], p[1] - size / 2)
            self.pen.pendown()
            self.pen.fillcolor(r, g, b)
            self.pen.pencolor(1.0, 1.0, 1.0)
            self.pen.pensize(1.0)
            self.pen.begin_fill()
            self.pen.circle(size)
            self.pen.end_fill()

        # HUD 信息
        self._draw_hud()

        self.screen.update()
        self.screen.ontimer(self.tick, 16)

    def _draw_hud(self):
        self.hud.clear()
        self.hud.penup()
        self.hud.pencolor("#94a3b8")
        self.hud.goto(-460, 320)
        tname, _ = THEMES[self.theme_idx]
        planes = " ".join([k.upper() for k, v in self.active_planes.items() if v]) or "None"
        text = (
            f"4D Tesseract [16 Vertices · 32 Edges] | Theme: {tname} (C) | "
            f"Active 4D Planes: {planes} (1-4) | Space: {'Pause' if self.auto_rotate else 'Play'} | Esc: Quit"
        )
        self.hud.write(text, font=("Consolas", 10, "normal"))


if __name__ == "__main__":
    app = Tesseract4DApp()
    t.mainloop()
