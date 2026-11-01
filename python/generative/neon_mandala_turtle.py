"""霓虹万花筒与神圣几何曼陀罗 (Turtle HSV 渐变生成艺术)"""
import colorsys
import math
import turtle as t


def draw_mandala():
    screen = t.Screen()
    screen.setup(900, 900)
    screen.bgcolor("#05050d")
    screen.title("Neon Sacred Mandala — 霓虹万花筒生成艺术")
    screen.colormode(1.0)
    screen.tracer(12, 0)

    pen = t.Turtle()
    pen.hideturtle()
    pen.speed(0)

    # Layer 1: Outer lotus spirograph
    steps = 180
    for i in range(steps):
        hue = (i / steps) % 1.0
        r, g, b = colorsys.hsv_to_rgb(hue, 0.85, 1.0)
        pen.pencolor(r, g, b)
        pen.pensize(1.4)
        pen.penup()
        pen.goto(0, 0)
        pen.setheading(i * (360 / steps))
        pen.forward(70)
        pen.pendown()
        pen.circle(120, 140)
        pen.left(50)
        pen.circle(80, 140)

    # Layer 2: Inner golden-ratio star web
    pen.pensize(1.8)
    for i in range(108):
        hue = (0.55 + i / 216) % 1.0
        r, g, b = colorsys.hsv_to_rgb(hue, 0.75, 1.0)
        pen.pencolor(r, g, b)
        angle = i * 137.508
        rad = 18 * math.sqrt(i)
        x = rad * math.cos(math.radians(angle))
        y = rad * math.sin(math.radians(angle))
        pen.penup()
        pen.goto(x, y)
        pen.pendown()
        pen.setheading(angle + 45)
        for _ in range(4):
            pen.forward(18 + i * 0.12)
            pen.right(90)

    # Layer 3: Glowing core ring
    pen.penup()
    pen.goto(0, -42)
    pen.setheading(0)
    pen.pensize(3)
    pen.pencolor(1.0, 0.92, 0.65)
    pen.pendown()
    pen.circle(42)

    screen.update()
    screen.exitonclick()


if __name__ == "__main__":
    draw_mandala()
