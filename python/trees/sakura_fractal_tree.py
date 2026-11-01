"""动态分形樱花树与落花效果 (Turtle 递归分形)"""
import random
import turtle as T


def tree(branch, t):
    if branch > 3:
        if 8 <= branch <= 12:
            t.pencolor("snow" if random.randint(0, 2) == 0 else "lightcoral")
            t.pensize(branch / 3)
        elif branch < 8:
            t.pencolor("snow" if random.randint(0, 1) == 0 else "lightcoral")
            t.pensize(branch / 2)
        else:
            t.pencolor("sienna")
            t.pensize(branch / 10)
        t.forward(branch)
        a = 1.5 * random.random()
        t.right(20 * a)
        b = 1.5 * random.random()
        tree(branch - 10 * b, t)
        t.left(40 * a)
        tree(branch - 10 * b, t)
        t.right(20 * a)
        t.up()
        t.backward(branch)
        t.down()


def petal(m, t):
    for _ in range(m):
        a = 200 - 400 * random.random()
        b = 10 - 20 * random.random()
        t.up()
        t.forward(b)
        t.left(90)
        t.forward(a)
        t.down()
        t.pencolor("lightcoral")
        t.circle(1)
        t.up()
        t.backward(a)
        t.right(90)
        t.backward(b)


def main():
    w = T.Screen()
    w.title("Sakura Fractal Tree — 动态分形樱花树")
    w.bgcolor("wheat")
    w.setup(860, 680)
    w.tracer(4, 0)
    t = T.Turtle()
    t.hideturtle()
    t.left(90)
    t.up()
    t.backward(170)
    t.down()
    t.pencolor("sienna")
    tree(62, t)
    petal(180, t)
    w.update()
    w.exitonclick()


if __name__ == "__main__":
    main()
