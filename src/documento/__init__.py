import argparse
import http.server
import json
import urllib.request
from pathlib import Path

from .openapi import create_openapi_spec

WEBSITE_DIR = Path(__file__).parent.parent / "website"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Documento: OpenAPI documentation generator for backo backends."
    )
    subparsers = parser.add_subparsers(
        title="Commands", dest="command", required=True
    )
    # Generate subcommand
    parser_generate = subparsers.add_parser(
        "generate",
        help="Generate OpenAPI json from backo metadata json.",
    )
    parser_generate.add_argument(
        "meta",
        help="path to the backend metadata json file.",
    )
    parser_generate.add_argument(
        "--output",
        help="path to the output OpenAPI yml file.",
        default="./openapi.json",
    )
    # Serve subcommand
    parser_serve = subparsers.add_parser(
        "serve",
        help="Serve the documentation locally.",
    )
    parser_serve.add_argument(
        "url",
        help="backo backend's URL to document.",
    )
    parser_serve.add_argument(
        "--host",
        help="host to serve the documentation on.",
        default="localhost",
    )
    parser_serve.add_argument(
        "--port",
        help="port used to serve the documentation.",
        default=8000,
    )
    return parser.parse_args()


def serve(spec: dict, host: str, port: int) -> None:
    class HTTPHandler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs, directory=WEBSITE_DIR)

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


def main() -> None:
    # Parse command line arguments
    args = parse_args()

    # Handle the command generate
    if args.command == "generate":
        print(f"Generating OpenAPI yml from {args.meta}")
        # Convert to OpenAPI spec
        spec = create_openapi_spec(args.meta)
        # Save to output file
        with open(args.output, "w") as f:
            json.dump(spec, f, indent=4)

    # Handle the command serve
    elif args.command == "serve":
        # Get metadata from backo
        with urllib.request.urlopen(f"{args.url}/_meta") as r:
            metadata = json.load(r)
        # Convert to OpenAPI spec
        spec = create_openapi_spec(metadata)
        # Serve the spec
        print(f"Serving documentation on {args.host} at port {args.port}")
        serve(spec, args.host, args.port)
