import argparse
import os

from .server import THEMES_DIR, serve


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

    # Serve the OpenAPI documentation
    serve(f"{args.url}/openapi", args.theme, args.host, args.port)
