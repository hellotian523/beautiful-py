#!/usr/bin/env python3
"""自动化展厅构建脚本：从 gallery.json 单一事实来源同步生成 index.html、README.md 与 run.py 菜单"""
from __future__ import annotations
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GALLERY_JSON = ROOT / "gallery.json"
INDEX_HTML = ROOT / "index.html"
README_MD = ROOT / "README.md"

def build() -> None:
    data = json.loads(GALLERY_JSON.read_text(encoding="utf-8"))
    web_items = data.get("web", [])
    py_items = data.get("python", [])
    total_web = len(web_items)
    total_py = len(py_items)
    total = total_web + total_py

    # 1. Update index.html
    html = INDEX_HTML.read_text(encoding="utf-8")

    # Update filter counts
    html = re.sub(
        r'<button class="active" data-filter="all">全部作品 \(\d+\)</button>',
        f'<button class="active" data-filter="all">全部作品 ({total})</button>',
        html
    )
    html = re.sub(
        r'<button data-filter="web">🌐 Web 在线交互 \(\d+\)</button>',
        f'<button data-filter="web">🌐 Web 在线交互 ({total_web})</button>',
        html
    )
    html = re.sub(
        r'<button data-filter="python">🐍 Python 桌面动画 \(\d+\)</button>',
        f'<button data-filter="python">🐍 Python 桌面动画 ({total_py})</button>',
        html
    )

    # Combine all items for index.html (web first, then python)
    all_items = []
    for w in web_items:
        it = {
            "type": "web",
            "tag": w.get("tag", "Web"),
            "title": w["title"],
            "desc": w["desc"],
            "url": w["url"]
        }
        if "img" in w:
            it["img"] = w["img"]
        if "icon" in w:
            it["icon"] = w["icon"]
        all_items.append(it)

    for p in py_items:
        it = {
            "type": "python",
            "tag": p.get("tag", "Python"),
            "title": p["title"],
            "desc": p["desc"],
            "cmd": p["cmd"]
        }
        if "img" in p:
            it["img"] = p["img"]
        if "icon" in p:
            it["icon"] = p["icon"]
        all_items.append(it)

    items_json = json.dumps(all_items, ensure_ascii=False, indent=6)
    html = re.sub(
        r'const ITEMS = \[.*?\];',
        f'const ITEMS = {items_json};',
        html,
        flags=re.DOTALL
    )
    INDEX_HTML.write_text(html, encoding="utf-8")
    print(f"✓ index.html synced: {total} items ({total_web} web, {total_py} python).")

    # 2. Update README.md
    readme = README_MD.read_text(encoding="utf-8")
    readme = re.sub(r'作品目录（共 \d+ 个精选与原创展示）', f'作品目录（共 {total} 个精选与原创展示）', readme)

    # Format Web Table
    web_lines = [
        "| 作品 | 路径 | 亮点 / 原作者说明 |",
        "| :--- | :--- | :--- |"
    ]
    for w in web_items:
        author_info = f"[{w['author']}](https://github.com/{w['author']}) (★{w.get('stars','-')}, {w.get('license','MIT')})。{w['desc']}" if "author" in w else w["desc"]
        web_lines.append(f"| **{w['title']}** | [`{w['url']}`]({w['url']}) | {author_info} |")

    # Format Python Table
    py_lines = [
        "| 作品 | 路径 | 亮点说明 |",
        "| :--- | :--- | :--- |"
    ]
    for p in py_items:
        py_lines.append(f"| **{p['title']}** | [`{p['rel']}`]({p['rel']}) | {p['desc']} |")

    # Replace markdown sections if markers exist, or format cleanly
    catalog_section = "### 🌐 Web 交互视觉展示（支持 GitHub Pages 在线运行）\n" + "\n".join(web_lines) + "\n\n" + "### 🐍 Python 桌面动画展示（标准库 `turtle` & `tkinter`，零安装）\n" + "\n".join(py_lines)

    readme = re.sub(
        r'### 🌐 Web 交互视觉展示.*?(?=---\n\n## 🚀 快速开始)',
        catalog_section + "\n\n",
        readme,
        flags=re.DOTALL
    )
    README_MD.write_text(readme, encoding="utf-8")
    print(f"✓ README.md synced with updated tables.")

if __name__ == '__main__':
    build()
