# Documento

Generate an OpenAPI documentation from a backend powered by [backo](https://github.com/bwallrich/backo).

## Installation

:warning: documento is not on PyPI yet !

`pip install documento`

## Usage

```bash
usage: documento [-h] (--from-url URL | --from-file FILE) {generate,serve} ...

Documento: OpenAPI documentation generator for backo backends.

options:
  -h, --help        show this help message and exit
  --from-url URL    URL of backo backend.
  --from-file FILE  path to the backo metadata json file.

Commands:
  {generate,serve}
    generate        Generate OpenAPI json from backo metadata json.
    serve           Serve the documentation locally.
```

### Generate

The `generate` subcommand is used if you only wants to create a `openapi.json` file.

```bash
usage: documento generate [-h] [--output OUTPUT]

options:
  -h, --help       show this help message and exit
  --output OUTPUT  path to the output OpenAPI yml file.
```

### Serve

The `serve` subcommand is used if you only to quickly deploy an HTTP server containing the OpenAPI documentation (either using swagger or redoc).

```bash
usage: documento serve [-h] [--theme {swagger,redoc}] [--host HOST] [--port PORT]

options:
  -h, --help            show this help message and exit
  --theme {swagger,redoc}
                        theme to use for the documentation.
  --host HOST           host to serve the documentation on.
  --port PORT           port used to serve the documentation.
```
