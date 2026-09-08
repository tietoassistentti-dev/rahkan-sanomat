import json, os, re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data_en = os.path.join(BASE_DIR, "data", "stories.json")
data_fi = os.path.join(BASE_DIR, "data", "stories_fi.json")
template_path = os.path.join(BASE_DIR, "index.html")

with open(data_en, "r", encoding="utf-8") as f:
    stories_en = json.load(f)
with open(data_fi, "r", encoding="utf-8") as f:
    stories_fi = json.load(f)
with open(template_path, "r", encoding="utf-8") as f:
    template = f.read()

# Sort descending by pub
stories_en.sort(key=lambda x: x.get("pub", ""), reverse=True)
stories_fi.sort(key=lambda x: x.get("pub", ""), reverse=True)

# Replace JS variables
new_template = re.sub(r'const STORIES_EN = \[.*?\];', f'const STORIES_EN = {json.dumps(stories_en, ensure_ascii=False)};', template, flags=re.DOTALL)
new_template = re.sub(r'const STORIES_FI = \[.*?\];', f'const STORIES_FI = {json.dumps(stories_fi, ensure_ascii=False)};', new_template, flags=re.DOTALL)

output_path = os.path.join(BASE_DIR, "site", "index.html")
os.makedirs(os.path.dirname(output_path), exist_ok=True)
with open(output_path, "w", encoding="utf-8") as f:
    f.write(new_template)
print("Successfully updated site/index.html with template and fresh data")
