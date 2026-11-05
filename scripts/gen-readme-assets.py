#!/usr/bin/env python3
"""Generate README image assets for dsh-dida (docs/assets/).

Outputs (idempotent overwrite):
  dsh-dida-flow-light.svg / dsh-dida-flow-dark.svg
      Hero architecture diagram. Two hand-written SVG files (vector — never
      rasterized to webp). Text inside is command-surface tokens only
      (session header, ticktick_*, ctx.remote.ticktick.*, tools/call,
      https://mcp.dida365.com, ...), so all five README languages share the
      same pair.
  (No evidence chart: this repository ships no benchmark results, so there is
   no measured-data section and nothing to plot. WEBP_QUALITY is kept for
   future raster assets created by this same script.)

Run once:  python scripts/gen-readme-assets.py
Requires:  Pillow (pip install pillow)
"""
from __future__ import annotations

import os
import sys

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "docs", "assets")

# --- palette: PerryLink family (accent) + GitHub page backgrounds ----------
FAMILY = "#4B67B4"   # family accent (badges labelColor family uses #2B3245)
GREEN = {"light": "#16a34a", "dark": "#3fb950"}
ORANGE = {"light": "#bc4c00", "dark": "#d29922"}
SKIN = {
    "light": dict(bg="#ffffff", box="#f6f8fa", border="#d0d7de",
                  text="#1f2328", sub="#57606a", track="#eaeef2"),
    "dark": dict(bg="#0d1117", box="#161b22", border="#30363d",
                 text="#f0f6fc", sub="#8b949e", track="#21262d"),
}

# --- CJK font probe: Chinese must never render as tofu boxes ----------------
FONT_CANDIDATES = [
    r"C:\Windows\Fonts\msyh.ttc",      # Microsoft YaHei
    r"C:\Windows\Fonts\simhei.ttf",    # SimHei
    r"C:\Windows\Fonts\Deng.ttf",      # DengXian
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/System/Library/Fonts/PingFang.ttc",
]
FONT_PATH = next((p for p in FONT_CANDIDATES if os.path.exists(p)), None)
if FONT_PATH is None:
    sys.exit("FATAL: no CJK font found (looked for msyh.ttc, simhei.ttf, "
             "Deng.ttf, Noto Sans CJK, PingFang). Refusing to render Chinese "
             "as tofu boxes; install one of the probed fonts and re-run.")

WEBP_QUALITY = 90


def font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_PATH, size)


# ---------------------------------------------------------------------------
# 1. Hero architecture SVG (light + dark)
# ---------------------------------------------------------------------------
def node(parts: list[str], s: dict, x: int, y: int, w: int, h: int,
         title: str, lines: list[str], accent: str | None = None,
         dashed: bool = False) -> None:
    stroke = accent or s["border"]
    dash = ' stroke-dasharray="6 5"' if dashed else ""
    parts.append(
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" '
        f'fill="{s["box"]}" stroke="{stroke}" stroke-width="2"{dash}/>')
    parts.append(
        f'<text x="{x + w // 2}" y="{y + 32}" fill="{s["text"]}" '
        f'text-anchor="middle" font-family="ui-monospace,monospace" '
        f'font-size="16" font-weight="700">{title}</text>')
    for i, line in enumerate(lines):
        parts.append(
            f'<text x="{x + w // 2}" y="{y + 56 + i * 22}" fill="{s["sub"]}" '
            f'text-anchor="middle" font-family="ui-monospace,monospace" '
            f'font-size="12">{line}</text>')


def arrow(parts: list[str], s: dict, d: str, tip: tuple[int, int],
          direction: str) -> None:
    parts.append(
        f'<path d="{d}" fill="none" stroke="{s["sub"]}" stroke-width="2.5" '
        f'stroke-linecap="round" stroke-linejoin="round"/>')
    x, y = tip
    if direction == "right":
        head = f'M{x - 8} {y - 5}l8 5-8 5'
    else:  # down
        head = f'M{x - 5} {y - 8}l5 8 5-8'
    parts.append(
        f'<path d="{head}" fill="none" stroke="{s["sub"]}" stroke-width="2.5" '
        f'stroke-linecap="round" stroke-linejoin="round"/>')


def flow_svg(skin: str) -> str:
    s = SKIN[skin]
    w, h = 1200, 580
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}" role="img" aria-label="dsh-dida architecture: '
        f'session header and ticktick_* tools feed TicktickService, which '
        f'calls the official TickTick MCP endpoint; the configuration card '
        f'writes the profile row">',
        '<title>dsh-dida architecture</title>',
        f'<rect width="{w}" height="{h}" rx="18" fill="{s["bg"]}"/>',
        f'<text x="60" y="62" fill="{s["text"]}" font-family="ui-sans-serif,'
        f'system-ui,sans-serif" font-size="30" font-weight="700">dsh-dida</text>',
        f'<text x="60" y="94" fill="{s["sub"]}" font-family="ui-monospace,'
        f'monospace" font-size="16">TickTick / Dida365 task bridge · official '
        f'MCP endpoint · panel + 11 tools</text>',
        f'<line x1="60" y1="116" x2="1140" y2="116" stroke="{s["border"]}"/>',
    ]

    # Left-hand inputs.
    node(parts, s, 60, 150, 300, 84, "session header",
         ["action: ticktick"])
    node(parts, s, 60, 270, 300, 84, "ticktick_* tools",
         ["ctx.tools"])
    node(parts, s, 60, 390, 300, 84, "plugins.row.config",
         ["ctx.configForms"])

    # Service, MCP client, endpoint.
    node(parts, s, 470, 210, 260, 140, "TicktickService",
         ["Remote namespace: ticktick", "ctx.remote.ticktick.*",
          "tools/call"], accent=FAMILY)
    node(parts, s, 810, 210, 310, 110, "MCP client",
         ["streamable HTTP", "session id · Retry-After"])
    node(parts, s, 810, 360, 310, 70, "https://mcp.dida365.com",
         ["official TickTick MCP"], accent=GREEN[skin])

    # Configuration page writes the profile row (not the service).
    node(parts, s, 470, 420, 260, 90, "profile row: ticktick",
         ["Volatile Config", "no restart"], dashed=True)

    # Token sources note.
    node(parts, s, 810, 450, 310, 80, "token",
         ["token &gt; DIDA365_TOKEN &gt; tokenFile",
          "re-read per request · 401 → reset"])

    # Arrows: inputs -> service.
    arrow(parts, s, "M360 190h60v55h38", (464, 245), "right")
    arrow(parts, s, "M360 310h98", (464, 310), "right")
    # Configuration page -> profile row.
    arrow(parts, s, "M360 430h60v35h38", (464, 465), "right")
    # Service -> MCP client -> endpoint.
    arrow(parts, s, "M730 265h68", (804, 265), "right")
    arrow(parts, s, "M965 320v28", (965, 354), "down")

    parts.append(
        f'<text x="60" y="560" fill="{s["sub"]}" font-family="ui-monospace,'
        f'monospace" font-size="13">protectedTaskIds · refuse before wire · '
        f'reads = cloud state · writes = cloud account</text>')
    parts.append("</svg>")
    return "\n".join(parts) + "\n"


def main() -> None:
    os.makedirs(OUT, exist_ok=True)
    for skin in ("light", "dark"):
        with open(os.path.join(OUT, f"dsh-dida-flow-{skin}.svg"),
                  "w", encoding="utf-8", newline="\n") as fh:
            fh.write(flow_svg(skin))
    print("wrote 2 SVG hero assets to docs/assets/ "
          "(dsh-dida-flow-light.svg, dsh-dida-flow-dark.svg)")


if __name__ == "__main__":
    main()
