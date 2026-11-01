"""满屏漂浮爱心动画 (Turtle 双缓冲帧动画)"""
import math
import random as ra
import turtle as tu

tu.setup(960, 640)
tu.title("Floating Hearts — 满屏浪漫漂浮爱心")
tu.bgcolor("#070710")
tu.tracer(0)

t = tu.Pen()
t.ht()
COLORS = ["#ff4d79", "#ff758f", "#ff8fa3", "#ffb3c1", "#ffccd5", "#e056fd"]


class Heart:
    def __init__(self, initial=True):
        self.reset(initial)

    def reset(self, initial=False):
        self.r = ra.randint(8, 16)
        self.x = ra.randint(-480, 480)
        self.y = ra.randint(-320, 320) if initial else -340
        self.phase = ra.uniform(-math.pi, math.pi)
        self.speed = ra.uniform(2.5, 5.5)
        self.color = ra.choice(COLORS)

    def move(self):
        if self.y <= 340:
            self.y += self.speed
            self.x += self.speed * math.sin(self.phase) * 0.45
            self.phase += 0.08
        else:
            self.reset(False)

    def draw(self):
        t.penup()
        t.goto(self.x, self.y)
        t.pendown()
        t.color(self.color, self.color)
        t.begin_fill()
        t.setheading(120)
        t.circle(self.r, 195)
        t.fd(self.r * 2.4)
        t.left(90)
        t.forward(self.r * 2.4)
        t.circle(self.r, 195)
        t.end_fill()


hearts = [Heart(True) for _ in range(48)]


def animate():
    t.clear()
    for h in hearts:
        h.move()
        h.draw()
    tu.update()
    tu.ontimer(animate, 25)


animate()
tu.mainloop()
