#!/usr/bin/env python3
"""Visual Art Gallery — 一键启动器、完整性自检与自动构建脚本"""
from __future__ import annotations

import argparse
import functools
import http.server
import json
import py_compile
import subprocess
import sys
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parent
GALLERY_JSON = ROOT / "gallery.json"

BANNED_SNIPPETS = ("hm.baidu.com", "weidian.com", "pan.quark.cn", "mp.weixin.qq.com", "hide_buttom")


def load_gallery() -> dict:
    if not GALLERY_JSON.is_file():
        raise FileNotFoundError(f"Missing {GALLERY_JSON}")
    return json.loads(GALLERY_JSON.read_text(encoding="utf-8"))


def self_check() -> int:
    data = load_gallery()
    py_items = data.get("python", [])
    web_items = data.get("web", [])

    for item in py_items:
        rel = item.get("rel") or item.get("path")
        p = ROOT / rel
        assert p.is_file(), f"Missing Python demo: {rel}"
        py_compile.compile(str(p), doraise=True)

    for item in web_items:
        rel = item.get("url") or item.get("path")
        p = ROOT / rel
        assert p.is_file(), f"Missing Web demo: {rel}"
        text = p.read_text(encoding="utf-8", errors="ignore")
        for bad in BANNED_SNIPPETS:
            assert bad not in text, f"Ad/tracker snippet '{bad}' still in {rel}"

    print(f"OK: {len(py_items)} Python demos compiled, {len(web_items)} Web pages verified clean.")
    return 0


def build_catalog() -> int:
    script = ROOT / "scripts" / "build_catalog.py"
    if not script.is_file():
        print("Error: scripts/build_catalog.py not found.")
        return 1
    res = subprocess.run([sys.executable, str(script)], check=False)
    return res.returncode


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
    data = load_gallery()
    py_items = data.get("python", [])
    print(f"\n=== ✨ Visual Art Gallery 启动器 (共 {len(py_items)} 个桌面动画) ===")
    print("  [0] 🌐 启动本地 Web 展厅 (浏览器打开全部 HTML5 Canvas / WebGL 特效)")
    for idx, item in enumerate(py_items, start=1):
        print(f"  [{idx:2d}] 🐍 {item['title']}  ({item.get('rel', '')})")
    print("  [b] 🛠️ 重新生成 index.html 与 README.md (Build)")
    print("  [c] 🔍 运行代码语法与完整性自检 (Check)")
    print("  [n] 🎨 新建 Python 动画模板 (--new-python)")
    print("  [w] ✨ 新建 Web 交互特效模板 (--new-web)")
    print("  [r] 🔭 运行开源视觉雷达追踪 (--radar)")

    print("  [q] 退出")

    choice = input("\n请输入选项或编号: ").strip().lower()
    if choice in ("q", "quit", "exit", ""):
        return
    if choice == "0":
        serve_web()
        return
    if choice == "b":
        build_catalog()
        return
    if choice == "c":
        self_check()
        return
    if choice == "n":
        name = input("请输入新 Python 动画名称 (英文标识符): ").strip()
        if name:
            from scripts.scaffold import new_python
            new_python(name)
        return
    if choice == "w":
        name = input("请输入新 Web 特效名称 (英文标识符): ").strip()
        if name:
            from scripts.scaffold import new_web
            new_web(name)
        return
    if choice == "r":
        subprocess.run([sys.executable, str(ROOT / "scripts" / "trend_tracker.py")], check=True)
        return

    if choice.isdigit() and 1 <= int(choice) <= len(py_items):
        item = py_items[int(choice) - 1]
        subprocess.run([sys.executable, str(ROOT / item["rel"])], check=False)
    else:
        print("无效编号。")


def main() -> int:
    parser = argparse.ArgumentParser(description="Visual Art Gallery Runner & Automation")
    parser.add_argument("--check", action="store_true", help="Compile-check all Python scripts & audit Web files")
    parser.add_argument("--build", action="store_true", help="Rebuild index.html & README.md from gallery.json")
    parser.add_argument("--list", action="store_true", help="List all curated demos")
    parser.add_argument("--web", action="store_true", help="Launch local HTTP server and open gallery index.html")
    parser.add_argument("--port", type=int, default=8080, help="Port for --web server")
    parser.add_argument("--new-python", metavar="NAME", help="Create new Python generative demo from template")
    parser.add_argument("--new-web", metavar="NAME", help="Create new Web Canvas visual demo from template")
    parser.add_argument("--template", default="turtle", choices=["turtle", "tkinter"], help="Template type for --new-python")
    parser.add_argument("--import", "--import-path", metavar="PATH", dest="import_path", help="Import local python or web demo into gallery")
    parser.add_argument("--radar", action="store_true", help="Run visual art trend radar locally")

    args = parser.parse_args()

    if args.check:
        return self_check()
    if args.build:
        return build_catalog()
    if args.list:
        data = load_gallery()
        print(f"Python Demos ({len(data.get('python', []))}):")
        for p in data.get("python", []):
            print(f"  - {p['title']} -> {p['rel']}")
        print(f"\nWeb Demos ({len(data.get('web', []))}):")
        for w in data.get("web", []):
            print(f"  - {w['title']} -> {w['url']}")
        return 0
    if args.web:
        serve_web(args.port)
        return 0
    if args.new_python:
        from scripts.scaffold import new_python
        new_python(args.new_python, tmpl=args.template)
        return 0
    if args.new_web:
        from scripts.scaffold import new_web
        new_web(args.new_web)
        return 0
    if args.import_path:
        from scripts.scaffold import import_local
        import_local(args.import_path)
        return 0
    if args.radar:
        subprocess.run([sys.executable, str(ROOT / "scripts" / "trend_tracker.py")], check=True)
        return 0


    interactive_menu()
    return 0


if __name__ == "__main__":
    sys.exit(main())
