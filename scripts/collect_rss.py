#!/usr/bin/env python3
import feedparser
import json
import os
import time

FEEDS = {
    "Deutsche Welle": "https://rss.dw.com/rdf/rss-en-all",
    "France 24": "https://www.france24.com/en/rss",
    "Euronews": "https://www.euronews.com/rss?format=rss",
    "El País (EN)": "https://elpais.com/eps/rss/",
    "ANSA English": "https://www.ansa.it/english/ansanews_rss.xml"
}

KEYWORDS = ['riot', 'protest', 'eu commission', 'age verification', 'politics', 'political', 'strike', 'regulation', 'digital', 'police', 'demonstration', 'parliament', 'law', 'court', 'election', 'migrant', 'immigration', 'asylum', 'refugee', 'maahanmuutto', 'turvapaikka', 'trump', 'tariff', 'war', 'russia', 'ukraine', 'israel', 'gaza', 'energy', 'economy']

DATA_DIR = os.path.expanduser("~/multiperspective-news/data")
OUT_MATCHES = os.path.join(DATA_DIR, "rss_matches.jsonl")

def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    matches = []
    
    for source, url in FEEDS.items():
        try:
            d = feedparser.parse(url)
            for entry in d.entries:
                title = entry.get("title", "")
                summary = entry.get("summary", "")
                link = entry.get("link", "#")
                
                pub = entry.get("published", entry.get("updated", ""))
                if not pub and hasattr(entry, "published_parsed") and entry.published_parsed:
                    pub = time.strftime("%Y-%m-%d %H:%M:%S", entry.published_parsed)
                
                combined_text = (title + " " + summary).lower()
                if any(kw in combined_text for kw in KEYWORDS):
                    matches.append({
                        "title": title,
                        "summary": summary,
                        "link": link,
                        "source": source,
                        "published": pub or "Recent"
                    })
        except Exception as e:
            print(f"Error parsing {source}: {e}")
            
    with open(OUT_MATCHES, "w", encoding="utf-8") as f:
        for m in matches:
            f.write(json.dumps(m, ensure_ascii=False) + "\n")
            
    print(f"Collected {len(matches)} matching articles.")

if __name__ == "__main__":
    main()
