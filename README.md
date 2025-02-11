# Markovate

*v0.0.1*

#### This CLI application will help you to generate a **markdown** from **OpenAPI** specification file.

## Clone and go to main directory

```
git clone https://github.com/anvarjamgirov/markovate.git
cd markovate
```

## Create environment and activate it

```
python3 -m venv ven
source ven/bin/activate
```

## Install requirements

```
pip install -r requirements.txt
```

## Using

- Put your OpenAPI specification file to **inputs** directory.
- Run following command in your terminal `python -m markovate <openapi-file-name>.json <output-file-name>.md -l ru -source description`.
- In result `<output-file-name>.md` will be generated from `<openapi-file-name>.json` in russian language and will use parsing source as description of endpoint. 

## Available values for -l[--language] and -s[--source] parameters

- `--language` or `-l`
  - en
  - ru
  - uz
- `--source` or `-s`
  - description
  - schema [not ready yet]

## What is next ?

You can change parsing logic in `markovate/utils.py`