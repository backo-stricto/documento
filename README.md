# Documento

Generate an OpenAPI documentation from a backend powered by [backo](https://github.com/bwallrich/backo).

## Installation

:warning: documento is not on PyPI yet !

`pip install documento`

## Usage

```bash
usage: documento [-h] [--theme {redoc,swagger}] [--host HOST] [--port PORT] url

Documento: OpenAPI documentation server for backo.

positional arguments:
  url                   Base URL of the backo instance.

options:
  -h, --help            show this help message and exit
  --theme {redoc,swagger}
                        theme to use for the documentation.
  --host HOST           host to serve the documentation on.
  --port PORT           port used to serve the documentation.
```