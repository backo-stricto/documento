import argparse
import json
import urllib.request

from .server import serve


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Documento: OpenAPI documentation server for backo."
    )
    parser.add_argument("url", help="Base URL of the backo instance.", type=str)
    parser.add_argument(
        "--theme",
        help="theme to use for the documentation.",
        choices=["swagger", "redoc"],
        default="swagger",
    )
    parser.add_argument(
        "--host",
        help="host to serve the documentation on.",
        default="localhost",
    )
    parser.add_argument(
        "--port",
        help="port used to serve the documentation.",
        default=8000,
    )
    return parser.parse_args()


def main() -> None:
    # Parse command line arguments
    args = parse_args()

    # Get OpenAPI specification from backo
    with urllib.request.urlopen(f"{args.url}/openapi") as req:
        openapi_spec = json.load(req)
    # Serve the OpenAPI documentation
    serve(openapi_spec, args.theme, args.host, args.port)
