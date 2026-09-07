#!/usr/bin/env python3
import json
import os
import re
import datetime

DATA_DIR = os.path.expanduser("~/multiperspective-news/data")
MATCHES = os.path.join(DATA_DIR, "rss_matches.jsonl")
OUT = os.path.join(DATA_DIR, "stories.json")

STOPWORDS = set("a an and the or of to in for on with at by from as is are was were be been".split())

def tokenize(title):
    return [w for w in re.findall(r"[a-z0-9]{3,}", title.lower()) if w not in STOPWORDS]

def main():
    if not os.path.exists(MATCHES):
        return
    matches = []
    with open(MATCHES, encoding="utf-8") as f:
        for l in f:
            if l.strip():
                try: matches.append(json.loads(l))
                except: pass

    clusters = []
    for m in matches:
        tokens = set(tokenize(m.get("title", "")))
        if not tokens: continue
        matched = False
        for c in clusters:
            c_tokens = set(tokenize(c[0].get("title", "")))
            if c_tokens and len(tokens & c_tokens) / len(tokens | c_tokens) >= 0.45:
                c.append(m)
                matched = True
                break
        if not matched:
            clusters.append([m])

    out = []
    for ms in clusters:
        langs = list(set(m.get("lang") for m in ms if m.get("lang")))
        domains = list(set(m.get("domain") for m in ms if m.get("domain")))
        pub_dates = []
        for m in ms:
            try:
                # Handle common RSS date formats
                pub_dates.append(datetime.datetime.strptime(m.get("pub", ""), "%a, %d %b %Y %H:%M:%S %Z"))
            except:
                pass
        
        # Use a real timestamp
        earliest_pub = min(pub_dates) if pub_dates else datetime.datetime.now()
        
        out.append({
            "headline": ms[0].get("title", ""),
            "languages": langs,
            "domains": domains,
            "perspectives": len(ms),
            "pub": earliest_pub.strftime("%Y-%m-%d %H:%M"),
            "matches": ms
        })

    out.sort(key=lambda x: x["pub"], reverse=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"Generated {len(out)} stories with formatted pub dates")

if __name__ == "__main__":
    main()
