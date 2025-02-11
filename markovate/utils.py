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


def parse_information_from_endpoint_schema(endpoint: dict) -> str:
    return "Parsing logic for {} source is not ready yet.".format(SOURCE.SCHEMA)


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
                parsed_information = parse_information_from_endpoint_schema(endpoint)
            endpoints_markdown_list.append(
                "### [{}] ***{}***\n\n#### {}".format(
                    method.upper(),
                    endpoint_path,
                    parsed_information,
                )
            )
    result = "# {} ***[v{}]***\n\n## {}\n\n\n\n".format(
        title,
        version,
        description,
    ) + '\n\n\n\n'.join(endpoints_markdown_list)
    return result


def translate_markdown_string(markdown_string: str, target: str):
    translator = GoogleTranslator(source='en', target=target)
    return translator.translate(markdown_string)


def save_to_markdown_file(openapi_string: str, markdown_file_name: str) -> None:
    with open(OUTPUT_PATH / markdown_file_name, 'w') as markdown_file:
        markdown_file.write(openapi_string)
