#!/usr/bin/env python3
"""
Firehose collector for the multi-perspective news product.

Reads the Firehose SSE stream for the Global News tap, filters by quality,
stores matches in a local store for the downstream clustering + translation stage.

Run modes:
  once    — connect, collect for N seconds (default 60), save, exit (for cron)
  daemon  — connect and collect continuously (for systemd), restarting on errors
"""
import json
import os
import sys
import time
import urllib.request
import urllib.error
import datetime

# --- config ---
FIREHOSE_TAP_TOKEN = os.environ.get("FIREHOSE_TAP_TOKEN", "fh_auY3U00vF5bOfKKgjk88hahqYAao1R85pvSEssPM")
STREAM_URL = "https://api.firehose.com/v1/stream"
DATA_DIR = os.path.expanduser("~/multiperspective-news/data")
MIN_DR = 50           # minimum domain rating (quality floor, 0-100 scale)
ALLOWED_CATS = []      # empty = no category filter (news rule already filters)
EXCLUDE_TYPES = ["/Listing", "/Listing/Location", "/Listing/Business"]
CLICKBAIT = ["which is a better buy", "better buy?", "ai stock analysis", "stock analysis",
             "top 10", "top 5", "best rated", "vs ", "versus ", "listicle"]
MIN_TITLE_LEN = 12
# ---

def now_iso():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

def collect(seconds=60):
    os.makedirs(DATA_DIR, exist_ok=True)
    out_path = os.path.join(DATA_DIR, "matches.jsonl")
    req = urllib.request.Request(STREAM_URL, headers={
        "Authorization": f"Bearer {FIREHOSE_TAP_TOKEN}",
        "Accept": "text/event-stream",
    })
    count = 0
    filtered = 0
    start = time.time()

    try:
        with urllib.request.urlopen(req, timeout=seconds + 30) as resp:
            buf = b""
            while time.time() - start < seconds:
                chunk = resp.read(4096)
                if not chunk:
                    break
                buf += chunk
                while b"\n\n" in buf:
                    raw_event, buf = buf.split(b"\n\n", 1)
                    data_lines = [l[6:] for l in raw_event.split(b"\n") if l.startswith(b"data:")]
                    if not data_lines:
                        continue
                    data = json.loads(data_lines[0])
                    if "document" not in data:
                        continue
                    doc = data["document"]
                    # quality filter
                    dr = doc.get("domain_rating") or 0
                    types = doc.get("page_types") or []
                    title = (doc.get("title") or "").strip()
                    if dr < MIN_DR:
                        filtered += 1
                        continue
                    if any(t in EXCLUDE_TYPES for t in types):
                        filtered += 1
                        continue
                    if len(title) < MIN_TITLE_LEN:
                        filtered += 1
                        continue
                    tl = title.lower()
                    if any(cb in tl for cb in CLICKBAIT):
                        filtered += 1
                        continue
                    record = {
                        "url": doc.get("url"),
                        "title": title,
                        "language": doc.get("language"),
                        "publish_time": doc.get("publish_time"),
                        "domain_rating": dr,
                        "page_categories": doc.get("page_categories") or [],
                        "matched_at": data.get("matched_at"),
                        "collected_at": now_iso(),
                    }
                    with open(out_path, "a", encoding="utf-8") as f:
                        f.write(json.dumps(record, ensure_ascii=False) + "\n")
                    count += 1
    except urllib.error.HTTPError as e:
        print(f"collect error: HTTP {e.code} {e.reason}")
        return count, filtered
    except Exception as e:
        print(f"collect error: {e}")
        return count, filtered

    return count, filtered

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "once"
    secs = int(sys.argv[2]) if len(sys.argv) > 2 else 60
    if mode == "once":
        c, f = collect(secs)
        print(f"collected={c} filtered={f} sample-file={DATA_DIR}/matches.jsonl")
    else:
        # daemon: loop forever (systemd Restart handles crashes)
        while True:
            try:
                c, f = collect(120)
                print(f"{now_iso()} collected={c} filtered={f}")
            except Exception as e:
                print(f"{now_iso()} daemon error: {e}")
            time.sleep(5)