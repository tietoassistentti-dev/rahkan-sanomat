#!/usr/bin/env python3
from deep_translator import GoogleTranslator
import json
import os
import time

def translate_text(text, target="fi"):
    try:
        return GoogleTranslator(source="en", target=target).translate(text) or text
    except Exception:
        return text

def main():
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sp = os.path.join(BASE_DIR, "data", "stories.json")
    fi_path = os.path.join(BASE_DIR, "data", "stories_fi.json")
    if os.path.exists(sp):
        stories = json.load(open(sp, encoding="utf-8"))
        for s in stories:
            en_title = s.get("headline", "")
            s["headline_fi"] = translate_text(en_title, "fi")
            time.sleep(0.05)
        json.dump(stories, open(fi_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        print("Successfully generated translated stories_fi.json")

if __name__ == "__main__":
    main()
