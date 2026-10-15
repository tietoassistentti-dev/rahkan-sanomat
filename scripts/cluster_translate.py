#!/usr/bin/env python3
import feedparser
import json
import os
import time
from email.utils import parsedate_to_datetime
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "data"
MATCHES = DATA_DIR / "rss_matches.jsonl"

def parse_pub_dt(p_str):
    if not p_str:
        return datetime.min
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S"):
        try:
            return datetime.strptime(p_str, fmt)
        except:
            pass
    try:
        dt = parsedate_to_datetime(p_str)
        return dt.replace(tzinfo=None)
    except:
        return datetime.min

def format_pub(dt):
    if dt == datetime.min:
        return "Recent"
    return dt.strftime("%Y-%m-%d %H:%M")

def story_key(story):
    return (story.get("link", "#"), story.get("headline", ""))

def load_previous_translations(path):
    try:
        with open(path, encoding="utf-8") as f:
            previous_stories = json.load(f)
    except FileNotFoundError:
        return {}
    except (OSError, json.JSONDecodeError) as e:
        print(f"Could not load previous Finnish translations: {e}")
        return {}

    translations = {}
    for story in previous_stories:
        headline = story.get("headline", "")
        headline_fi = story.get("headline_fi", "")
        if headline_fi and headline_fi != headline:
            translations[story_key(story)] = headline_fi
    return translations

def translate_stories(stories, previous_translations, translator):
    stories_fi = []
    translation_attempts = 0

    for story in stories:
        story_fi = story.copy()
        previous_translation = previous_translations.get(story_key(story))
        if previous_translation:
            story_fi["headline_fi"] = previous_translation
        elif translation_attempts < 20:
            translation_attempts += 1
            try:
                result = translator.translate(story["headline"], "fi")
                if result and result.result:
                    story_fi["headline_fi"] = result.result
                else:
                    story_fi["headline_fi"] = story["headline"]
            except Exception as e:
                print(f"Translation failed: {e}")
                story_fi["headline_fi"] = story["headline"]
            time.sleep(1.0)
        else:
            story_fi["headline_fi"] = story["headline"]

        stories_fi.append(story_fi)

    return stories_fi

def main():
    rows = []
    if os.path.exists(MATCHES):
        with open(MATCHES, encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    rows.append(json.loads(line))
    
    rows.sort(key=lambda x: parse_pub_dt(x.get("published", "")), reverse=True)
    
    stories = []
    for r in rows:
        title = r.get("title", "")
        pub_raw = r.get("published", "")
        dt = parse_pub_dt(pub_raw)
        pub_formatted = format_pub(dt)
        
        stories.append({
            "headline": title,
            "headline_fi": title,
            "link": r.get("link", "#"),
            "source": r.get("source", "Unknown"),
            "pub": pub_formatted,
            "_dt": dt.isoformat()
        })
    
    from translatepy import Translator
    translator = Translator()

    previous_translations = load_previous_translations(DATA_DIR / "stories_fi.json")
    stories_fi = translate_stories(stories, previous_translations, translator)

    for s_fi in stories_fi:
        s_fi.pop("_dt", None)

    for s in stories:
        s.pop("_dt", None)

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(DATA_DIR / "stories.json", "w", encoding="utf-8") as f:
        json.dump(stories, f, ensure_ascii=False, indent=2)

    with open(DATA_DIR / "stories_fi.json", "w", encoding="utf-8") as f:
        json.dump(stories_fi, f, ensure_ascii=False, indent=2)
        
    print("Pipeline completed successfully.")

if __name__ == "__main__":
    main()
