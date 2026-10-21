#!/usr/bin/env python3
"""Servidor do portfólio: serve o site e a API do painel /admin.html.
Uso: python3 server.py   (senha em admin_password.txt, criada na 1a execução)"""
import hmac, json, os, re, secrets, sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)
PASS_FILE = os.path.join(ROOT, "admin_password.txt")
if not os.path.exists(PASS_FILE):
    open(PASS_FILE, "w").write("admin123")
PASSWORD = open(PASS_FILE).read().strip()
HIDDEN = {"server.py", "admin_password.txt"}
EXTS = {".mp4", ".webm", ".mov", ".m4v"}


class H(SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def authed(self):
        return hmac.compare_digest(self.headers.get("X-Pass", ""), PASSWORD)

    def reply(self, code, obj):
        b = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/api.php":
            path = "/api/" + parse_qs(urlparse(self.path).query).get("a", [""])[0]
        if os.path.basename(path) in HIDDEN:
            return self.reply(404, {"error": "not found"})
        if path == "/api/check":
            return self.reply(200 if self.authed() else 401, {"ok": self.authed()})
        super().do_GET()

    def do_POST(self):
        u = urlparse(self.path)
        if u.path == "/api.php":
            u = u._replace(path="/api/" + parse_qs(u.query).get("a", [""])[0])
        if not self.authed():
            return self.reply(401, {"error": "senha incorreta"})
        n = int(self.headers.get("Content-Length", 0))
        if u.path == "/api/config":
            try:
                data = json.loads(self.rfile.read(n))
            except ValueError:
                return self.reply(400, {"error": "json inválido"})
            with open("config.json", "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return self.reply(200, {"ok": True})
        if u.path == "/api/upload":
            name = parse_qs(u.query).get("name", ["video.mp4"])[0]
            name = re.sub(r"[^A-Za-z0-9._-]", "_", os.path.basename(name))
            if os.path.splitext(name)[1].lower() not in EXTS:
                return self.reply(400, {"error": "use mp4, webm, mov ou m4v"})
            os.makedirs("videos", exist_ok=True)
            dest = os.path.join("videos", name)
            if os.path.exists(dest):
                base, ext = os.path.splitext(name)
                name = "%s_%s%s" % (base, secrets.token_hex(2), ext)
                dest = os.path.join("videos", name)
            with open(dest, "wb") as f:
                while n > 0:
                    chunk = self.rfile.read(min(n, 1 << 20))
                    if not chunk:
                        break
                    f.write(chunk)
                    n -= len(chunk)
            return self.reply(200, {"src": "videos/" + name})
        self.reply(404, {"error": "not found"})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "127.0.0.1")
    print("Site:   http://%s:%d" % (host, port))
    print("Painel: http://%s:%d/admin.html  (senha em admin_password.txt)" % (host, port))
    ThreadingHTTPServer((host, port), H).serve_forever()
