#!/usr/bin/env python3
"""自动化作品脚手架与外部导入工具"""
from __future__ import annotations
import json, re, shutil, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GALLERY_JSON = ROOT / "gallery.json"
BANNED = ["hm.baidu.com", "weidian.com", "pan.quark.cn", "mp.weixin.qq.com", "hide_buttom"]

def register(item: dict, kind: str) -> None:
    data = json.loads(GALLERY_JSON.read_text(encoding="utf-8"))
    items = data.setdefault(kind, [])
    items = [i for i in items if i.get("id") != item["id"]]
    items.append(item)
    data[kind] = items
    GALLERY_JSON.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    subprocess.run([sys.executable, str(ROOT / "scripts" / "build_catalog.py")], check=True)

def new_python(slug: str, title: str | None = None, tmpl: str = "turtle") -> Path:
    slug = re.sub(r"[^a-zA-Z0-9_]+", "_", slug).strip("_").lower()
    title = title or slug.replace("_", " ").title()
    dest = ROOT / "python" / "generative" / f"{slug}.py"
    if dest.exists():
        print(f"File {dest} already exists.")
        return dest

    if tmpl == "turtle":
        body = f"""#!/usr/bin/env python3
\"\"\"
{title}
技术栈: Python 标准库 turtle (零外部依赖)
按 Esc 退出，点击屏幕重新生成
\"\"\"
import turtle

def draw():
    turtle.clearscreen()
    screen = turtle.Screen()
    screen.setup(width=960, height=720)
    screen.bgcolor("#030712")
    screen.title("{title}")
    screen.tracer(0, 0)

    t = turtle.Turtle()
    t.hideturtle()
    t.speed(0)
    t.pensize(1.5)

    colors = ["#38bdf8", "#818cf8", "#c084fc", "#f472b6", "#fbbf24"]
    for i in range(240):
        t.color(colors[i % len(colors)])
        t.forward(i * 1.5)
        t.left(59)
        t.circle(i * 0.4, 60)
        t.left(31)

    screen.update()
    screen.listen()
    screen.onkey(turtle.bye, "Escape")
    screen.onclick(lambda x, y: draw())

if __name__ == "__main__":
    turtle.colormode(255)
    draw()
    turtle.done()
"""
    else:
        body = f"""#!/usr/bin/env python3
\"\"\"
{title}
技术栈: Python 标准库 tkinter + math (60FPS 物理粒子循环)
\"\"\"
import tkinter as tk, math, random

class VisualApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("{title}")
        self.root.geometry("960x720")
        self.canvas = tk.Canvas(root, bg="#030712", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.cx, self.cy = 480, 360
        self.angle = 0.0
        self.canvas.bind("<Configure>", lambda e: setattr(self, "cx", e.width/2) or setattr(self, "cy", e.height/2))
        self.root.bind("<Escape>", lambda e: self.root.destroy())
        self.loop()

    def loop(self):
        self.canvas.delete("all")
        self.angle += 0.03
        for i in range(120):
            r = 160 + math.sin(self.angle * 2 + i * 0.1) * 30
            x = self.cx + math.cos(i * 0.05 + self.angle) * r
            y = self.cy + math.sin(i * 0.05 + self.angle) * r
            self.canvas.create_oval(x-3, y-3, x+3, y+3, fill="#38bdf8", outline="")
        self.root.after(16, self.loop)

if __name__ == "__main__":
    r = tk.Tk()
    VisualApp(r)
    r.mainloop()
"""
    dest.write_text(body, encoding="utf-8")
    rel = f"python/generative/{slug}.py"
    register({
        "id": slug,
        "type": "python",
        "tag": f"Python {tmpl.capitalize()} · 原创",
        "title": title,
        "desc": f"基于 Python 标准库 {tmpl} 实现的实时生成艺术视觉展示。",
        "cmd": f"python {rel}",
        "rel": rel,
        "icon": "🎨" if tmpl == "turtle" else "⚡"
    }, "python")
    print(f"✓ Created Python demo: {dest}")
    return dest

def new_web(slug: str, title: str | None = None) -> Path:
    slug = re.sub(r"[^a-zA-Z0-9_-]+", "-", slug).strip("-").lower()
    title = title or slug.replace("-", " ").title()
    dest_dir = ROOT / "web" / slug
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / "index.html"
    if dest.exists():
        print(f"File {dest} already exists.")
        return dest

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{title}</title>
  <style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    html, body {{ width: 100%; height: 100%; overflow: hidden; background: #030712; }}
    canvas {{ display: block; width: 100vw; height: 100vh; cursor: crosshair; }}
    .hint {{ position: fixed; top: 16px; left: 20px; color: rgba(224,242,254,0.7); font-size: 13px; }}
  </style>
</head>
<body>
  <div class="hint">✨ 移动鼠标与点击屏幕交互</div>
  <canvas id="c"></canvas>
  <script>
    const canvas = document.getElementById("c");
    const ctx = canvas.getContext("2d");
    let w, h, dpr = window.devicePixelRatio || 1;
    function resize() {{
      w = window.innerWidth; h = window.innerHeight;
      canvas.width = w * dpr; canvas.height = h * dpr;
      ctx.scale(dpr, dpr);
    }}
    window.addEventListener("resize", resize);
    resize();
    let mouse = {{ x: w/2, y: h/2, active: false }};
    window.addEventListener("mousemove", e => {{ mouse.x = e.clientX; mouse.y = e.clientY; mouse.active = true; }});
    const pts = Array.from({{ length: 240 }}, () => ({{
      x: Math.random() * w, y: Math.random() * h,
      vx: (Math.random() - 0.5) * 2, vy: (Math.random() - 0.5) * 2,
      r: Math.random() * 2 + 1, hue: Math.random() * 60 + 190
    }}));
    function frame() {{
      ctx.fillStyle = "rgba(3, 7, 18, 0.2)";
      ctx.fillRect(0, 0, w, h);
      pts.forEach(p => {{
        p.x += p.vx; p.y += p.vy;
        if (p.x < 0 || p.x > w) p.vx *= -1;
        if (p.y < 0 || p.y > h) p.vy *= -1;
        if (mouse.active) {{
          let dx = mouse.x - p.x, dy = mouse.y - p.y;
          let d = Math.hypot(dx, dy);
          if (d < 160) {{ p.x += (dx/d)*2; p.y += (dy/d)*2; }}
        }}
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
        ctx.fillStyle = `hsl(${p.hue}, 90%, 65%)`;
        ctx.shadowColor = `hsl(${p.hue}, 90%, 65%)`;
        ctx.shadowBlur = 10;
        ctx.fill();
      }});
      requestAnimationFrame(frame);
    }}
    requestAnimationFrame(frame);
  </script>
</body>
</html>
"""
    dest.write_text(html, encoding="utf-8")
    url = f"web/{slug}/index.html"
    register({
        "id": slug.replace("-", "_"),
        "type": "web",
        "tag": "Web Canvas · 原创",
        "title": title,
        "desc": "基于 HTML5 Canvas 的高响应流光粒子与交互视觉展示。",
        "url": url,
        "icon": "✨"
    }, "web")
    print(f"✓ Created Web demo: {dest}")
    return dest

def import_local(source_path: str, title: str | None = None) -> None:
    src = Path(source_path).resolve()
    if not src.exists(): raise FileNotFoundError(f"Source not found: {source_path}")
    if src.is_file() and src.suffix == ".py":
        slug = src.stem
        title = title or slug.replace("_", " ").title()
        dest = ROOT / "python" / "generative" / src.name
        shutil.copy2(src, dest)
        rel = f"python/generative/{src.name}"
        register({
            "id": slug, "type": "python", "tag": "Python · 导入精选",
            "title": title, "desc": "收录自外部的 Python 视觉艺术脚本。",
            "cmd": f"python {rel}", "rel": rel, "icon": "🐍"
        }, "python")
        print(f"✓ Imported Python demo: {dest}")
    elif src.is_file() and src.suffix in (".html", ".htm"):
        slug = src.stem
        title = title or slug.replace("-", " ").title()
        dest_dir = ROOT / "web" / slug
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest = dest_dir / "index.html"
        txt = src.read_text(encoding="utf-8", errors="ignore")
        for bad in BANNED: txt = txt.replace(bad, "")
        dest.write_text(txt, encoding="utf-8")
        url = f"web/{slug}/index.html"
        register({
            "id": slug.replace("-", "_"), "type": "web", "tag": "Web · 导入精选",
            "title": title, "desc": "收录自外部的高颜值 Web 视觉特效展示。",
            "url": url, "icon": "🌐"
        }, "web")
        print(f"✓ Imported Web single file: {dest}")
    elif src.is_dir():
        slug = src.name
        title = title or slug.replace("-", " ").title()
        dest_dir = ROOT / "web" / slug
        if dest_dir.exists(): shutil.rmtree(dest_dir)
        shutil.copytree(src, dest_dir)
        for h in dest_dir.glob("**/*.html"):
            txt = h.read_text(encoding="utf-8", errors="ignore")
            for bad in BANNED: txt = txt.replace(bad, "")
            h.write_text(txt, encoding="utf-8")
        url = f"web/{slug}/index.html"
        register({
            "id": slug.replace("-", "_"), "type": "web", "tag": "Web · 导入精选",
            "title": title, "desc": "收录自外部的 Web 完整项目展项。",
            "url": url, "icon": "🌟"
        }, "web")
        print(f"✓ Imported Web directory: {dest_dir}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: scaffold.py [new-python|new-web|import] <name/path> [title] [template]")
        sys.exit(1)
    act = sys.argv[1]
    arg1 = sys.argv[2]
    t = sys.argv[3] if len(sys.argv) > 3 else None
    if act == "new-python":
        new_python(arg1, t, sys.argv[4] if len(sys.argv) > 4 else "turtle")
    elif act == "new-web":
        new_web(arg1, t)
    elif act == "import":
        import_local(arg1, t)
