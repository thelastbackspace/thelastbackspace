"""Shared design system for every SVG in the profile README.

One set of tokens and one panel primitive, so the banner, terminals, cards,
stats and toolbox all share radii, borders, spacing, type and glow.
System fonts only, CSS animation only, no external references.
"""
from html import escape

THEMES = {
    "dark": dict(
        bg="#0d1117", top="#161b22", border="#30363d", text="#e6edf3",
        muted="#8b949e", faint="#6e7681", acc="#3fb950", acc_text="#3fb950",
        acc_soft="#3fb950", glow=0.16, dots="#ffffff", dots_op=0.045,
        hl="#ffffff", hl_op=0.10, pill="#12261a",
    ),
    "light": dict(
        bg="#ffffff", top="#f6f8fa", border="#d0d7de", text="#1f2328",
        muted="#59636e", faint="#818b98", acc="#2ea043", acc_text="#1a7f37",
        acc_soft="#2ea043", glow=0.10, dots="#1f2328", dots_op=0.06,
        hl="#ffffff", hl_op=0.0, pill="#eaf6ec",
    ),
}

R = 16          # outer radius
R_IN = 10       # inner radius (pills, tiles inside panels)
HEADER = 44     # terminal title bar height
PAD = 40        # horizontal content padding
W = 1000        # standard full-width asset

SANS = "ui-sans-serif,-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif"
MONO = "ui-monospace,SFMono-Regular,'SF Mono',Menlo,Consolas,'Liberation Mono',monospace"

BASE_CSS = (
    f".s{{font-family:{SANS}}}.m{{font-family:{MONO}}}"
    ".r{animation:f .6s ease-out backwards}@keyframes f{from{opacity:0}}"
    ".k{animation:b 1s steps(1) infinite}@keyframes b{50%{opacity:0}}"
)


def esc(s):
    return escape(str(s), quote=True)


def svg_open(w, h, label, css=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
            f'viewBox="0 0 {w} {h}" role="img" aria-label="{esc(label)}">'
            f"<style>{BASE_CSS}{css}</style>")


def defs(t, uid="p", glow_x=0.88, glow_y=0.0):
    return (
        "<defs>"
        f'<linearGradient id="{uid}s" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{t["top"]}"/><stop offset="1" stop-color="{t["bg"]}"/></linearGradient>'
        f'<radialGradient id="{uid}g" cx="{glow_x}" cy="{glow_y}" r="0.75">'
        f'<stop offset="0" stop-color="{t["acc"]}" stop-opacity="{t["glow"]}"/>'
        f'<stop offset="1" stop-color="{t["acc"]}" stop-opacity="0"/></radialGradient>'
        f'<pattern id="{uid}d" width="20" height="20" patternUnits="userSpaceOnUse">'
        f'<circle cx="2" cy="2" r="1" fill="{t["dots"]}" fill-opacity="{t["dots_op"]}"/></pattern>'
        f'<linearGradient id="{uid}h" x1="0" x2="1">'
        f'<stop offset="0" stop-color="{t["hl"]}" stop-opacity="0"/>'
        f'<stop offset=".5" stop-color="{t["hl"]}" stop-opacity="{t["hl_op"]}"/>'
        f'<stop offset="1" stop-color="{t["hl"]}" stop-opacity="0"/></linearGradient>'
        "</defs>"
    )


def panel(t, x, y, w, h, uid="p", title=None, dots=True, glow=True, glow_x=0.88, glow_y=0.0):
    """Rounded glass panel: vertical surface gradient, dot grid, accent glow,
    hairline top highlight and an optional terminal title bar."""
    o = [defs(t, uid, glow_x, glow_y)]
    box = f'x="{x + .5}" y="{y + .5}" width="{w - 1}" height="{h - 1}" rx="{R}"'
    o.append(f'<rect {box} fill="url(#{uid}s)"/>')
    if dots:
        o.append(f'<rect {box} fill="url(#{uid}d)"/>')
    if glow:
        o.append(f'<rect {box} fill="url(#{uid}g)"/>')
    o.append(f'<rect {box} fill="none" stroke="{t["border"]}"/>')
    o.append(f'<rect x="{x + R}" y="{y + 1}" width="{w - 2 * R}" height="1" fill="url(#{uid}h)"/>')
    if title is not None:
        cy = y + HEADER / 2
        for i, c in enumerate(("#ff5f57", "#febc2e", "#28c840")):
            o.append(f'<circle cx="{x + 24 + i * 20}" cy="{cy}" r="6" fill="{c}"/>')
        o.append(f'<text class="m" x="{x + w / 2}" y="{cy + 5}" text-anchor="middle" '
                 f'font-size="14" fill="{t["muted"]}">{esc(title)}</text>')
        o.append(f'<rect x="{x + 1}" y="{y + HEADER}" width="{w - 2}" height="1" fill="{t["border"]}"/>')
    return "".join(o)


def pill(t, x, y, label, size=14):
    w = len(label) * size * 0.6 + 28
    return (w, f'<rect x="{x}" y="{y}" width="{w:.1f}" height="30" rx="15" fill="{t["pill"]}" '
               f'stroke="{t["acc"]}" stroke-opacity=".45"/>'
               f'<text class="m" x="{x + w / 2:.1f}" y="{y + 20}" text-anchor="middle" '
               f'font-size="{size}" fill="{t["acc_text"]}">{esc(label)}</text>')


def eyebrow(t, x, y, label):
    return (f'<rect x="{x}" y="{y - 12}" width="10" height="10" rx="2" fill="{t["acc"]}"/>'
            f'<text class="m" x="{x + 20}" y="{y - 2}" font-size="16" letter-spacing="1.5" '
            f'fill="{t["acc_text"]}">{esc(label.upper())}</text>')


def write(path, parts):
    with open(path, "w") as fh:
        fh.write("".join(parts) + "</svg>\n")
