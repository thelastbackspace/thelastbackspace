#!/usr/bin/env bash
# Rebuild the merged-PR table between the OSS markers in README.md.
set -euo pipefail
user="thelastbackspace"
rows=$(gh api -X GET search/issues \
  -f q="author:$user is:pr is:merged -user:$user -org:Xmobility-ai" \
  -f sort=updated -f per_page=20 \
  --jq '.items[] | "| <img src=\"https://github.com/\(.repository_url|split("/")[-2]).png\" width=\"16\"/> **[\(.repository_url|split("/")[-2:]|join("/"))](\(.html_url))** | \(.title|gsub("\\|";"/")) |"')
[ -z "$rows" ] && exit 0
table=$(printf '| Project | Pull request |\n|---|---|\n%s\n' "$rows")
python3 - "$table" <<'PY'
import re, sys
p = "README.md"
s = open(p).read()
new = "<!-- OSS:START -->\n" + sys.argv[1] + "\n<!-- OSS:END -->"
s = re.sub(r"<!-- OSS:START -->.*?<!-- OSS:END -->", new, s, flags=re.S)
open(p, "w").write(s)
PY
