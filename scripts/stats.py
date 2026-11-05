#!/usr/bin/env python3
"""Render self-hosted stats cards (light and dark) from the GitHub GraphQL API."""
import json, os, subprocess

USER = "thelastbackspace"
Q = """query($u:String!){user(login:$u){
  contributionsCollection{contributionCalendar{totalContributions}}
  repositories(ownerAffiliations:OWNER,isFork:false,privacy:PUBLIC,first:100,orderBy:{field:STARGAZERS,direction:DESC}){totalCount nodes{stargazerCount}}
  pullRequests{totalCount}
}}"""

def gh(args):
    return json.loads(subprocess.check_output(["gh", "api"] + args))

d = gh(["graphql", "-f", f"query={Q}", "-f", f"u={USER}"])["data"]["user"]
stars = sum(n["stargazerCount"] for n in d["repositories"]["nodes"])
merged = gh(["-X", "GET", "search/issues", "-f",
             f"q=author:{USER} is:pr is:merged -user:{USER} -org:Xmobility-ai"])["total_count"]
items = [
    ("Contributions (1y)", d["contributionsCollection"]["contributionCalendar"]["totalContributions"]),
    ("Stars earned", stars),
    ("Original repos", d["repositories"]["totalCount"]),
    ("Pull requests", d["pullRequests"]["totalCount"]),
    ("Merged in other projects", merged),
]

themes = {
    "dark": dict(bg="#0d1117", border="#1f2a24", label="#8b949e", value="#e6edf3", acc="#3fb950"),
    "light": dict(bg="#ffffff", border="#d0e8d8", label="#57606a", value="#0d1117", acc="#2ea043"),
}
w, h = 1200, 140
col = w / len(items)
os.makedirs("assets", exist_ok=True)
for name, t in themes.items():
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">',
             f'<rect x="1" y="1" width="{w-2}" height="{h-2}" rx="14" fill="{t["bg"]}" stroke="{t["border"]}" stroke-width="2"/>']
    for i, (label, value) in enumerate(items):
        cx = col * i + col / 2
        parts.append(f'<text x="{cx}" y="72" text-anchor="middle" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="40" font-weight="700" fill="{t["value"]}">{value:,}</text>')
        parts.append(f'<text x="{cx}" y="104" text-anchor="middle" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="16" fill="{t["label"]}">{label}</text>')
        if i:
            parts.append(f'<line x1="{col*i}" y1="36" x2="{col*i}" y2="{h-36}" stroke="{t["border"]}" stroke-width="2"/>')
    parts.append(f'<rect x="{w/2-40}" y="{h-14}" width="80" height="4" rx="2" fill="{t["acc"]}"/></svg>')
    open(f"assets/stats-{name}.svg", "w").write("\n".join(parts))
print(items)
