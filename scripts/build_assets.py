#!/usr/bin/env python3
"""Render the static profile SVGs (light and dark) from the shared design system.

Run from the repo root: python3 scripts/build_assets.py
Dynamic assets (stats, recently merged) are rendered by scripts/stats.py.
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from design import (THEMES, W, PAD, HEADER, R_IN, svg_open, panel, pill,
                    eyebrow, esc, write)

A = "assets"

S_BITS = [".####", "#....", "#....", ".###.", "....#", "....#", "####."]
W_BITS = ["#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"]


def monogram(t, x, y, cell=14, gap=3):
    """Pixel 'SW' monogram drawn with rects (no font dependency)."""
    o = []
    step = cell + gap
    for li, bits in enumerate((S_BITS, W_BITS)):
        ox = x + li * (5 * step + step)
        for r, row in enumerate(bits):
            for c, ch in enumerate(row):
                if ch == "#":
                    op = 1 if (r + c + li) % 3 else 0.72
                    o.append(f'<rect x="{ox + c * step}" y="{y + r * step}" width="{cell}" '
                             f'height="{cell}" rx="3" fill="{t["acc"]}" fill-opacity="{op}"/>')
    return "".join(o)


def banner(t):
    w, h = W, 300
    o = [svg_open(w, h, "Shubh Wadekar: CTO & Co-Founder @ XMobility, Product Designer, Security Researcher"),
         panel(t, 0, 0, w, h, glow_x=0.85, glow_y=0.15)]
    o.append(eyebrow(t, PAD + 8, 78, "~/thelastbackspace"))
    o.append(f'<text class="s" x="{PAD + 6}" y="152" font-size="62" font-weight="700" '
             f'letter-spacing="-1.5" fill="{t["text"]}">Shubh Wadekar</text>')
    o.append(f'<text class="s" x="{PAD + 8}" y="194" font-size="22" fill="{t["muted"]}">'
             'CTO &amp; Co-Founder @ XMobility · Product Designer · Security Researcher</text>')
    o.append(f'<rect x="{PAD + 8}" y="226" width="84" height="4" rx="2" fill="{t["acc"]}"/>')
    o.append(f'<text class="m" x="{PAD + 108}" y="233" font-size="17" fill="{t["muted"]}">'
             'Bengaluru, India</text>')
    # monogram tile, top right
    tx, ty, ts = w - PAD - 150, 40, 150
    o.append(f'<rect x="{tx}" y="{ty}" width="{ts}" height="{ts}" rx="{R_IN + 6}" fill="{t["bg"]}" '
             f'fill-opacity=".55" stroke="{t["border"]}"/>')
    o.append(monogram(t, tx + 10.5, ty + 34.5, cell=9, gap=3))
    return o


def about(t):
    w = W
    rows = [
        ("user", "thelastbackspace @ github"),
        ("role", "CTO & Co-Founder @ XMobility"),
        ("also", "Product Designer · Security Researcher"),
        ("craft", "Figma file to production"),
        ("stack", "TypeScript · React · Next.js · Node.js"),
        ("systems", "Rust · Go · Python · Zig · Postgres"),
        ("ai", "AI agents and MCP · Claude Code · Cursor"),
        ("location", "Bengaluru, India"),
        ("focus", "XMobility · security research · open source fixes"),
    ]
    top = HEADER + 44
    step = 32
    h = top + step * len(rows) + 64
    o = [svg_open(w, h, "About: " + "; ".join(f"{k}: {v}" for k, v in rows)),
         panel(t, 0, 0, w, h, title="neofetch", glow_x=0.1, glow_y=0.4)]
    # monogram column
    o.append(f'<g class="r" style="animation-delay:.2s">{monogram(t, PAD + 6, top + 10, cell=14, gap=3)}</g>')
    kx, vx = 330, 440
    o.append(f'<g class="r" style="animation-delay:.4s"><text class="m" x="{kx}" y="{top}" font-size="18" '
             f'font-weight="700" fill="{t["acc_text"]}">shubh<tspan fill="{t["muted"]}">@</tspan>'
             f'wadekar</text><rect x="{kx}" y="{top + 12}" width="168" height="1" fill="{t["border"]}"/></g>')
    for i, (k, v) in enumerate(rows):
        y = top + 44 + i * step
        o.append(f'<g class="r" style="animation-delay:{0.6 + i * 0.15:.2f}s">'
                 f'<text class="m" x="{kx}" y="{y}" font-size="17" fill="{t["acc_text"]}">{esc(k)}</text>'
                 f'<text class="m" x="{vx}" y="{y}" font-size="17" fill="{t["text"]}">{esc(v)}</text></g>')
    # neofetch colour row
    sy = top + 44 + len(rows) * step - 14
    sw = ["#30363d", "#ff5f57", "#febc2e", "#28c840", t["acc"], "#58a6ff", "#bc8cff", t["text"]]
    cells = "".join(f'<rect x="{kx + i * 30}" y="{sy}" width="24" height="12" rx="3" fill="{c}"/>'
                    for i, c in enumerate(sw))
    o.append(f'<g class="r" style="animation-delay:2s">{cells}</g>')
    return o


def security(t):
    w, h = W, 290
    o = [svg_open(w, h, "Security research summary"),
         panel(t, 0, 0, w, h, title="security-research", glow_x=0.95, glow_y=1.0)]
    lines = [
        (0.3, f'<tspan fill="{t["acc_text"]}">$ </tspan>disclosures --summary', t["text"]),
        (1.0, f'<tspan fill="{t["muted"]}">&gt; </tspan>10+ apps reported', t["acc_text"]),
        (1.7, f'<tspan fill="{t["muted"]}">&gt; </tspan>exposed customer PII · refund abuse on any order · e-bike unlock without access', t["text"]),
        (2.4, f'<tspan fill="{t["muted"]}">&gt; </tspan>status: disclosed privately · fixed · bounties awarded', t["acc_text"]),
    ]
    y0 = HEADER + 46
    for i, (d, body, fill) in enumerate(lines):
        o.append(f'<g class="r" style="animation-delay:{d}s"><text class="m" x="{PAD}" y="{y0 + i * 40}" '
                 f'font-size="17" fill="{fill}">{body}</text></g>')
    y = y0 + 4 * 40
    o.append(f'<g class="r" style="animation-delay:3.2s"><text class="m" x="{PAD}" y="{y}" font-size="17" '
             f'fill="{t["acc_text"]}">$ </text><rect class="k" x="{PAD + 22}" y="{y - 15}" width="10" '
             f'height="19" rx="1" fill="{t["acc"]}"/></g>')
    return o


CARDS = {
    "xmobility": dict(idx="01", kind="product", name="XMobility", url="xmobility.ai",
                      desc=["AI suite for global mobility, visa to payroll:",
                            "Immigration, EOR, HRMS and Payroll on one record."],
                      pills=["Live with paying customers", "MVP in 30 days"]),
    "crawlfox": dict(idx="02", kind="product", name="Crawlfox", url="crawlfox.io",
                     desc=["Web scraping product with real users.",
                           "Run end to end as Product Manager @ Automote.io."],
                     pills=["Shipped in 3 months", "90%+ success rate"]),
}


def card(t, c):
    w, h = 560, 300
    o = [svg_open(w, h, c["name"]), panel(t, 0, 0, w, h, glow_x=1.0, glow_y=0.0)]
    o.append(eyebrow(t, 36, 56, f'{c["idx"]} / {c["kind"]}'))
    # corner arrow
    o.append(f'<rect x="{w - 76}" y="32" width="40" height="40" rx="{R_IN}" fill="none" stroke="{t["border"]}"/>'
             f'<path d="M{w - 62} 58 L{w - 50} 46 M{w - 59} 46 H{w - 50} V55" fill="none" '
             f'stroke="{t["acc"]}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>')
    o.append(f'<text class="s" x="34" y="116" font-size="36" font-weight="700" letter-spacing="-.5" '
             f'fill="{t["text"]}">{esc(c["name"])}</text>')
    o.append(f'<text class="m" x="36" y="144" font-size="15" fill="{t["acc_text"]}">{esc(c["url"])}</text>')
    for i, line in enumerate(c["desc"]):
        o.append(f'<text class="s" x="36" y="{186 + i * 25}" font-size="17" fill="{t["muted"]}">{esc(line)}</text>')
    x = 36
    for p in c["pills"]:
        pw, s = pill(t, x, 240, p)
        o.append(s)
        x += pw + 10
    return o


def divider(t):
    w, h = 900, 12
    return ['<svg xmlns="http://www.w3.org/2000/svg" width="900" height="12" viewBox="0 0 900 12">'
            '<defs><linearGradient id="g" x1="0" x2="1">'
            f'<stop offset="0" stop-color="{t["border"]}" stop-opacity="0"/>'
            f'<stop offset=".5" stop-color="{t["acc"]}" stop-opacity=".8"/>'
            f'<stop offset="1" stop-color="{t["border"]}" stop-opacity="0"/></linearGradient></defs>'
            f'<rect x="0" y="5.5" width="{w}" height="1" fill="url(#g)"/>'
            f'<rect x="444" y="2" width="8" height="8" rx="2" transform="rotate(45 448 6)" '
            f'fill="{t["bg"]}" stroke="{t["acc"]}" stroke-width="1.5"/>']


ICON_RE = re.compile(r'<svg xmlns="http://www.w3.org/2000/svg" width="256" height="256".*?</svg>', re.S)


def skills(t, icons):
    n = len(icons)
    size, gap = 56, 14
    inner = n * size + (n - 1) * gap
    w = W
    h = HEADER + 40 + size + 36
    o = [svg_open(w, h, "Toolbox"), panel(t, 0, 0, w, h, title="toolbox", glow_x=0.5, glow_y=1.2)]
    x0 = (w - inner) / 2
    for i, ic in enumerate(icons):
        x = x0 + i * (size + gap)
        body = ic.replace('width="256" height="256"', f'x="{x:.1f}" y="{HEADER + 38}" width="{size}" height="{size}"', 1)
        o.append(f'<g class="r" style="animation-delay:{0.1 + i * 0.06:.2f}s">{body}</g>')
    return o


def main():
    os.makedirs(A, exist_ok=True)
    for name, t in THEMES.items():
        write(f"{A}/banner-green-{name}.svg", banner(t))
        write(f"{A}/about-{name}.svg", about(t))
        write(f"{A}/security-{name}.svg", security(t))
        for k, c in CARDS.items():
            write(f"{A}/card-{k}-{name}.svg", card(t, c))
        write(f"{A}/divider-{name}.svg", divider(t))
        src = f"{A}/skills-src-{name}.svg"
        icons = ICON_RE.findall(open(src).read())
        assert len(icons) == 13, (src, len(icons))
        write(f"{A}/skills-{name}.svg", skills(t, icons))


if __name__ == "__main__":
    main()
