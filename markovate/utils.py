import json
from typing import Any

from deep_translator import GoogleTranslator

from markovate import SOURCE, INPUT_PATH, OUTPUT_PATH


def validate_openapi(openapi: dict) -> None:
    if type(openapi) is not dict:
        raise ValueError("OpenAPI specification must be dict.")
    if openapi.get('info') is None or openapi.get('paths') is None:
        raise ValueError("OpenAPI specific fields not found.")


def load_openapi(openapi_file_name: str) -> dict[str, Any]:
    with open(INPUT_PATH / openapi_file_name, 'r') as openapi_file:
        openapi = json.loads(openapi_file.read())
    validate_openapi(openapi)
    return openapi


def parse_information_from_endpoint_description(endpoint: dict) -> str:
    parsed_description = endpoint.get('description', "Description is not provided.")
    if parsed_description.startswith('**Parameters**'):
        parsed_description = "{}\n\n{}".format(
            endpoint['summary'],
            parsed_description,
        )
    return parsed_description


def parse_information_from_endpoint_schema(openapi: dict, endpoint: dict) -> str:
    parsed_information = endpoint['summary']
    if endpoint.get('parameters') is not None:
        parsed_information += "\n\n**Parameters**\n\n{}".format(
            '\n'.join([
                "- **{}**{}: {}".format(
                    parameter.get('name'),
                    "*" if parameter.get('required') else '',
                    parameter['schema'].get('title'),
                ) for parameter in endpoint['parameters']
            ])
        )
    if endpoint.get('requestBody') is not None:
        if endpoint['requestBody']['content'].get('application/x-www-form-urlencoded'):
            ref = endpoint['requestBody']['content']['application/x-www-form-urlencoded']['schema'].get('$ref')
        else:
            ref = endpoint['requestBody']['content']['application/json']['schema'].get('$ref')
        if ref is not None:
            schema_key = ref.split('/')[-1]
            parsed_information += "\n\n**Request body**\n\n- [{}](#{})".format(
                openapi['components']['schemas'][schema_key]['title'],
                schema_key.lower(),
            )
    if endpoint.get('responses') is not None:
        responses = []
        for status, response in endpoint.get('responses').items():
            ref = response['content']['application/json']['schema'].get('$ref')
            if ref is not None:
                response_schema_key = ref.split('/')[-1]
                responses.append(
                    "- **{}**: [{}](#{}) [{}]".format(
                        status,
                        response['description'],
                        response_schema_key.lower(),
                        response_schema_key,
                    )
                )
            else:
                responses.append(
                    "- **{}**: {} [Empty]".format(
                        status,
                        response['description'],
                    )
                )
        parsed_information += "\n\n**Responses**\n\n{}".format(
            '\n'.join(responses),
        )
    return parsed_information


def parse_schema_information(openapi: dict, schema: dict):
    properties = []
    for property_name, property_data in schema['properties'].items():
        title = property_data.get('title')
        ref = property_data.get('$ref')
        property_schema_key = None
        if title is None and ref is not None:
            property_schema_key = ref.split('/')[-1]
            title = openapi['components']['schemas'][property_schema_key]['title']
        property_type = property_data.get('type', 'object')
        if property_type == 'object' and property_data.get('anyOf'):
            property_types = []
            for _ in property_data['anyOf']:
                _type = _.get('type', 'object')
                if _type == 'array':
                    property_types.append(
                        "[{}]".format(
                            _['items']['type'],
                        )
                    )
                elif _type == 'object':
                    type_schema_key = _['$ref'].split('/')[-1]
                    property_types.append(
                        "[{}] (#{})".format(
                            type_schema_key,
                            type_schema_key.lower(),
                        )
                    )
                else:
                    property_types.append(
                        _type,
                    )
            property_type = ', '.join(property_types)
        if ref is None:
            properties.append(
                "- **{}**{}: {} [{}]{}".format(
                    property_name,
                    "*" if property_name in schema.get('required', []) else '',
                    title,
                    property_type,
                    f"\n\n\t {property_data['description']}" if property_data.get('description') else '',
                )
            )
        else:
            properties.append(
                "- **{}**{}: [{}](#{}) [{}]{}".format(
                    property_name,
                    "*" if property_name in schema.get('required', []) else '',
                    title,
                    property_schema_key.lower(),
                    property_type,
                    f"\n\n\t {property_data['description']}" if property_data.get('description') else '',
                )
            )
    return "### {}\n{}".format(
        schema['title'],
        '\n'.join(properties)
    )


def generate_markdown_string(openapi: dict, source: str) -> str:
    title = openapi['info']['title']
    description = openapi['info']['description']
    version = openapi['info']['version']
    endpoints_markdown_list = []
    for endpoint_path, endpoint_by_methods in openapi['paths'].items():
        for method, endpoint in endpoint_by_methods.items():
            if source == SOURCE.DESCRIPTION:
                parsed_information: str = parse_information_from_endpoint_description(endpoint)
            else:
                parsed_information = parse_information_from_endpoint_schema(openapi, endpoint)
            endpoints_markdown_list.append(
                "### [{}] ***{}***\n\n#### {}".format(
                    method.upper(),
                    endpoint_path,
                    parsed_information,
                )
            )
    schemas_markdown_list = []
    for schema_key, schema in openapi['components']['schemas'].items():
        schemas_markdown_list.append(parse_schema_information(openapi, schema))
    result = "# {} ***[v{}]***\n\n## {}\n\n\n\n{}\n\n\n\n## Schemas\n\n\n\n{}".format(
        title,
        version,
        description,
        '\n\n\n\n'.join(endpoints_markdown_list),
        '\n\n\n\n'.join(schemas_markdown_list),
    )
    return result


def translate_markdown_string(markdown_string: str, target: str):
    translator = GoogleTranslator(source='en', target=target)
    return translator.translate(markdown_string)


def save_to_markdown_file(openapi_string: str, markdown_file_name: str) -> None:
    with open(OUTPUT_PATH / markdown_file_name, 'w') as markdown_file:
        markdown_file.write(openapi_string)
