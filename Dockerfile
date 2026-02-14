FROM ghcr.io/astral-sh/uv:python3.12-alpine AS builder
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

ENV UV_PYTHON_DOWNLOADS=0

WORKDIR /app
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=.python-version,target=.python-version \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev

COPY pyproject.toml ./pyproject.toml
COPY uv.lock ./uv.lock
COPY alembic.ini ./alembic.ini
COPY alembic ./alembic
COPY src ./src

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

FROM python:3.12-alpine
RUN adduser -S -u 999 nonroot
RUN mkdir -p /app/database \
    && chown -R nonroot /app/database \
    && mkdir -p /app/logs \
    && chown -R nonroot /app/logs
HEALTHCHECK --interval=30s --timeout=5s CMD wget -q --spider http://127.0.0.1:8000/health || exit 1

COPY --from=builder --chown=nonroot:nonroot /app /app

ENV PATH="/app/.venv/bin:$PATH"

USER nonroot

WORKDIR /app

CMD ["python", "src/date_task_bot/main.py"]
