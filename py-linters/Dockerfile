FROM docker.io/python:3.12.5-alpine

ARG BASE_DIR=/opt/linters

ENV \
    # python
    PYTHONUNBUFFERED=1 \
    # poetry
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    # pip
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100

RUN apk add --no-cache curl

RUN curl -sSL https://install.python-poetry.org | POETRY_VERSION=1.8.3 python3 -
ENV PATH="/root/.local/bin:${PATH}"

WORKDIR ${BASE_DIR}

COPY ./pyproject.toml ./poetry.lock ./

RUN poetry install --no-ansi
