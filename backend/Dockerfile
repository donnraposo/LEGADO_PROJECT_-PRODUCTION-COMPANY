FROM python:3.14-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONPATH=/app/src

WORKDIR /app

RUN groupadd --system app \
    && useradd --system --gid app --create-home app

COPY pyproject.toml README.md ./
COPY src ./src
COPY manage.py ./

RUN python -m pip install --upgrade pip \
    && python -m pip install .

EXPOSE 8000

CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "config.asgi:application"]

FROM base AS development

COPY tests ./tests

RUN python -m pip install ".[dev]"

RUN mkdir -p /app/.pytest_cache /app/.ruff_cache \
    && chown -R app:app /app/.pytest_cache /app/.ruff_cache

USER app

FROM base AS runtime

USER app
