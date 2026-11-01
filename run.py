#!/usr/bin/env python3
"""Visual Art Gallery — 一键启动器与完整性自检脚本"""
from __future__ import annotations

import argparse
import functools
import http.server
import py_compile
import subprocess
import sys
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parent

PYTHON_DEMOS = [
    ("霓虹万花筒神圣几何曼陀罗 [原创/Turtle]", "python/generative/neon_mandala_turtle.py"),
    ("60FPS 星空引力交互烟花秀 [原创/Tkinter]", "python/generative/starry_fireworks_tk.py"),
    ("3D 跳动粒子光环爱心 [Tkinter]", "python/hearts_and_characters/beating_particle_heart.py"),
    ("草莓熊手持玫瑰花 [Turtle]", "python/hearts_and_characters/lotso_bear_rose.py"),
    ("满屏浪漫漂浮爱心 [Turtle]", "python/hearts_and_characters/floating_hearts.py"),
    ("黑夜童话装饰圣诞树 [Turtle]", "python/trees/night_decorated_tree.py"),
    ("经典分形彩灯落雪圣诞树 [Turtle]", "python/trees/fractal_christmas_tree.py"),
    ("少女粉蝴蝶结圣诞树 [Turtle]", "python/trees/pink_ribbon_tree.py"),
    ("动态分形樱花落花树 [Turtle]", "python/trees/sakura_fractal_tree.py"),
    ("浪漫爱心叶片分形树 [Turtle]", "python/trees/love_heart_tree.py"),
]

WEB_DEMOS = [
    ("在线视觉展厅总览 (Gallery Hub)", "index.html"),
    ("3D 流光旋转粒子圣诞树 [原创/Canvas]", "web/3d-spiral-tree/index.html"),
    ("极光流体引力星云 [原创/Canvas]", "web/aurora-cosmos/index.html"),
    ("烟花绽放凝聚文字 [Canvas]", "web/firework-text/index.html"),
    ("3D 空间烟花与粒子字变换 [Canvas]", "web/shape-shifter-particles/index.html"),
    ("全屏庆典烟花秀 [Canvas]", "web/fireworks-celebration/index.html"),
    ("彩色礼花生日蛋糕 [CSS3+JS]", "web/cake-confetti/index.html"),
    ("霓虹聚光灯扫描特效 [CSS3]", "web/neon-spotlight/index.html"),
]

BANNED_SNIPPETS = ("hm.baidu.com", "weidian.com", "pan.quark.cn", "mp.weixin.qq.com", "hide_buttom")


def self_check() -> int:
    for _, rel in PYTHON_DEMOS:
        p = ROOT / rel
        assert p.is_file(), f"Missing Python demo: {rel}"
        py_compile.compile(str(p), doraise=True)

    for _, rel in WEB_DEMOS:
        p = ROOT / rel
        assert p.is_file(), f"Missing Web demo: {rel}"
        text = p.read_text(encoding="utf-8")
        for bad in BANNED_SNIPPETS:
            assert bad not in text, f"Ad/tracker snippet '{bad}' still in {rel}"

    print(f"OK: {len(PYTHON_DEMOS)} Python demos compiled, {len(WEB_DEMOS)} Web pages verified clean.")
    return 0


def serve_web(port: int = 8080) -> None:
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(ROOT))
    with http.server.ThreadingHTTPServer(("127.0.0.1", port), handler) as httpd:
        url = f"http://127.0.0.1:{port}/index.html"
        print(f"Serving Visual Art Gallery at {url} (Ctrl+C to stop)")
        webbrowser.open(url)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nStopped.")


def interactive_menu() -> None:
    print("\n=== ✨ Visual Art Gallery 启动器 ===")
    print("  [0] 🌐 启动本地 Web 展厅 (浏览器打开全部 HTML5 Canvas 特效)")
    for idx, (title, rel) in enumerate(PYTHON_DEMOS, start=1):
        print(f"  [{idx}] 🐍 {title}  ({rel})")
    print("  [q] 退出")

    choice = input("\n请输入编号运行对应展示: ").strip().lower()
    if choice in ("q", "quit", "exit", ""):
        return
    if choice == "0":
        serve_web()
        return
    if choice.isdigit() and 1 <= int(choice) <= len(PYTHON_DEMOS):
        _, rel = PYTHON_DEMOS[int(choice) - 1]
        subprocess.run([sys.executable, str(ROOT / rel)], check=False)
    else:
        print("无效编号。")


def main() -> int:
    parser = argparse.ArgumentParser(description="Visual Art Gallery Runner")
    parser.add_argument("--check", action="store_true", help="Compile-check all Python scripts & audit Web files")
    parser.add_argument("--list", action="store_true", help="List all curated demos")
    parser.add_argument("--web", action="store_true", help="Launch local HTTP server and open gallery index.html")
    parser.add_argument("--port", type=int, default=8080, help="Port for --web server")
    args = parser.parse_args()

    if args.check:
        return self_check()
    if args.list:
        for title, rel in PYTHON_DEMOS + WEB_DEMOS:
            print(f"{title:36s} -> {rel}")
        return 0
    if args.web:
        serve_web(args.port)
        return 0
    interactive_menu()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
