"""This module provides the Markovate CLI."""
# markovate/cli.py
import json
from typing import Optional, Annotated

import typer

from markovate import LANGUAGE, SOURCE
from markovate.utils import load_openapi, generate_markdown_string, save_to_markdown_file, translate_markdown_string
from markovate.callbacks import _openapi_file_name_callback, _markdown_file_name_callback, _language_callback, \
    _source_callback, _version_callback

app = typer.Typer()


@app.command()
def generate(
        openapi_file_name: Annotated[
            str, typer.Argument(callback=_openapi_file_name_callback)
        ] = "openapi.json",
        markdown_file_name: Annotated[
            str, typer.Argument(callback=_markdown_file_name_callback)
        ] = "markdown.md",
        language: str = typer.Option(LANGUAGE.EN, '--language', '-l', callback=_language_callback),
        source: str = typer.Option(SOURCE.DESCRIPTION, '--source', '-s', callback=_source_callback),
) -> None:
    try:
        openapi = load_openapi(openapi_file_name)
        markdown_string = generate_markdown_string(openapi, source)
        if language != LANGUAGE.EN:
            translated_parts = []
            current_part = ''
            for part in markdown_string.split('\n\n\n\n'):
                if len(current_part + part) > 5000:
                    translated_parts.append(
                        translate_markdown_string(current_part, language)
                    )
                    current_part = part
                else:
                    current_part = '\n\n\n\n'.join([current_part, part])
            else:
                if len(current_part) > 0:
                    translated_parts.append(
                        translate_markdown_string(current_part, language)
                    )
            markdown_string = '\n\n\n\n'.join(translated_parts)
        save_to_markdown_file(markdown_string, markdown_file_name)
        typer.secho(
            f"""Markdown[{markdown_file_name}] generated for OpenAPI[{openapi_file_name}] specification.\n\n"""
            f"""Language: {LANGUAGE.DICT.get(language)}\n"""
            f"""Parsing source: {SOURCE.DICT.get(source)}""",
            fg=typer.colors.GREEN,
        )
    except FileNotFoundError as e:
        typer.secho(
            f'Reading file({e.filename}) failed.', fg=typer.colors.RED,
        )
        raise typer.Exit(1)
    except json.decoder.JSONDecodeError:
        typer.secho(
            f'OpenAPI json file\'s decoding failed.', fg=typer.colors.RED,
        )
        raise typer.Exit(1)
    except ValueError as e:
        typer.secho(
            '\n'.join(e.args), fg=typer.colors.RED,
        )
        raise typer.Exit(1)


@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        help="Show the application's version and exit.",
        callback=_version_callback,
        is_eager=True,
    )
) -> None:
    return
