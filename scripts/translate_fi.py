#!/usr/bin/env python3
from translate import Translator
import json
import os
import time

def translate_local(text, target="fi"):
    try:
        translator = Translator(to_lang=target)
        return translator.translate(text)
    except Exception as e:
        print(f"Translation error: {e}")
        return text

def main():
    sp = os.path.expanduser("~/multiperspective-news/data/stories.json")
    fi_path = os.path.expanduser("~/multiperspective-news/data/stories_fi.json")
    if os.path.exists(sp):
        stories = json.load(open(sp, encoding="utf-8"))
        for s in stories:
            s["headline_fi"] = translate_local(s.get("headline", ""), "fi")
            time.sleep(0.1)
        json.dump(stories, open(fi_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        print("Successfully generated stories_fi.json")

if __name__ == "__main__":
    main()
