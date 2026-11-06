#!/usr/bin/env python3
"""Render the self-hosted stats bento and the "recently merged" terminal
(light and dark) from the GitHub API, using the shared design system."""
import base64, json, os, subprocess, sys, textwrap, urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from design import THEMES, W, PAD, HEADER, svg_open, panel, pill, esc, write

USER = "thelastbackspace"
SEARCH = f"author:{USER} is:pr is:merged -user:{USER} -org:Xmobility-ai"
Q = """query($u:String!){user(login:$u){
  contributionsCollection{contributionCalendar{totalContributions weeks{contributionDays{contributionCount}}}}
  repositories(ownerAffiliations:OWNER,isFork:false,privacy:PUBLIC,first:100,orderBy:{field:STARGAZERS,direction:DESC}){totalCount nodes{stargazerCount}}
  pullRequests{totalCount}
}}"""


def gh(args):
    return json.loads(subprocess.check_output(["gh", "api"] + args))


d = gh(["graphql", "-f", f"query={Q}", "-f", f"u={USER}"])["data"]["user"]
cal = d["contributionsCollection"]["contributionCalendar"]
weeks = [sum(x["contributionCount"] for x in wk["contributionDays"]) for wk in cal["weeks"]][-52:]
stars = sum(n["stargazerCount"] for n in d["repositories"]["nodes"])
search = gh(["-X", "GET", "search/issues", "-f", f"q={SEARCH}", "-f", "sort=updated", "-f", "per_page=20"])
merged = search["total_count"]
prs = sorted(search["items"], key=lambda i: i.get("closed_at") or "", reverse=True)[:12]

hero = ("Contributions (1y)", cal["totalContributions"])
items = [
    ("Stars earned", stars),
    ("Original repos", d["repositories"]["totalCount"]),
    ("Pull requests", d["pullRequests"]["totalCount"]),
    ("Merged in other projects", merged),
]


def tile(t, x, y, w, h, uid, label, value, gx=1.0):
    return (panel(t, x, y, w, h, uid=uid, dots=False, glow_x=gx, glow_y=0.0)
            + f'<text class="s" x="{x + 28}" y="{y + 62}" font-size="42" font-weight="700" '
              f'letter-spacing="-1" fill="{t["text"]}">{value:,}</text>'
            + f'<text class="s" x="{x + 28}" y="{y + 94}" font-size="17" fill="{t["muted"]}">{esc(label)}</text>')


def stats_svg(t):
    gap, h = 16, 268
    lw = 392
    rw = (W - lw - 2 * gap) / 2
    th = (h - gap) / 2
    o = [svg_open(W, h, "GitHub stats: " + "; ".join(f"{k} {v:,}" for k, v in [hero] + items))]
    # hero tile with weekly contribution bars
    o.append(panel(t, 0, 0, lw, h, uid="h", glow_x=0.0, glow_y=1.0))
    o.append(f'<text class="s" x="28" y="72" font-size="56" font-weight="700" letter-spacing="-1.5" '
             f'fill="{t["text"]}">{hero[1]:,}</text>')
    o.append(f'<text class="s" x="28" y="104" font-size="17" fill="{t["muted"]}">{hero[0]}</text>')
    top = max(weeks) or 1
    bw, bg_ = 5, 1.75
    bx, by, bh = 28, h - 32, 108
    for i, v in enumerate(weeks):
        hh = max(2, v / top * bh)
        o.append(f'<rect x="{bx + i * (bw + bg_):.2f}" y="{by - hh:.1f}" width="{bw}" height="{hh:.1f}" '
                 f'rx="1.5" fill="{t["acc"]}" fill-opacity="{0.35 + 0.65 * v / top:.2f}"/>')
    o.append(f'<rect x="{bx}" y="{by + 6}" width="{lw - 56}" height="1" fill="{t["border"]}"/>')
    for i, (label, value) in enumerate(items):
        x = lw + gap + (i % 2) * (rw + gap)
        y = (i // 2) * (th + gap)
        o.append(tile(t, x, y, rw, th, f"t{i}", label, value))
    return o


def merged_svg(t):
    row = 64
    top = HEADER + 44
    n = max(1, len(prs))
    h = top + 46 + n * row + 34
    o = [svg_open(W, h, "Recently merged pull requests: " + "; ".join(
        f'{"/".join(p["repository_url"].split("/")[-2:])}: {p["title"]}' for p in prs)),
         panel(t, 0, 0, W, h, title="open source · recently merged", glow_x=0.0, glow_y=1.0)]
    o.append(f'<g class="r" style="animation-delay:.2s"><text class="m" x="{PAD}" y="{top}" font-size="17" '
             f'fill="{t["text"]}"><tspan fill="{t["acc_text"]}">$ </tspan>gh search prs --author {USER} --merged'
             f'</text></g>')
    maxc = 80
    for i, p in enumerate(prs):
        y = top + 46 + i * row
        repo = "/".join(p["repository_url"].split("/")[-2:])
        title = p["title"] if len(p["title"]) <= maxc else p["title"][: maxc - 1].rstrip() + "…"
        date = (p.get("closed_at") or "")[:10]
        o.append(
            f'<g class="r" style="animation-delay:{0.7 + i * 0.35:.2f}s">'
            f'<circle cx="{PAD + 6}" cy="{y - 6}" r="5" fill="none" stroke="{t["acc"]}" stroke-width="2"/>'
            f'<text class="m" x="{PAD + 24}" y="{y}" font-size="17" font-weight="700" fill="{t["text"]}">'
            f'{esc(repo)}<tspan font-weight="400" fill="{t["muted"]}">  #{p["number"]}</tspan></text>'
            f'<text class="m" x="{W - PAD}" y="{y}" text-anchor="end" font-size="15" fill="{t["acc_text"]}">'
            f'merged {esc(date)}</text>'
            f'<text class="m" x="{PAD + 24}" y="{y + 26}" font-size="15" fill="{t["muted"]}">{esc(title)}</text></g>')
    if not prs:
        o.append(f'<text class="m" x="{PAD}" y="{top + 46}" font-size="17" fill="{t["muted"]}">&gt; nothing yet</text>')
    y = top + 46 + n * row + 4
    o.append(f'<g class="r" style="animation-delay:{0.9 + n * 0.35:.2f}s"><text class="m" x="{PAD}" y="{y}" '
             f'font-size="17" fill="{t["acc_text"]}">$ </text><rect class="k" x="{PAD + 22}" y="{y - 15}" '
             f'width="10" height="19" rx="1" fill="{t["acc"]}"/></g>')
    return o


def repo_info(p):
    owner, name = p["repository_url"].split("/")[-2:]
    r = gh([f"repos/{owner}/{name}"])
    try:
        with urllib.request.urlopen(f"https://github.com/{owner}.png?size=96", timeout=20) as f:
            img = "data:image/png;base64," + base64.b64encode(f.read()).decode()
    except Exception:
        img = None
    return dict(repo=f"{owner}/{name}", stars=r.get("stargazers_count", 0), img=img)


INFO = [repo_info(p) for p in prs]


def stars_fmt(n):
    return f"{n/1000:.1f}k".replace(".0k", "k") if n >= 1000 else str(n)


def contrib_svg(t):
    gap, ch, cols = 16, 190, 2
    cw = (W - 2 * PAD - gap) / cols
    top = HEADER + 28
    rows = max(1, (len(prs) + cols - 1) // cols)
    h = top + rows * ch + (rows - 1) * gap + 32
    o = [svg_open(W, h, "Merged open source contributions: " + "; ".join(
        f'{i["repo"]} #{p["number"]}: {p["title"]}' for p, i in zip(prs, INFO))),
         panel(t, 0, 0, W, h, title="open source · merged contributions", glow_x=0.0, glow_y=1.0)]
    for k, (p, info) in enumerate(zip(prs, INFO)):
        x = PAD + (k % cols) * (cw + gap)
        y = top + (k // cols) * (ch + gap)
        o.append(f'<g class="r" style="animation-delay:{0.2 + k * 0.25:.2f}s">')
        o.append(panel(t, x, y, cw, ch, uid=f"c{k}", dots=False, glow_x=1.0, glow_y=0.0))
        if info["img"]:
            o.append(f'<clipPath id="av{k}"><rect x="{x + 24}" y="{y + 24}" width="40" height="40" rx="10"/></clipPath>'
                     f'<rect x="{x + 24}" y="{y + 24}" width="40" height="40" rx="10" fill="{t["border"]}"/>'
                     f'<image href="{info["img"]}" x="{x + 24}" y="{y + 24}" width="40" height="40" clip-path="url(#av{k})"/>')
        o.append(f'<text class="s" x="{x + 78}" y="{y + 42}" font-size="18" font-weight="700" fill="{t["text"]}">{esc(info["repo"])}</text>')
        o.append(f'<text class="m" x="{x + 78}" y="{y + 62}" font-size="13" fill="{t["muted"]}">★ {stars_fmt(info["stars"])}  ·  #{p["number"]}</text>')
        lines = textwrap.wrap(p["title"], 46)[:2]
        if len(textwrap.wrap(p["title"], 46)) > 2:
            lines[1] = lines[1][:43].rstrip() + "…"
        for j, ln in enumerate(lines):
            o.append(f'<text class="s" x="{x + 24}" y="{y + 102 + j * 24}" font-size="16" fill="{t["muted"]}">{esc(ln)}</text>')
        o.append(pill(t, x + 24, y + ch - 46, "merged " + (p.get("closed_at") or "")[:10], size=13)[1])
        o.append('</g>')
    if not prs:
        o.append(f'<text class="m" x="{PAD}" y="{top + 30}" font-size="17" fill="{t["muted"]}">&gt; first merges on the way</text>')
    return o


os.makedirs("assets", exist_ok=True)
for name, t in THEMES.items():
    write(f"assets/stats-{name}.svg", stats_svg(t))
    write(f"assets/merged-{name}.svg", merged_svg(t))
    write(f"assets/contrib-{name}.svg", contrib_svg(t))
print([hero] + items, len(prs), "merged rows")


def pr_links():
    """Rewrite the PRLINKS marker block in README.md with real-text links to each merged PR."""
    import re
    links = " · ".join(f'<a href="{p["html_url"]}">{esc(i["repo"])}#{p["number"]}</a>'
                       for p, i in zip(prs, INFO))
    block = f"<!-- PRLINKS:START -->\n<sub>{links}</sub>\n<!-- PRLINKS:END -->"
    src = open("README.md").read()
    new = re.sub(r"<!-- PRLINKS:START -->.*?<!-- PRLINKS:END -->", lambda m: block, src, flags=re.S)
    if new != src:
        open("README.md", "w").write(new)


pr_links()


# CACHE-BUST: give the daily-generated images a dated version so GitHub's image cache refreshes.
import datetime, re as _re
_v = datetime.date.today().strftime("%Y%m%d")
_p = "README.md"
_s = open(_p).read()
_s = _re.sub(r"(assets/(?:stats|contrib)-(?:dark|light)\.svg)\?v=\w+", r"\1?v=" + _v, _s)
open(_p, "w").write(_s)
