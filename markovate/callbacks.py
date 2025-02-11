import typer

from markovate import __app_name__, __version__, LANGUAGE, SOURCE


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"{__app_name__} v{__version__}")
        raise typer.Exit()


def _openapi_file_name_callback(value: str) -> str:
    if not value.endswith('.json'):
        raise ValueError("OpenAPI specification must be json file")
    return value


def _markdown_file_name_callback(value: str) -> str:
    if not value.endswith('.md'):
        raise ValueError("Markdown file name must ends with .md")
    return value


def _language_callback(value: str) -> str:
    if value is None:
        return LANGUAGE.EN
    if type(value) is not str:
        typer.secho(
            "Be careful, language option value must be str.", fg=typer.colors.RED,
        )
        raise typer.Exit(1)
    if LANGUAGE.DICT.get(value) is None:
        typer.secho(
            "Not acceptable value for language option, please select one of these: {}".format(
                ','.join(LANGUAGE.DICT.keys()),
            ), fg=typer.colors.RED,
        )
        raise typer.Exit(1)
    return value


def _source_callback(value: str) -> str:
    if value is None:
        return SOURCE.DESCRIPTION
    if type(value) is not str:
        typer.secho(
            "Be careful, source option value must be str.", fg=typer.colors.RED,
        )
        raise typer.Exit(1)
    if SOURCE.DICT.get(value) is None:
        typer.secho(
            "Not acceptable value for source option, please select one of these: {}".format(
                ','.join(SOURCE.DICT.keys()),
            ), fg=typer.colors.RED,
        )
        raise typer.Exit(1)
    return value
