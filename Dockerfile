# syntax=docker/dockerfile:1

FROM python:3.10.8-alpine3.16

# Set env
ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8
# Set python env
ENV PYTHONUNBUFFERED 1
ENV PYTHONFAULTHANDLER 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONHASHSEED random
# Set pip env
ENV PIP_NO_CACHE_DIR off
ENV PIP_DEFAULT_TIMEOUT 100
ENV PIP_DISABLE_PIP_VERSION_CHECK on
# Set poetry env
ENV POETRY_HOME="/opt/poetry"
ENV POETRY_VIRTUALENVS_CREATE=false
ENV POETRY_VIRTUALENVS_IN_PROJECT=false
ENV POETRY_NO_INTERACTION=1
ENV POETRY_VERSION=1.2.2

# Create workdir
WORKDIR /app

# Copy files
COPY . .

# Install pipenv and compilation dependencies
RUN apk update \
    && apk add --update \
        gcc \
        libc-dev \
    && rm -rf /var/cache/apk/*

# Update pip
RUN python3 -m pip install --upgrade pip
RUN pip3 install --upgrade wheel setuptools

# Install poetry
RUN pip3 install poetry

# Install app dependencies
RUN poetry update && poetry install --without dev

# Run alembic migrations & app
CMD poetry run python3 main.py ;
