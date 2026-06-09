from dataclasses import asdict, dataclass, field
from typing import Iterator, Literal


def create_openapi_spec(backo_meta: dict):
    openapi = {
        "openapi": "3.0.0",
        "info": {
            "title": backo_meta.get("name", ""),
            "description": backo_meta.get("description", ""),
            "version": backo_meta.get("version", ""),
        },
        "paths": {},
        "components": {
            "schemas": {
                "json-patch": {
                    "type": "array",
                    "items": {
                        "oneOf": [
                            {
                                "additionalProperties": False,
                                "required": ["value", "op", "path"],
                                "properties": {
                                    "path": {
                                        "description": "A JSON Pointer path.",
                                        "type": "string",
                                    },
                                    "op": {
                                        "description": "The operation to perform.",
                                        "type": "string",
                                        "enum": ["add", "replace", "test"],
                                    },
                                    "value": {
                                        "description": "The value to add, replace or test."
                                    },
                                },
                            },
                            {
                                "additionalProperties": False,
                                "required": ["op", "path"],
                                "properties": {
                                    "path": {
                                        "description": "A JSON Pointer path.",
                                        "type": "string",
                                    },
                                    "op": {
                                        "description": "The operation to perform.",
                                        "type": "string",
                                        "enum": ["remove"],
                                    },
                                },
                            },
                            {
                                "additionalProperties": False,
                                "required": ["from", "op", "path"],
                                "properties": {
                                    "path": {
                                        "description": "A JSON Pointer path.",
                                        "type": "string",
                                    },
                                    "op": {
                                        "description": "The operation to perform.",
                                        "type": "string",
                                        "enum": ["move", "copy"],
                                    },
                                },
                            },
                        ]
                    },
                }
            }
        },
    }
    for schema in extract_schemas(backo_meta):
        print(f"Adding schema {schema.title}")
        openapi["components"]["schemas"][schema.title] = asdict(schema)

    for route in extract_routes(backo_meta):
        print(f"Adding route {route.path}")
        openapi["paths"][route.path] = {}
        for method in route.methods:
            print(f"  Adding method {method.mode}")
            openapi["paths"][route.path][method.mode] = {
                "summary": method.summary,
                "operationId": method.operationId,
            }
            if len(method.parameters) > 0:
                openapi["paths"][route.path][method.mode]["parameters"] = (
                    method.parameters
                )
            if len(method.requestBody) > 0:
                openapi["paths"][route.path][method.mode]["requestBody"] = (
                    method.requestBody
                )
            if len(method.responses) > 0:
                openapi["paths"][route.path][method.mode]["responses"] = (
                    method.responses
                )
    return openapi


@dataclass
class Schema:
    title: str
    description: str
    type: str = "object"
    required: list[str] = field(default_factory=list)
    properties: dict[str, dict] = field(default_factory=dict)

    def add_property(self, title: str, type: str, description: str = ""):
        self.properties[title] = {}
        self.properties[title]["title"] = title
        self.properties[title]["description"] = description
        self.properties[title]["type"] = type


@dataclass
class Method:
    summary: str
    operationId: str
    mode: Literal["get", "post", "put", "delete", "patch"]
    requestBody: dict = field(default_factory=dict)
    parameters: list = field(default_factory=list)
    responses: dict = field(default_factory=dict)

    def add_response(self, status_code: str, description: str, content: dict):
        self.responses[status_code] = {
            "description": description,
            "content": content,
        }

    def add_parameter(self, parameter: dict):
        self.parameters.append(parameter)

    def add_request_body(self, content: dict):
        self.requestBody = {"content": content}


@dataclass
class Route:
    path: str
    methods: list[Method] = field(default_factory=list)

    def add_method(self, method: Method):
        self.methods.append(method)


def extract_schemas(backo_meta: dict) -> Iterator[Schema]:
    for collection in backo_meta.get("collections", []):
        schema = Schema(
            title=collection.get("name", ""),
            description=collection.get("description", ""),
        )
        schema_with_id = Schema(
            title=f"{collection.get('name', '')}_identified",
            description=collection.get("description", ""),
        )
        for name, infos in collection["item"]["sub_scheme"].items():
            # remove _id and _meta fields
            if name == "_meta":
                continue
            elif name == "_id":
                schema_with_id.add_property(
                    name, "string", infos.get("description", "")
                )
            else:
                type = "null"
                if "String" in infos["types"]:
                    type = "string"
                elif "Integer" in infos["types"]:
                    type = "integer"
                elif "Float" in infos["types"]:
                    type = "number"
                elif "Bool" in infos["types"]:
                    type = "boolean"
                elif "Dict" in infos["types"]:
                    type = "object"
                elif "List" in infos["types"]:
                    type = "array"
                schema.add_property(name, type, infos.get("description", ""))
                schema_with_id.add_property(name, type, infos.get("description", ""))

            if infos["required"]:
                schema.required.append(name)
                schema_with_id.required.append(name)

        yield schema
        yield schema_with_id


def extract_routes(backo_meta: dict) -> Iterator[Route]:
    for collection in backo_meta.get("collections", []):
        routes: dict[str, Route] = {}

        for route in collection["routes"]:
            if route["url"] not in routes:
                routes[route["url"]] = Route(path=route["url"])

            method = Method(
                mode=route["method"].lower(),
                operationId=f"{route['method'].lower()}_{route['url']}",
                summary=route["description"],
            )
            if route["parameters"]:
                for param in route["parameters"]:
                    match param["mode"]:
                        case "string-query":
                            method.add_parameter(
                                {
                                    "name": param["name"],
                                    "in": "query",
                                    "required": False,
                                    "schema": {"type": "string"},
                                    "description": "Query string",
                                }
                            )
                        case "path":
                            method.add_parameter(
                                {
                                    "name": param["name"],
                                    "in": "path",
                                    "required": True,
                                    "schema": {"type": "string"},
                                }
                            )
                        case "header":
                            pass
                        case "cookie":
                            pass
            if route["requestBody"]:
                for body in route["requestBody"]:
                    match body["type"]:
                        case "item":
                            method.add_request_body(
                                {
                                    "application/json": {
                                        "schema": {
                                            "$ref": f"#/components/schemas/{route['collection']}"
                                        }
                                    }
                                }
                            )
                        case "itempart":
                            ...
                        case "multipart":
                            ...
            if route["responses"]:
                for resp in route["responses"]:
                    ...  # TODO

            routes[route["url"]].add_method(method)

        yield from routes.values()
