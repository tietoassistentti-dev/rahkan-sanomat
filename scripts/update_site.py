import json, os

data = os.path.expanduser("~/multiperspective-news/data/stories.json")
with open(data, "r", encoding="utf-8") as f:
    stories = json.load(f)

html = "<h1>Rahkan Sanomat</h1>"
for s in stories[:20]:
    h = s.get('headline', '')
    html += f"<div>{h}</div>"

with open(os.path.expanduser("~/multiperspective-news/site/index.html"), "w", encoding="utf-8") as f:
    f.write(html)
print("Updated successfully")
