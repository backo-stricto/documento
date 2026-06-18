# Documento

Display an OpenAPI documentation from a backend powered by [backo](https://github.com/bwallrich/backo).

Documento can be powered by either Swagger UI, Scalar, ReDoc or RapiDoc.

## Installation

`pip install documento`

## Usage

```bash
usage: documento [-h] [--theme {redoc,scalar,swagger,rapidoc}] [--host HOST] [--port PORT] url

Documento: OpenAPI documentation server for backo.

positional arguments:
  url                   Base URL of the backo instance.

options:
  -h, --help            show this help message and exit
  --theme {redoc,scalar,swagger,rapidoc}
                        theme to use for the documentation.
  --host HOST           host to serve the documentation on.
  --port PORT           port used to serve the documentation.
```

**Minimal example:**

In [`backo/example`](https://github.com/bwallrich/backo/tree/main/examples) run the `nationality/backoffice.py`, then

```bash
documento http://localhost:5000/nationality
```

And access it on `http://localhost:8000/`.