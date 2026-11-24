"""Private Cloud Run service. Cloud Run IAM provides ingress authentication."""
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from cloud_probe import probe

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/healthz":
            status, data = 200, {"status": "ok"}
        elif self.path == "/v1/connectivity":
            try:
                status, data = 200, probe()
            except Exception:
                status, data = 502, {"authenticated": False, "error": "UniFi cloud probe failed"}
        else:
            status, data = 404, {"error": "Not found"}
        body = json.dumps(data).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

if __name__ == "__main__":
    ThreadingHTTPServer(("0.0.0.0", int(os.environ.get("PORT", "8080"))), Handler).serve_forever()
