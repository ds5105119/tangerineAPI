FROM python:3.12-slim
LABEL authors="IIH"
MAINTAINER ds5105119@gmail.com

# 프로젝트 폴더
WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    POETRY_VERSION=1.8.2 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=false \
    POETRY_NO_INTERACTION=1

ENV PATH="$POETRY_HOME/bin:$PATH"

# 시스템 패키지 설치 및 Poetry 설치
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libpq-dev curl \
    && rm -rf /var/lib/apt/lists/* \
    && curl -sSL https://install.python-poetry.org | python3 -

# Copy potery pyproject.toml file into docker containter and install it
COPY pyproject.toml ./
RUN poetry install --no-interaction --no-ansi --only main


# Copy Django Project File
COPY . .
