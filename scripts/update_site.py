import json, os, datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data = os.path.join(BASE_DIR, "data", "stories.json")
with open(data, "r", encoding="utf-8") as f:
    stories = json.load(f)

# Sort by publication date descending
stories.sort(key=lambda x: x.get('pub', ''), reverse=True)

html = """<!DOCTYPE html>
<html lang="fi">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Rahkan Sanomat</title>
<meta http-equiv="cache-control" content="no-cache">
<meta http-equiv="expires" content="0">
<meta http-equiv="pragma" content="no-cache">
<style>
:root { --bg:#0d1117; --panel:#161b22; --border:#30363d; --text:#e6edf3; --dim:#8b949e; --accent:#58a6ff; }
* { box-sizing:border-box; margin:0; padding:0; }
body { background:var(--bg); color:var(--text); font-family:monospace; padding: 20px; }
.wrap { max-width:860px; margin:0 auto; }
.story { background:var(--panel); border:1px solid var(--border); padding:16px; margin-bottom:12px; border-radius:8px; }
.meta { color:var(--dim); font-size:12px; margin-top:5px; }
</style>
</head>
<body>
<div class="wrap">
<h1>Rahkan <span>Sanomat</span></h1>
"""
for s in stories[:30]:
    h = s.get('headline', '')
    p = s.get('pub', '')
    src = s.get('source', '')
    html += f'<div class="story"><strong>{h}</strong><div class="meta">{src} · {p}</div></div>'
html += "</div></body></html>"

output_dir = os.path.join(BASE_DIR, "site")
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, "index.html")
with open(output_path, "w", encoding="utf-8") as f:
    f.write(html)
print("Updated site/index.html with sorted stories")
