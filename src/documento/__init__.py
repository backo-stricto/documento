import argparse
import json
import urllib.request
import os

from .server import serve, THEMES_DIR


def parse_args() -> argparse.Namespace:
    # get all existings themes
    themes_list = [f.name for f in os.scandir(THEMES_DIR) if f.is_dir()]

    # Setup argument parser
    parser = argparse.ArgumentParser(
        description="Documento: OpenAPI documentation server for backo."
    )
    parser.add_argument("url", help="Base URL of the backo instance.", type=str)
    parser.add_argument(
        "--theme",
        help="theme to use for the documentation.",
        choices=themes_list,
        default=themes_list[-1],
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
