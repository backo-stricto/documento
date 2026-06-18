import http.server
import json
import urllib.request
from pathlib import Path
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - [%(levelname)s] %(message)s"
)

THEMES_DIR = Path(__file__).parent / "themes"


def serve(spec_url: str, theme: str, host: str, port: int) -> None:
    class HTTPHandler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs, directory=THEMES_DIR / theme)

        def do_GET(self) -> None:
            if self.path == "/openapi.json":
                # Get OpenAPI specification from backo
                with urllib.request.urlopen(spec_url) as req:
                    spec = json.load(req)
                body = json.dumps(spec).encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            else:
                super().do_GET()

    with http.server.HTTPServer((host, port), HTTPHandler) as server:
        logging.info(f"Serving documentation at http://{host}:{port}")
        logging.info("Press Ctrl+C to quit")
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            logging.info("Shutting down server")
            server.server_close()
