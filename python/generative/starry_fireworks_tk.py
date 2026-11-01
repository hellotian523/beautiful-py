"""星空引力烟花秀 (Tkinter 60FPS 物理粒子交互展示 — 点击屏幕任意位置发射烟花)"""
import colorsys
import math
import random
import tkinter as tk

WIDTH, HEIGHT = 960, 640
PALETTES = [
    [0.95, 0.02, 0.08],  # Rose & Gold
    [0.52, 0.58, 0.65],  # Cyber Cyan & Blue
    [0.75, 0.85, 0.12],  # Neon Violet & Amber
    [0.32, 0.48, 0.16],  # Emerald Aurora
]


def hsv_hex(h, s, v):
    r, g, b = colorsys.hsv_to_rgb(h % 1.0, max(0.0, min(1.0, s)), max(0.0, min(1.0, v)))
    return f"#{int(r * 255):02x}{int(g * 255):02x}{int(b * 255):02x}"


class Spark:
    __slots__ = ("x", "y", "px", "py", "vx", "vy", "hue", "life", "max_life", "size")

    def __init__(self, x, y, hue):
        angle = random.uniform(0, math.tau)
        speed = random.uniform(1.2, 7.8) * (1.0 if random.random() > 0.15 else 1.45)
        self.x = self.px = x
        self.y = self.py = y
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.hue = hue + random.uniform(-0.04, 0.04)
        self.max_life = random.randint(36, 68)
        self.life = self.max_life
        self.size = random.uniform(1.8, 3.4)

    def step(self):
        self.px, self.py = self.x, self.y
        self.x += self.vx
        self.y += self.vy
        self.vx *= 0.965
        self.vy = self.vy * 0.965 + 0.095
        self.life -= 1
        return self.life > 0


class Rocket:
    __slots__ = ("x", "y", "vx", "vy", "target_y", "palette")

    def __init__(self, x=None, target_y=None):
        self.x = x if x is not None else random.uniform(140, WIDTH - 140)
        self.y = HEIGHT - 10
        self.target_y = target_y if target_y is not None else random.uniform(110, HEIGHT * 0.52)
        dist = max(60.0, self.y - self.target_y)
        self.vy = -math.sqrt(2 * 0.14 * dist)
        self.vx = random.uniform(-1.1, 1.1) if x is None else 0.0
        self.palette = random.choice(PALETTES)

    def step(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.14
        return self.vy < -0.4 and self.y > self.target_y


class FireworkShow:
    def __init__(self, root):
        self.root = root
        self.root.title("Starry Fireworks — 星空引力粒子烟花秀 (点击画布发射)")
        self.canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg="#050611", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.stars = [
            (random.randint(0, WIDTH), random.randint(0, int(HEIGHT * 0.78)), random.choice((1, 1, 2)), random.random())
            for _ in range(110)
        ]
        self.rockets = [Rocket() for _ in range(2)]
        self.sparks = []
        self.frame = 0
        self.canvas.bind("<Button-1>", self.on_click)

    def on_click(self, event):
        self.rockets.append(Rocket(event.x, max(70, min(HEIGHT - 120, event.y))))

    def explode(self, rocket):
        for _ in range(95):
            self.sparks.append(Spark(rocket.x, rocket.y, random.choice(rocket.palette)))

    def tick(self):
        self.frame += 1
        self.canvas.delete("all")

        # Twinkling starfield
        for sx, sy, sr, phase in self.stars:
            b = 0.45 + 0.55 * abs(math.sin(self.frame * 0.04 + phase * 6.28))
            col = hsv_hex(0.62, 0.2, b)
            self.canvas.create_oval(sx, sy, sx + sr, sy + sr, fill=col, outline="")

        self.canvas.create_text(
            WIDTH // 2,
            HEIGHT - 24,
            text="✨ 点击屏幕任意位置发射定制烟花 | Click anywhere to launch fireworks ✨",
            fill="#6c7a9c",
            font=("Microsoft YaHei", 10),
        )

        if self.frame % 26 == 0 and len(self.rockets) < 5:
            self.rockets.append(Rocket())

        next_rockets = []
        for r in self.rockets:
            if r.step():
                self.canvas.create_oval(r.x - 2.5, r.y - 2.5, r.x + 2.5, r.y + 2.5, fill="#ffe89e", outline="")
                self.canvas.create_line(r.x, r.y, r.x - r.vx * 3, r.y - r.vy * 3, fill="#ff9f43", width=2)
                next_rockets.append(r)
            else:
                self.explode(r)
        self.rockets = next_rockets

        next_sparks = []
        for s in self.sparks:
            if s.step():
                ratio = s.life / s.max_life
                col = hsv_hex(s.hue, 0.78, min(1.0, ratio * 1.25))
                self.canvas.create_line(s.px, s.py, s.x, s.y, fill=col, width=max(1.0, s.size * ratio))
                next_sparks.append(s)
        self.sparks = next_sparks

        self.root.after(16, self.tick)


if __name__ == "__main__":
    app = tk.Tk()
    show = FireworkShow(app)
    show.tick()
    app.mainloop()
