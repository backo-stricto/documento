import json
from pathlib import Path


def create_openapi_spec(backo_meta: Path):
    # Load the Backo metadata
    with open(backo_meta, "r") as f:
        meta = json.load(f)

    # TODO: transform to OpenAPI format
    openapi = meta

    return openapi
