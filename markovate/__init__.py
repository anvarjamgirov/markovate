"""Top-level package for Markovate."""
# markovate/__init__.py

__app_name__ = "markovate"
__version__ = "0.0.1"

from pathlib import Path


class LANGUAGE:
    EN = 'en'
    RU = 'ru'
    UZ = 'uz'

    DICT = {
        EN: "English",
        RU: "Русский",
        UZ: "O'zbekcha",
    }


class SOURCE:
    DESCRIPTION = 'description'
    SCHEMA = 'schema'

    DICT = {
        DESCRIPTION: "From description of the endpoint",
        SCHEMA: "From schema of the endpoint",
    }


INPUT_PATH = Path('./inputs')
OUTPUT_PATH = Path('./outputs')
