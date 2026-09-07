#!/usr/bin/env python3
"""
RSS collector — focused specifically on EU politics, protests, riots, digital regulation, age verification.
"""
import json
import os
import urllib.request
import xml.etree.ElementTree as ET

DATA_DIR = os.path.expanduser("~/multiperspective-news/data")
OUT = os.path.join(DATA_DIR, "rss_matches.jsonl")
UA = "Mozilla/5.0 (X11; Linux x86_64) MultiperspectiveNews/0.1"

FEEDS = [
    ("https://feeds.bbci.co.uk/news/world/europe/rss.xml", "en", "bbc.com"),
    ("https://www.france24.com/en/europe/rss", "en", "france24.com"),
    ("https://rss.dw.com/rdf/rss-de-all", "de", "dw.com"),
    ("https://www.lemonde.fr/rss/une.xml", "fr", "lemonde.fr"),
    ("https://elpais.com/rss/elpais/portada.xml", "es", "elpais.com"),
]

KEYWORDS = ["riot", "protest", "commission", "age", "verification", "politic", "eu", "strike", "regulation", "digital", "police", "demonstrat", "parliament", "law", "court", "elect", "migrant", "border"]

def fetch(url, timeout=20):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()

def parse_rss(data):
    try:
        root = ET.fromstring(data)
    except Exception:
        return []
    items = []
    channel = root.find("channel")
    entries = channel.findall("item") if channel is not None else []
    for it in entries:
        title_el = it.find("title")
        link_el = it.find("link")
        pub_el = it.find("pubDate")
        title = title_el.text if title_el is not None and title_el.text else ""
        link = link_el.text if link_el is not None and link_el.text else ""
        pub = pub_el.text if pub_el is not None and pub_el.text else ""
        if title and link:
            t_lower = title.lower()
            if any(k in t_lower for k in KEYWORDS):
                items.append({"title": title.strip(), "url": link.strip(), "pub": pub.strip()})
    return items

def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    existing = set()
    if os.path.exists(OUT):
        with open(OUT, encoding="utf-8") as f:
            for l in f:
                if l.strip():
                    try:
                        existing.add(json.loads(l)["url"])
                    except Exception:
                        pass
    total_new = 0
    for url, lang, domain in FEEDS:
        try:
            data = fetch(url)
            items = parse_rss(data)
            with open(OUT, "a", encoding="utf-8") as f:
                for item in items:
                    if item["url"] not in existing:
                        item["lang"] = lang
                        item["domain"] = domain
                        f.write(json.dumps(item) + "\n")
                        existing.add(item["url"])
                        total_new += 1
        except Exception as e:
            print(f"Error fetching {url}: {e}")
    print(f"Added {total_new} filtered European items")

if __name__ == "__main__":
    main()
