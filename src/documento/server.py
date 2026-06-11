import http.server
import json
from pathlib import Path

WEBSITE_DIR = Path(__file__).parent.parent / "themes"


def serve(spec: dict, theme: str, host: str, port: int) -> None:
    class HTTPHandler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs, directory=WEBSITE_DIR / theme)

        def do_GET(self) -> None:
            if self.path == "/openapi.json":
                body = json.dumps(spec).encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            else:
                super().do_GET()

    with http.server.HTTPServer((host, port), HTTPHandler) as server:
        server.serve_forever()
