#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the README figure set for dsh-dida.

Outputs (docs/assets/, overwritten in place):

  dsh-dida-hero-{zh,en}-{light,dark}.webp   1440x576 hero banner (Pillow)
  dsh-dida-flow-v5-{light,dark}.svg         1100x660 structure figure (hand SVG)

Both figures are derived from what this package actually ships, never from a
generic pipeline template:

Hero — the plugin's own surface pair. The session header carries one
`ticktick` action; opening it gives the task popup drawn here (list filter,
undone/completed views, full-text search, quick add with a date, rows with
checkbox / due chip / list chip / delete, the per-list warning line and the
connection dot) — every label is a shipped locale string or a real date chip
(`today`, `tomorrow`, the ISO key for an overdue row) from src/client. On the
right of the popup sit the eleven tool names and the one wire frame
(`tools/call` over `mcp.dida365.com`, Bearer + session id, 429 Retry-After,
`isError` thrown).

Structure — a bridge map, not a left-to-right node chain: three surfaces fan
into one `TicktickService` (left column + fan-in), the service carries three
in-card gates (protectedTaskIds, resolveToken per request, ensure()'s lazy
client), the single wire leaves for the official endpoint, and two loops stay
attached to it — the measured `setDue` detour ring (project task: update
crashes, move to inbox, update, move back in `finally`) and the 401 → reset()
return into the token gate. The footer carries the result shapes and the
per-list warning rule.

The hero is raster and localized (zh for README.md, en for the four
translations). The structure figure is token-only English, so one light/dark
pair serves all five READMEs.

Run:  python scripts/gen-readme-assets.py
Needs: Pillow and the Windows fonts msyh.ttc / msyhbd.ttc / consola.ttf.
"""

from __future__ import annotations

import math
import os
import sys
from xml.sax.saxutils import escape

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "docs", "assets")
NAME = "dsh-dida"

FONT_DIR = r"C:\Windows\Fonts"
F_REG = os.path.join(FONT_DIR, "msyh.ttc")
F_BOLD = os.path.join(FONT_DIR, "msyhbd.ttc")
F_MONO = os.path.join(FONT_DIR, "consola.ttf")
F_MONO_BOLD = os.path.join(FONT_DIR, "consolab.ttf")

for _path in (F_REG, F_BOLD, F_MONO):
    if not os.path.exists(_path):
        sys.exit(f"FATAL: missing font {_path}; this repo's figures use "
                 f"msyh.ttc / msyhbd.ttc / consola.ttf")

_FONTS: dict[tuple[str, int], ImageFont.FreeTypeFont] = {}


def F(path: str, size: int) -> ImageFont.FreeTypeFont:
    """Cached FreeType face."""
    key = (path, int(size))
    if key not in _FONTS:
        _FONTS[key] = ImageFont.truetype(path, int(size))
    return _FONTS[key]


def rgb(value: str) -> tuple[int, int, int]:
    value = value.lstrip("#")
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))


def rgba(value: str, alpha: int = 255) -> tuple[int, int, int, int]:
    return rgb(value) + (alpha,)


# ---------------------------------------------------------------------------
# shared skins (family palette: #4B67B4, dark #8496f5)
# ---------------------------------------------------------------------------
HERO_SKIN = {
    "light": dict(
        bg=("#f9f6fd", "#e4eaf8"), glow=("#4B67B4", 22),
        card="#ffffff", row="#f4f7fd", stroke="#d6dded",
        text="#1b2233", body="#2b3347", sub="#5a6275", faint="#8a93a8",
        accent="#4B67B4", accent_soft="#eef1fa", dash="#8fa2d8",
        amber="#b45309", amber_soft="#fdf1e1", green="#15803d", green_soft="#e8f5ec",
        shadow=(52, 72, 130, 26),
    ),
    "dark": dict(
        bg=("#131a2a", "#0c1016"), glow=("#4B67B4", 54),
        card="#1b2438", row="#202a41", stroke="#2b3550",
        text="#eef2fb", body="#d7def0", sub="#9aa7c2", faint="#6f7c96",
        accent="#8496f5", accent_soft="#202b45", dash="#4d5f96",
        amber="#fbbf24", amber_soft="#33280f", green="#4ade80", green_soft="#12291c",
        shadow=(0, 0, 0, 110),
    ),
}

FLOW_SKIN = {
    "light": dict(
        bg=("#f9f6fd", "#e4eaf8"),
        card="#ffffff", stroke="#d6dded", rowbg="#f4f7fd",
        text="#1b2233", body="#2f3750", sub="#5a6275", faint="#8a93a8",
        accent="#4B67B4", accent_soft="#eef1fa", green="#15803d",
        amber="#b45309", dash="#8fa2d8",
        shadow="#2a3a6a", shadow_op="0.16",
    ),
    "dark": dict(
        bg=("#131a2a", "#0c1016"),
        card="#1b2438", stroke="#2b3550", rowbg="#202a41",
        text="#eef2fb", body="#d7def0", sub="#9aa7c2", faint="#6f7c96",
        accent="#8496f5", accent_soft="#202b45", green="#4ade80",
        amber="#fbbf24", dash="#4d5f96",
        shadow="#000000", shadow_op="0.55",
    ),
}

# ---------------------------------------------------------------------------
# hero copy — zh for README.md, en for the four translated READMEs
# ---------------------------------------------------------------------------
HERO = {
    "zh": dict(
        kicker="DSH 插件 · 滴答清单任务桥",
        title=[("滴答待办", "text"), ("进会话", "accent")],
        value=["面板给手指：筛选、勾选、改期、拖拽排序",
               "工具给模型：11 个 ticktick_* 直接读写"],
        subtitle="全部走官方滴答 MCP 端点 · 插件不建本地任务库",
        meta="会话面板 · 11 个工具 · 配置卡 · Apache-2.0",
        footer1="github.com/PerryLink/dsh-dida",
        footer2="社区插件 · Apache-2.0 · 与 DeepSeek 无关",
        session="会话头部 · 动作槽",
        action="滴答清单",
        all_lists="全部清单",
        view_undone="未完成",
        view_done="已完成",
        search="搜索任务…",
        add="添加任务…",
        add_btn="添加",
        rows=[
            ("重排配置表", "2026-11-02", "工作"),
            ("补 0.3 迁移说明", "today", "工作"),
            ("周三需求评审", "tomorrow", "生活"),
            ("Q3 发票清算", None, "财务"),
        ],
        warning="警告：工作 清单校验失败，已跳过",
        status="● 已连接 · mcp.dida365.com",
        tools_title="11 × ticktick_*",
        wire_title="tools/call",
        wire_rows=["Bearer · session id", "429 → Retry-After ×1", "isError → throw"],
        sync="手机 / 桌面 / 网页同步",
        note="插件不建本地任务库 · 读取即云端当前状态",
    ),
    "en": dict(
        kicker="DSH PLUGIN · TICKTICK TASK BRIDGE",
        title=[("TickTick", "accent"), (" tasks", "text")],
        value=["A panel for your hands: filter, add, reschedule.",
               "Eleven ticktick_* tools on the same account."],
        subtitle="official TickTick MCP · no local task store",
        meta="session panel · 11 tools · settings card · Apache-2.0",
        footer1="github.com/PerryLink/dsh-dida",
        footer2="Community plugin · Apache-2.0 · not affiliated with DeepSeek",
        session="session header · actions",
        action="TickTick",
        all_lists="All lists",
        view_undone="Undone",
        view_done="Completed",
        search="Search tasks…",
        add="Add a task…",
        add_btn="Add",
        rows=[
            ("reflow config", "2026-11-02", "Work"),
            ("write 0.3 notes", "today", "Work"),
            ("design review", "tomorrow", "Life"),
            ("Q3 invoices", None, "Finance"),
        ],
        warning="Warning: Work list failed validation, skipped",
        status="● connected · mcp.dida365.com",
        tools_title="11 × ticktick_*",
        wire_title="tools/call",
        wire_rows=["Bearer · session id", "429 → Retry-After ×1", "isError → throw"],
        sync="phone / desktop / web sync",
        note="no local task store · reads are the live cloud state",
    ),
}

TOOLS_READ = ["ticktick_status", "ticktick_lists", "ticktick_tasks",
              "ticktick_completed", "ticktick_search"]
TOOLS_WRITE = ["ticktick_add", "ticktick_batch_add", "ticktick_complete",
               "ticktick_delete", "ticktick_due", "ticktick_reorder"]


# ---------------------------------------------------------------------------
# Pillow helpers
# ---------------------------------------------------------------------------
def gradient(w: int, h: int, top: str, bottom: str) -> Image.Image:
    """Vertical brand gradient."""
    img = Image.new("RGBA", (w, h))
    draw = ImageDraw.Draw(img)
    c0, c1 = rgb(top), rgb(bottom)
    for y in range(h):
        t = y / (h - 1)
        draw.line([(0, y), (w, y)],
                  fill=tuple(int(c0[i] + (c1[i] - c0[i]) * t) for i in range(3)) + (255,))
    return img


def glow(img: Image.Image, cx: int, cy: int, rx: int, ry: int,
         color: str, alpha: int, blur: int) -> Image.Image:
    """Soft accent bloom so the flat gradient does not look dead."""
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(layer).ellipse((cx - rx, cy - ry, cx + rx, cy + ry),
                                  fill=rgba(color, alpha))
    return Image.alpha_composite(img, layer.filter(ImageFilter.GaussianBlur(blur)))


def paint_shadows(img: Image.Image, specs, color, blur: int = 18, dy: int = 8) -> Image.Image:
    """Composite every card shadow in one blurred pass."""
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    for box, radius in specs:
        draw.rounded_rectangle((box[0], box[1] + dy, box[2], box[3] + dy),
                               radius=radius, fill=color)
    return Image.alpha_composite(img, layer.filter(ImageFilter.GaussianBlur(blur)))


def card(draw: ImageDraw.ImageDraw, box, radius: int, fill, stroke=None,
         width: int = 1) -> None:
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=stroke, width=width)


def dashed_round_rect(draw: ImageDraw.ImageDraw, box, radius: int, color,
                      width: int = 2, dash: int = 7, gap: int = 6) -> None:
    """Dashed rounded border (Pillow has no dash pattern)."""
    x0, y0, x1, y1 = box
    r = radius
    pts: list[tuple[float, float]] = []

    def arc(cx: float, cy: float, start: float, end: float) -> None:
        steps = max(6, int(abs(end - start) / 3))
        for i in range(steps + 1):
            a = math.radians(start + (end - start) * i / steps)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))

    pts.extend((x0 + r + i, y0) for i in range(0, max(1, int(x1 - x0 - 2 * r)), 2))
    arc(x1 - r, y0 + r, -90, 0)
    pts.extend((x1, y0 + r + i) for i in range(0, max(1, int(y1 - y0 - 2 * r)), 2))
    arc(x1 - r, y1 - r, 0, 90)
    pts.extend((x1 - r - i, y1) for i in range(0, max(1, int(x1 - x0 - 2 * r)), 2))
    arc(x0 + r, y1 - r, 90, 180)
    pts.extend((x0, y1 - r - i) for i in range(0, max(1, int(y1 - y0 - 2 * r)), 2))
    arc(x0 + r, y0 + r, 180, 270)
    pts.append(pts[0])

    on, left = True, float(dash)
    prev = pts[0]
    for point in pts[1:]:
        seg = math.dist(prev, point)
        while seg > 0:
            step = min(seg, left)
            t = step / seg
            nxt = (prev[0] + (point[0] - prev[0]) * t, prev[1] + (point[1] - prev[1]) * t)
            if on:
                draw.line([prev, nxt], fill=color, width=width)
            prev = nxt
            seg -= step
            left -= step
            if left <= 1e-6:
                on = not on
                left = float(dash if on else gap)


def fit(path: str, text: str, size: int, maxw: float, minsize: int,
        label: str = "") -> ImageFont.FreeTypeFont:
    """Largest face size <= size that fits maxw (never below minsize)."""
    while size > minsize and F(path, size).getlength(text) > maxw:
        size -= 1
    face = F(path, size)
    if face.getlength(text) > maxw:
        print(f"WARN hero: {label or text[:18]!r} is "
              f"{face.getlength(text):.0f}px > {maxw:.0f}px at {minsize}px")
    return face


def put(draw: ImageDraw.ImageDraw, xy, text: str, face, fill,
        anchor: str = "ls") -> None:
    draw.text(xy, text, font=face, fill=fill, anchor=anchor)


def auto_face(text: str, size: int, *, mono: bool = False,
              bold: bool = False) -> ImageFont.FreeTypeFont:
    """Consolas has no CJK, so mixed strings fall back to YaHei."""
    ascii_only = all(ord(ch) < 128 for ch in text)
    if mono and ascii_only:
        return F(F_MONO_BOLD if bold else F_MONO, size)
    return F(F_BOLD if bold else F_REG, size)


def put_runs(draw: ImageDraw.ImageDraw, x: int, baseline: int, runs, face,
             palette: dict) -> int:
    """Draw colour-segmented runs of one title line."""
    cursor = x
    for text, key in runs:
        put(draw, (cursor, baseline), text, face, palette[key])
        cursor += face.getlength(text)
    return cursor


def pill(draw: ImageDraw.ImageDraw, box, radius: int, label: str, face,
         fill, color, stroke=None, width: int = 1, anchor: str = "m") -> None:
    """Rounded chip with one centred label."""
    card(draw, box, radius, fill, stroke, width)
    cx = (box[0] + box[2]) / 2
    cy = (box[1] + box[3]) / 2
    put(draw, (cx, cy), label, face, color, anchor="mm")


# ---------------------------------------------------------------------------
# hero 1440x576
# ---------------------------------------------------------------------------
def hero(lang: str, theme: str) -> Image.Image:
    L, c = HERO[lang], HERO_SKIN[theme]
    w, h = 1440, 576
    img = gradient(w, h, c["bg"][0], c["bg"][1])
    img = glow(img, 1180, 190, 470, 300, c["glow"][0], c["glow"][1], 170)
    img = glow(img, 170, 540, 430, 230, c["glow"][0], max(6, c["glow"][1] // 2), 170)

    # geometry -------------------------------------------------------------
    header = (700, 56, 1052, 112)
    panel = (700, 124, 1052, 540)
    tools = (1068, 56, 1372, 330)
    wire = (1068, 346, 1372, 540)
    row_boxes = [(720, 266 + i * 47, 1032, 308 + i * 47) for i in range(4)]

    img = paint_shadows(img, [(header, 20), (panel, 22), (tools, 20), (wire, 20)] +
                        [(box, 12) for box in row_boxes], c["shadow"])
    d = ImageDraw.Draw(img)

    # left column: kicker / title / value lines / subtitle / meta / footer -
    kicker_face = F(F_BOLD, 16)
    kx, ky = 72, 56
    kw = int(kicker_face.getlength(L["kicker"])) + 58
    card(d, (kx, ky, kx + kw, ky + 42), 21, rgba(c["accent_soft"], 240), c["stroke"], 1)
    d.ellipse((kx + 18, ky + 15, kx + 30, ky + 27), fill=c["accent"])
    put(d, (kx + 38, ky + 27), L["kicker"], kicker_face, c["body"])

    title_face = F(F_BOLD, 80)
    title_w = sum(title_face.getlength(t) for t, _ in L["title"])
    if title_w > 600:
        sys.exit(f"FATAL: {lang} title is {title_w:.0f}px wide, column is 600px")
    put_runs(d, 72, 208, L["title"], title_face, c)

    for i, line in enumerate(L["value"]):
        face = fit(F_REG, line, 30, 600, 26, f"{lang} value {i + 1}")
        put(d, (72, 258 + i * 42), line, face, c["body"])

    sub_face = fit(F_REG, L["subtitle"], 26, 600, 23, f"{lang} subtitle")
    put(d, (72, 352), L["subtitle"], sub_face, c["sub"])
    meta_face = fit(F_REG, L["meta"], 20, 600, 18, f"{lang} meta")
    put(d, (72, 398), L["meta"], meta_face, c["sub"])
    d.line((72, 436, 672, 436), fill=c["stroke"], width=1)

    foot1 = fit(F_MONO, L["footer1"], 17, 600, 15, f"{lang} footer link")
    put(d, (72, 474), L["footer1"], foot1, c["sub"])
    foot2 = fit(F_REG, L["footer2"], 15, 600, 13, f"{lang} footer note")
    put(d, (72, 500), L["footer2"], foot2, c["faint"])

    # right: the session header + its one action ---------------------------
    card(d, header, 20, c["card"], c["stroke"], 1)
    put(d, (720, 92), L["session"], auto_face(L["session"], 12), c["faint"])
    act_face = F(F_BOLD, 13.5)
    aw = int(act_face.getlength(L["action"])) + 44
    abox = (1036 - aw, 70, 1036, 98)
    card(d, abox, 14, rgba(c["accent_soft"], 245), c["accent"], 1)
    ax0, ay0 = abox[0] + 12, abox[1] + 8
    d.rounded_rectangle((ax0, ay0, ax0 + 13, ay0 + 13), radius=3,
                        outline=c["accent"], width=2)
    d.line((ax0 + 3, ay0 + 7, ax0 + 6, ay0 + 10), fill=c["accent"], width=2)
    d.line((ax0 + 6, ay0 + 10, ax0 + 11, ay0 + 4), fill=c["accent"], width=2)
    put(d, (ax0 + 21, abox[1] + 20), L["action"], act_face, c["accent"])

    # right: the task popup -------------------------------------------------
    card(d, panel, 22, c["card"], c["stroke"], 1)

    # filter row: list select, view toggles, status dot
    card(d, (720, 138, 824, 172), 10, c["row"], c["stroke"], 1)
    put(d, (732, 162), L["all_lists"], F(F_REG, 13.5), c["body"])
    d.line((810, 154, 815, 159), fill=c["sub"], width=2)
    d.line((815, 159, 820, 154), fill=c["sub"], width=2)
    tab_face = F(F_BOLD, 13.5)
    tab1_x = 840
    put(d, (tab1_x, 161), L["view_undone"], tab_face, c["accent"])
    d.line((tab1_x, 172, tab1_x + tab_face.getlength(L["view_undone"]), 172),
           fill=c["accent"], width=2)
    tab2_x = tab1_x + tab_face.getlength(L["view_undone"]) + 24
    put(d, (tab2_x, 161), L["view_done"], F(F_REG, 13.5), c["faint"])
    card(d, (990, 142, 1024, 168), 13, rgba(c["green_soft"], 245),
         rgba(c["green"], 90), 1)
    put(d, (1007, 155), "●", F(F_REG, 11), c["green"], anchor="mm")

    # search row
    card(d, (720, 182, 1032, 214), 10, c["row"], c["stroke"], 1)
    put(d, (732, 203), L["search"], F(F_REG, 13.5), c["faint"])

    # add row
    card(d, (720, 222, 868, 254), 10, c["row"], c["stroke"], 1)
    put(d, (732, 243), L["add"], F(F_REG, 13.5), c["faint"])
    card(d, (874, 222, 962, 254), 10, c["row"], c["stroke"], 1)
    put(d, (886, 243), "2026-11-08", F(F_MONO, 11.5), c["sub"])
    card(d, (968, 222, 1032, 254), 10, rgba(c["accent_soft"], 245), c["accent"], 1)
    put(d, (1000, 243), L["add_btn"], F(F_BOLD, 13), c["accent"], anchor="mm")

    # task rows: checkbox / title / list chip / due chip / delete
    due_style = {"today": (c["amber"], c["amber_soft"]),
                 "tomorrow": (c["sub"], c["row"])}
    for box, (title, due, project) in zip(row_boxes, L["rows"]):
        card(d, box, 12, c["row"], None, 0)
        cy = (box[1] + box[3]) // 2
        d.rounded_rectangle((730, cy - 8, 746, cy + 8), radius=4,
                            outline=c["dash"], width=2)
        title_face = F(F_REG, 15.5)
        delete_face = F(F_REG, 12)
        put(d, (1018, cy + 4), "×", delete_face, c["faint"], anchor="rs")

        due_right = 998
        if due is not None:
            color, back = due_style.get(due, (c["amber"], c["amber_soft"]))
            face = F(F_BOLD, 11.5)
            dw = int(face.getlength(due)) + 18
            card(d, (due_right - dw, cy - 10, due_right, cy + 10), 10, back, None, 0)
            put(d, (due_right - dw / 2, cy), due, face, color, anchor="mm")
            due_left = due_right - dw
        else:
            due_left = due_right

        project_face = F(F_REG, 11)
        pw = int(project_face.getlength(project)) + 16
        card(d, (due_left - 8 - pw, cy - 10, due_left - 8, cy + 10), 10,
             rgba(c["card"], 200), c["stroke"], 1)
        put(d, (due_left - 8 - pw / 2, cy), project, project_face, c["sub"], anchor="mm")

        put(d, (756, cy + 5), title, title_face, c["body"])

    # warning + connection line
    put(d, (720, 466), L["warning"], F(F_REG, 12), c["amber"])
    put(d, (720, 500), L["status"], F(F_REG, 12), c["sub"])

    # right column: the eleven tools ---------------------------------------
    card(d, tools, 20, c["card"], c["stroke"], 1)
    put(d, (1088, 86), L["tools_title"], F(F_BOLD, 15), c["text"])
    put(d, (1088, 110), "READ", F(F_MONO_BOLD, 10.5), c["faint"])
    for i, name in enumerate(TOOLS_READ):
        put(d, (1088, 130 + i * 17.5), name, F(F_MONO, 12.5), c["sub"])
    put(d, (1088, 228), "WRITE", F(F_MONO_BOLD, 10.5), c["faint"])
    for i, name in enumerate(TOOLS_WRITE):
        put(d, (1088, 248 + i * 17.5), name, F(F_MONO, 12.5), c["body"])

    # right column: the one wire frame --------------------------------------
    card(d, wire, 20, c["card"], c["stroke"], 1)
    put(d, (1088, 378), L["wire_title"], F(F_MONO_BOLD, 13.5), c["accent"])
    for i, line in enumerate(L["wire_rows"]):
        put(d, (1088, 404 + i * 22), line, auto_face(line, 12.5, mono=True), c["sub"])
    card(d, (1088, 464, 1352, 496), 10, rgba(c["accent_soft"], 245), None, 0)
    put(d, (1100, 484), "mcp.dida365.com", F(F_MONO_BOLD, 12), c["accent"])
    put(d, (1088, 522), L["sync"], F(F_REG, 11.5), c["faint"])

    put(d, (700, 566), L["note"], F(F_REG, 12.5), c["faint"])

    return img


# ---------------------------------------------------------------------------
# structure figure 1100x660 (hand-written SVG)
# ---------------------------------------------------------------------------
def flow_svg(theme: str) -> str:
    c = FLOW_SKIN[theme]
    p: list[str] = []
    add = p.append

    def t(x, y, s, size, fill, weight=400, anchor="start", mono=False,
          spacing=None) -> str:
        family = ("'Consolas','Cascadia Mono',monospace" if mono
                  else "'Microsoft YaHei','Segoe UI',sans-serif")
        attrs = [f'x="{x}"', f'y="{y}"', f'font-size="{size}"',
                 f'fill="{fill}"', f'font-family="{family}"']
        if weight != 400:
            attrs.append(f'font-weight="{weight}"')
        if anchor != "start":
            attrs.append(f'text-anchor="{anchor}"')
        if spacing is not None:
            attrs.append(f'letter-spacing="{spacing}"')
        return f'<text {" ".join(attrs)}>{escape(s)}</text>'

    def rect(x0, y0, x1, y1, r, fill, stroke=None, sw=1, dashed=False,
             shadow=False) -> str:
        attrs = [f'x="{x0}"', f'y="{y0}"', f'width="{x1 - x0}"',
                 f'height="{y1 - y0}"', f'rx="{r}"', f'fill="{fill}"']
        if stroke:
            attrs += [f'stroke="{stroke}"', f'stroke-width="{sw}"']
        if dashed:
            attrs.append('stroke-dasharray="7 6"')
        if shadow:
            attrs.append('filter="url(#soft)"')
        return f'<rect {" ".join(attrs)}/>'

    # shell -----------------------------------------------------------------
    add('<?xml version="1.0" encoding="UTF-8"?>')
    add(f'<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="660" '
        f'viewBox="0 0 1100 660" role="img" aria-labelledby="fig-title">')
    add('<title id="fig-title">dsh-dida — one guarded wire: three surfaces, one '
        'remote namespace, one MCP endpoint</title>')
    add('<desc>Three surfaces (session-header panel, eleven tools, config card '
        'that writes the profile row) fan into TicktickService, whose three '
        'gates are protectedTaskIds, a per-request token resolve and a lazy '
        'client bootstrap; the single wire leaves for mcp.dida365.com and the '
        'TickTick cloud. Two loops stay attached: the measured setDue detour '
        'and the 401 reset back into the token gate.</desc>')
    add('<defs>')
    add(f'<linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{c["bg"][0]}"/>'
        f'<stop offset="1" stop-color="{c["bg"][1]}"/></linearGradient>')
    add(f'<filter id="soft" x="-25%" y="-25%" width="150%" height="150%">'
        f'<feDropShadow dx="0" dy="6" stdDeviation="10" '
        f'flood-color="{c["shadow"]}" flood-opacity="{c["shadow_op"]}"/></filter>')
    for key, color in (("acc", c["accent"]), ("sub", c["sub"]),
                       ("fnt", c["faint"]), ("amb", c["amber"])):
        add(f'<marker id="arr-{key}" viewBox="0 0 10 10" refX="9" refY="5" '
            f'markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
            f'<path d="M0 0L10 5L0 10Z" fill="{color}"/></marker>')
    add('</defs>')
    add('<rect width="1100" height="660" fill="url(#bg)"/>')

    # header ----------------------------------------------------------------
    add(t(48, 54, "dsh-dida · one guarded wire", 22, c["text"], weight=700))
    add(t(1052, 54, "v0.2.0 · Apache-2.0", 13, c["faint"], anchor="end", mono=True))
    add(t(48, 82, "three surfaces → one Remote namespace → one MCP wire; the "
                  "token is re-read per request, a 401 drops the client",
          13, c["sub"]))

    # left: surfaces --------------------------------------------------------
    add(t(48, 116, "SURFACES", 12, c["faint"], weight=700, mono=True, spacing=1.5))
    add(rect(48, 126, 296, 208, 18, c["card"], c["stroke"], 1, shadow=True))
    add(t(66, 152, "session header", 14, c["text"], weight=700))
    add(t(66, 172, "ticktick panel", 12, c["sub"]))
    add(t(66, 194, "ctx.remote.ticktick.*", 11.5, c["accent"], mono=True))

    add(rect(48, 218, 296, 300, 18, c["card"], c["stroke"], 1, shadow=True))
    add(t(66, 244, "11 × ticktick_* tools", 14, c["text"], weight=700))
    add(t(66, 264, "ctx.tools", 11.5, c["accent"], mono=True))
    add(t(66, 286, "read 5 · write 6", 12, c["sub"]))

    add(rect(48, 310, 296, 392, 18, c["card"], c["stroke"], 1, shadow=True))
    add(t(66, 336, "plugins.row.config", 14, c["text"], weight=700, mono=True))
    add(t(66, 356, "ctx.configForms", 11.5, c["accent"], mono=True))
    add(t(66, 378, "writes the profile row", 12, c["sub"]))

    add(rect(48, 404, 296, 472, 16, c["rowbg"], c["dash"], 1.4, dashed=True))
    add(t(66, 428, "profile row: ticktick", 12.5, c["body"], weight=700, mono=True))
    add(t(66, 450, "Volatile Config · live", 12, c["sub"]))

    # left: token ladder (the resolveToken() priority, as text) -------------
    add(rect(48, 484, 296, 586, 18, c["card"], c["stroke"], 1, shadow=True))
    add(t(66, 504, "TOKEN · resolveToken()", 11.5, c["faint"], weight=700,
          mono=True, spacing=0.5))
    add(rect(66, 510, 278, 530, 8, c["accent_soft"], None, 0))
    add(t(76, 525, "1 settings secret", 12, c["accent"], mono=True))
    add(rect(66, 534, 254, 554, 8, c["rowbg"], c["stroke"], 1))
    add(t(76, 549, "2 DIDA365_TOKEN", 12, c["body"], mono=True))
    add(rect(66, 558, 230, 578, 8, c["rowbg"], c["stroke"], 1))
    add(t(76, 573, "3 tokenFile · $DSH_HOME", 11.5, c["sub"], mono=True))

    # fan-in into the service ----------------------------------------------
    add(f'<path d="M296 167H316" stroke="{c["accent"]}" stroke-width="2" '
        f'marker-end="url(#arr-acc)"/>')
    add(f'<path d="M296 259H316" stroke="{c["accent"]}" stroke-width="2" '
        f'marker-end="url(#arr-acc)"/>')
    add(f'<path d="M296 438H306V287H316" stroke="{c["dash"]}" stroke-width="1.8" '
        f'fill="none" stroke-dasharray="6 5" marker-end="url(#arr-fnt)"/>')
    add(f'<path d="M172 392V400" stroke="{c["dash"]}" stroke-width="1.8" '
        f'stroke-dasharray="5 4" marker-end="url(#arr-fnt)"/>')

    # centre: the service card with its three gates ------------------------
    add(rect(320, 126, 676, 586, 20, c["card"], c["stroke"], 1, shadow=True))
    add(t(340, 154, "TicktickService", 16, c["text"], weight=700))
    add(t(340, 174, "Remote ns ticktick · one policy for both faces", 12, c["sub"]))
    add(f'<line x1="340" y1="184" x2="656" y2="184" stroke="{c["stroke"]}"/>')

    add(rect(336, 192, 660, 254, 14, c["rowbg"], None, 0))
    add(t(350, 213, "G1 · protectedTaskIds", 13, c["accent"], weight=700))
    add(t(350, 234, "a mutating call is refused before any wire call", 12, c["body"]))
    add(t(350, 249, "→ ticktick/protected", 11.5, c["sub"], mono=True))

    add(rect(336, 260, 660, 322, 14, c["rowbg"], None, 0))
    add(t(350, 281, "G2 · resolveToken() per request", 13, c["accent"], weight=700))
    add(t(350, 302, "secret > DIDA365_TOKEN > tokenFile", 12, c["body"], mono=True))
    add(t(350, 317, "null → ticktick/no-token · 401 → reset()", 11.5, c["sub"]))

    add(rect(336, 328, 660, 410, 14, c["rowbg"], None, 0))
    add(t(350, 346, "G3 · ensure() · lazy client per token", 13, c["accent"], weight=700))
    add(t(350, 366, "initialize + tools/list → resolver", 12, c["body"], mono=True))
    add(t(350, 385, "pins | pattern · client cached per token", 12, c["sub"]))
    add(t(350, 402, "token changed / bootFailed → rebuild", 12, c["sub"]))

    # centre: the measured setDue detour as a ring --------------------------
    add(f'<path d="M350 410V424" stroke="{c["dash"]}" stroke-width="1.6" '
        f'stroke-dasharray="5 4"/>')
    add(rect(336, 424, 660, 572, 14, c["card"], c["amber"], 1.4, dashed=True))
    add(t(350, 448, "MEASURED DETOUR · setDue on project tasks", 11.5,
          c["amber"], weight=700))
    add(t(350, 468, "trigger: 'Expecting value: line 1 column 1'", 11.5, c["sub"]))
    ring_cx, ring_cy, ring_r = 392, 516, 24
    add(f'<circle cx="{ring_cx}" cy="{ring_cy}" r="{ring_r}" fill="none" '
        f'stroke="{c["amber"]}" stroke-width="1.2" stroke-opacity="0.55"/>')
    a0, a1 = math.radians(-78), math.radians(-22)
    x0, y0 = ring_cx + ring_r * math.cos(a0), ring_cy + ring_r * math.sin(a0)
    x1, y1 = ring_cx + ring_r * math.cos(a1), ring_cy + ring_r * math.sin(a1)
    add(f'<path d="M{x0:.1f} {y0:.1f}A{ring_r} {ring_r} 0 0 1 {x1:.1f} {y1:.1f}" '
        f'fill="none" stroke="{c["amber"]}" stroke-width="1.8" '
        f'marker-end="url(#arr-amb)"/>')
    for i, (dx, dy, label) in enumerate(((0, -ring_r, "1"), (ring_r, 0, "2"),
                                         (0, ring_r, "3"), (-ring_r, 0, "4"))):
        add(f'<circle cx="{ring_cx + dx}" cy="{ring_cy + dy}" r="9" '
            f'fill="{c["card"]}" stroke="{c["amber"]}" stroke-width="1.4"/>')
        add(t(ring_cx + dx, ring_cy + dy + 4, label, 11, c["amber"],
              weight=700, anchor="middle"))
    legend = ["update the project task", "move → inbox", "update the due date",
              "move back (finally)"]
    for i, line in enumerate(legend):
        add(t(444, 500 + i * 18, line, 11.5, c["body"]))

    # right: the wire, endpoint, cloud --------------------------------------
    add(t(724, 116, "WIRE", 12, c["faint"], weight=700, mono=True, spacing=1.5))
    add(rect(724, 126, 1052, 300, 18, c["card"], c["stroke"], 1, shadow=True))
    add(t(742, 152, "MCP client · streamable-HTTP", 13, c["text"], weight=700))
    add(t(742, 172, "tools/call → POST JSON-RPC", 11.5, c["accent"], mono=True))
    rows = ["initialize → session id + protocol version",
            "tools/list → raw tool names",
            "429 → Retry-After ×1",
            "isError → throw",
            "timeout: toolCallTimeoutMs"]
    for i, line in enumerate(rows):
        add(t(742, 194 + i * 20, line, 11.5, c["sub"], mono=True))

    add(rect(724, 310, 1052, 368, 18, c["card"], c["stroke"], 1, shadow=True))
    add(t(742, 338, "https://mcp.dida365.com", 13.5, c["accent"],
          weight=700, mono=True))
    add(t(742, 358, "official TickTick MCP · tools/call", 12, c["sub"]))

    add(rect(724, 378, 1052, 450, 18, c["card"], c["stroke"], 1, shadow=True))
    add(t(742, 402, "your TickTick account", 13, c["text"], weight=700))
    add(t(742, 422, "phone · desktop · web sync", 12, c["body"]))
    add(t(742, 442, "reads = current cloud state", 12, c["sub"]))

    add(rect(724, 460, 1052, 586, 18, c["card"], c["dash"], 1.4, dashed=True))
    add(t(742, 486, "PROBE · test connection", 12, c["accent"], weight=700))
    add(t(742, 508, "throwaway client · initialize + listTools", 11.5,
          c["body"], mono=True))
    add(t(742, 530, "→ { ok, toolCount, error }", 12, c["sub"], mono=True))
    add(t(742, 552, "feeds the settings card's Test connection", 12, c["body"]))
    add(t(742, 574, "the cached bridge client stays untouched", 12, c["sub"]))

    # connecting rails ------------------------------------------------------
    add(f'<path d="M676 236H720" stroke="{c["accent"]}" stroke-width="2.4" '
        f'marker-end="url(#arr-acc)"/>')
    add(f'<path d="M724 282H680" stroke="{c["amber"]}" stroke-width="1.8" '
        f'stroke-dasharray="6 5" marker-end="url(#arr-amb)"/>')
    add(t(690, 275, "401", 11, c["amber"], mono=True, anchor="middle"))
    add(f'<path d="M888 300V306" stroke="{c["accent"]}" stroke-width="2.2" '
        f'marker-end="url(#arr-acc)"/>')
    add(f'<path d="M888 368V374" stroke="{c["accent"]}" stroke-width="2.2" '
        f'marker-end="url(#arr-acc)"/>')

    # footer: result shapes and the read rule ------------------------------
    add(f'<line x1="48" y1="598" x2="1052" y2="598" stroke="{c["stroke"]}"/>')
    add(t(48, 620, "results: status {configured, connected, lastError} · "
                   "tasks {tasks[], warnings[]} · add {task, verifyWarning} · "
                   "ok {ok}", 12, c["sub"]))
    add(t(48, 640, "tasks(): projects[] → one tools/call per list → merge · an "
                   "unreadable list is skipped into warnings[] · no local task store",
          12, c["faint"]))

    add('</svg>')
    return "\n".join(p) + "\n"


# ---------------------------------------------------------------------------
# entry point
# ---------------------------------------------------------------------------
def main() -> None:
    os.makedirs(OUT, exist_ok=True)
    written: list[str] = []

    for lang in ("zh", "en"):
        for theme in ("light", "dark"):
            img = hero(lang, theme)
            path = os.path.join(OUT, f"{NAME}-hero-{lang}-{theme}.webp")
            img.convert("RGB").save(path, "WEBP", quality=92, method=6)
            written.append(path)

    for theme in ("light", "dark"):
        path = os.path.join(OUT, f"{NAME}-flow-v5-{theme}.svg")
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(flow_svg(theme))
        written.append(path)

    for path in written:
        print(f"wrote {os.path.relpath(path, ROOT)} "
              f"({os.path.getsize(path) // 1024} KB)")


if __name__ == "__main__":
    main()
