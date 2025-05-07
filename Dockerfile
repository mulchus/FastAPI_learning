FROM python:3.12.7-slim-bookworm

ARG BASE_DIR=/app

ENV \
    # python
    PYTHONPATH=${BASE_DIR}/src \
    PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    # prevents python creating .pyc files
    PYTHONDONTWRITEBYTECODE=1 \
    \
    # poetry
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    \
    # pip
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100

RUN pip install pipx
RUN PIPX_BIN_DIR=/usr/local/bin pipx install poetry==1.8.4

WORKDIR ${BASE_DIR}

COPY pyproject.toml ./poetry.lock ./

RUN poetry install --no-ansi

COPY src src
COPY tests tests

RUN mkdir -p static
RUN echo  "Hello!" > static/hello.txt

ENV \
    UVICORN_PORT="8000" \
    UVICORN_HOST="0.0.0.0" \
    UVICORN_FACTORY="true" \
    UVICORN_APP="src.main:main"

CMD "uvicorn"
