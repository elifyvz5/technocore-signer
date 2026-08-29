
import json
import hmac
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

from technocore_agent import (
    load_identity,
    did_from_private_key,
    post_signed_message,
)

KEY_FILE = Path("/run/secrets/identity.pem")
PASS_FILE = Path("/run/secrets/passphrase")
TOKEN_FILE = Path("/run/secrets/token")

PASSPHRASE = PASS_FILE.read_bytes()
TOKEN = TOKEN_FILE.read_text().strip()

PRIVATE_KEY = load_identity(
    KEY_FILE,
    passphrase=PASSPHRASE,
    allow_prompt=False,
)

DID = did_from_private_key(PRIVATE_KEY)


class Handler(BaseHTTPRequestHandler):

    def send_json(self, status, data):
        body = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/health":
            return self.send_json(200, {
                "ok": True,
                "did": DID
            })

        return self.send_json(404, {"error": "not found"})

    def do_POST(self):
        if self.path != "/say":
            return self.send_json(404, {"error": "not found"})

        supplied_token = self.headers.get("X-Signer-Token", "")

        if not hmac.compare_digest(supplied_token, TOKEN):
            return self.send_json(403, {"error": "forbidden"})

        try:
            length = int(self.headers.get("Content-Length", "0"))

            if length <= 0 or length > 8192:
                raise ValueError("invalid request size")

            data = json.loads(self.rfile.read(length))

            if not isinstance(data, dict):
                raise ValueError("invalid JSON")

            room = str(data.get("room", ""))
            text = str(data.get("text", ""))

            if room not in {"lobby", "technocore"}:
                raise ValueError("room not allowed")

            if not 1 <= len(text) <= 1000:
                raise ValueError("invalid text length")

            result = post_signed_message(
                PRIVATE_KEY,
                room,
                text,
                timeout=15,
            )

            return self.send_json(200, result)

        except Exception as exc:
            return self.send_json(400, {"error": str(exc)})

    def log_message(self, format, *args):
        return


HTTPServer(("0.0.0.0", 8787), Handler).serve_forever()
