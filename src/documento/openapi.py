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
        "components": {"schemas": {}},
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
                openapi["paths"][route.path][method.mode]["parameters"] = method.parameters
            if len(method.requestBody) > 0:
                openapi["paths"][route.path][method.mode]["requestBody"] = method.requestBody
            if len(method.responses) > 0:
                openapi["paths"][route.path][method.mode]["responses"] = method.responses
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
            title=f"{collection.get("name", "")}_identified",
            description=collection.get("description", ""),
        )
        for name, infos in collection["item"]["sub_scheme"].items():
            # remove _id and _meta fields
            if name == "_meta":
                continue
            elif name == "_id":
                schema_with_id.add_property(name, "string", infos.get("description", ""))
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
        route = Route(path=f"/{collection['name']}")

        if collection["rights"]["read"]:
            get = Method(
                mode="get",
                operationId=f"get_{collection['name']}",
                summary=f"read {collection['name']} collection",
            )
            get.add_response(
                "200",
                f"Read whole list of {collection['name']}",
                {
                    "application/json": {
                        "schema": {
                            "title": f"Response list of {collection['name']}",
                            "type": "array",
                            "items": {
                                "$ref": f"#/components/schemas/{collection['name']}_identified"
                            },
                        }
                    }
                },
            )
            route.add_method(get)

        if collection["rights"]["create"]:
            post = Method(
                mode="post",
                operationId=f"post_{collection['name']}",
                summary=f"create object in {collection['name']} collection",
            )
            post.add_request_body(
                {
                    "application/json": {
                        "schema": {
                            "$ref": f"#/components/schemas/{collection['name']}"
                        }
                    }
                },
            )
            route.add_method(post)

        yield route

        route = Route(path=f"/{collection['name']}/_meta")
        route.add_method(
            Method(
                mode="get",
                operationId=f"meta_{collection['name']}",
                summary=f"get metadata for {collection['name']} collection",
            )
        )
        yield route

        route = Route(path=f"/{collection['name']}/_check")
        post = Method(
            mode="post",
            operationId=f"check_{collection['name']}",
            summary=f"check {collection['name']} collection",
        )
        post.add_request_body(
            {
                "application/json": {
                    "schema": {
                        "$ref": f"#/components/schemas/{collection['name']}"
                    }
                }
            },
        )
        route.add_method(post)
        yield route

        route = Route(path=f"/{collection['name']}/{{_id}}")
        if collection["rights"]["create"]:
            post = Method(
                mode="post",
                operationId=f"post_{collection['name']}",
                summary=f"create object in {collection['name']} collection",
            )
            post.add_parameter(
                {
                    "name": "_id",
                    "in": "path",
                    "required": True,
                    "schema": {"type": "string"},
                }
            )
            post.add_request_body(
                {
                    "application/json": {
                        "schema": {
                            "$ref": f"#/components/schemas/{collection['name']}"
                        }
                    }
                }
            )
            route.add_method(post)

        if collection["rights"]["read"]:
            get = Method(
                mode="get",
                operationId=f"get_{collection['name']}",
                summary=f"get object with id {{_id}} in {collection['name']} collection",
            )
            get.add_parameter(
                {
                    "name": "_id",
                    "in": "path",
                    "required": True,
                    "schema": {"type": "string"},
                }
            )
            route.add_method(get)

        if collection["rights"]["modify"]:
            put = Method(
                mode="put",
                operationId=f"put_{collection['name']}",
                summary=f"update object with id {{_id}} in {collection['name']} collection",
            )
            put.add_parameter(
                {
                    "name": "_id",
                    "in": "path",
                    "required": True,
                    "description": f"id of the {collection['name']} object to update",
                    "schema": {"type": "string"},
                }
            )
            route.add_method(put)

            patch = Method(
                mode="patch",
                operationId=f"patch_{collection['name']}",
                summary=f"update object with id {{_id}} in {collection['name']} collection",
            )
            patch.add_parameter(
                {
                    "name": "_id",
                    "in": "path",
                    "required": True,
                    "description": f"id of the {collection['name']} object to patch",
                    "schema": {"type": "string"},
                }
            )
            route.add_method(patch)

        if collection["rights"]["delete"]:
            delete = Method(
                mode="delete",
                operationId=f"delete_{collection['name']}",
                summary=f"delete object with id {{_id}} in {collection['name']} collection",
            )
            delete.add_parameter(
                {
                    "name": "_id",
                    "in": "path",
                    "required": True,
                    "description": f"id of the {collection['name']} object to delete",
                    "schema": {"type": "string"},
                }
            )
            route.add_method(delete)

        yield route

        # TODO route action, route view
