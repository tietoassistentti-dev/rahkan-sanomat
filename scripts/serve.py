#!/usr/bin/env python3
import http.server
import json
import os
import socketserver
import base64

SITE = os.path.join(os.path.dirname(__file__), "..", "site")
DATA_EN = os.path.join(os.path.dirname(__file__), "..", "data", "stories.json")
DATA_FI = os.path.join(os.path.dirname(__file__), "..", "data", "stories_fi.json")
PORT = 5000

# Credentials for login wall
USERNAME = "Vitusti"
PASSWORD = "Rahkaa"

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=SITE, **kwargs)

    def do_HEAD(self):
        self.check_auth()

    def do_GET(self):
        if not self.check_auth():
            return
        if self.path.startswith("/api/stories_fi"):
            self.serve_json(DATA_FI)
            return
        if self.path.startswith("/api/stories"):
            self.serve_json(DATA_EN)
            return
        super().do_GET()

    def check_auth(self):
        auth_header = self.headers.get("Authorization")
        if auth_header and auth_header.startswith("Basic "):
            try:
                encoded = auth_header.split(" ")[1]
                decoded = base64.b64decode(encoded).decode("utf-8")
                u, p = decoded.split(":", 1)
                if u == USERNAME and p == PASSWORD:
                    return True
            except Exception:
                pass
        
        self.send_response(401)
        self.send_header("WWW-Authenticate", 'Basic realm="WorldWire Restricted Access"')
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"<h1>401 Unauthorized</h1><p>Please log in to access WorldWire.</p>")
        return False

    def serve_json(self, path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                stories = json.load(f)
            body = json.dumps(stories, ensure_ascii=False).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        except Exception as e:
            msg = json.dumps({"error": str(e)}).encode()
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(msg)

    def log_message(self, fmt, *args):
        pass

class TS(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True
    allow_reuse_address = True

if __name__ == "__main__":
    print(f"WorldWire with Login Wall on http://0.0.0.0:{PORT}/")
    TS(("0.0.0.0", PORT), Handler).serve_forever()
