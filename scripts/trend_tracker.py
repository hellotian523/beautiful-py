#!/usr/bin/env python3
"""每周创意视觉与 Shader / Turtle 开源项目雷达追踪器"""
from __future__ import annotations
import json, urllib.parse, urllib.request, sys
from datetime import datetime
from pathlib import Path

QUERIES = [
    ("WebGL 粒子 / 体积流体 / GPGPU", "webgl fluid OR gpgpu particles stars:>100"),
    ("Three.js 着色器视觉特效", "threejs shader bloom OR particles stars:>100"),
    ("Python 生成艺术 / Turtle / Taichi", "taichi visual OR fluid OR turtle art stars:>50"),
]

def search(q: str, limit: int = 4) -> list[dict]:
    url = f"https://api.github.com/search/repositories?q={urllib.parse.quote(q)}&sort=stars&order=desc&per_page={limit}"
    req = urllib.request.Request(url, headers={"User-Agent": "beautiful-py-radar/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data.get("items", [])
    except Exception as e:
        print(f"Search error: {e}", file=sys.stderr)
        return []

def main():
    now = datetime.now().strftime("%Y-%m-%d")
    lines = [
        f"# 🔭 [Weekly Radar] 创意视觉与生成艺术前沿开源推荐 ({now})",
        "",
        "> 本 Issue 由 GitHub Actions 自动化雷达流水线每周定时生成，精选当前社区最高星、最具艺术视觉价值的代码仓库，可供评估收录至 `beautiful-py` 展厅。",
        ""
    ]
    for cat, q in QUERIES:
        lines.append(f"## 🌟 {cat}")
        lines.append("| 仓库名 | 获赞 | 协议 | 简介 | 链接 |")
        lines.append("| :--- | :---: | :---: | :--- | :--- |")
        for it in search(q, 4):
            desc = (it.get("description") or "无描述").replace("|", "-").strip()
            lic = (it.get("license") or {}).get("spdx_id") or "None"
            lines.append(f"| **{it['full_name']}** | ★ {it['stargazers_count']:,} | `{lic}` | {desc[:80]} | [查看]({it['html_url']}) |")
        lines.append("")

    lines.append("---")
    lines.append("### 💡 一键收录提示")
    lines.append("```bash")
    lines.append("python run.py --import <本地文件或目录>")
    lines.append("python run.py --build")
    lines.append("```")
    report = "\n".join(lines)
    print(report)
    Path("trend_report.md").write_text(report, encoding="utf-8")

if __name__ == "__main__":
    main()
