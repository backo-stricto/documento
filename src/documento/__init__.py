import argparse
import json
import urllib.request

from .openapi import create_openapi_spec
from .server import serve


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Documento: OpenAPI documentation generator for backo backends."
    )
    from_group = parser.add_mutually_exclusive_group(required=True)
    from_group.add_argument(
        "--from-url",
        dest="url",
        help="URL of backo backend.",
    )
    from_group.add_argument(
        "--from-file",
        dest="file",
        help="path to the backo metadata json file.",
    )
    subparsers = parser.add_subparsers(
        title="Commands",
        dest="command",
        required=True,
    )
    # Generate subcommand
    parser_generate = subparsers.add_parser(
        "generate",
        help="Generate OpenAPI json from backo metadata json.",
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
        "--theme",
        help="theme to use for the documentation.",
        choices=["swagger", "redoc"],
        default="swagger",
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


def main() -> None:
    # Parse command line arguments
    args = parse_args()

    # Get metadata
    if args.url:
        # from backo _meta route
        with urllib.request.urlopen(f"{args.url}/_meta") as r:
            metadata = json.load(r)
    elif args.file:
        # from meta file
        with open(args.file, "r") as f:
            metadata = json.load(f)
    else:
        raise ValueError("Either --from-url or --from-file must be provided.")

    # Handle the command generate
    if args.command == "generate":
        print(f"Generating OpenAPI yml from {args.meta}")
        # Convert to OpenAPI spec
        spec = create_openapi_spec(metadata)
        # Save to output file
        with open(args.output, "w") as f:
            json.dump(spec, f, indent=4)

    # Handle the command serve
    elif args.command == "serve":
        # Convert to OpenAPI spec
        spec = create_openapi_spec(metadata)
        # Serve the spec
        print(f"Serving documentation on {args.host} at port {args.port}")
        serve(spec, args.theme, args.host, args.port)
