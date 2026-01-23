ARG UV_VERSION=0.9.15
ARG PYTHON_VERSION=3.12

FROM ghcr.io/astral-sh/uv:${UV_VERSION}-python${PYTHON_VERSION}-bookworm-slim AS builder

ENV UV_LINK_MODE=copy UV_COMPILE_BYTECODE=1 UV_PYTHON_DOWNLOADS=never

WORKDIR /watcher

COPY pyproject.toml uv.lock ./

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-install-project

COPY . /watcher
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

FROM python:${PYTHON_VERSION}-slim-bookworm AS runtime

RUN groupadd -r appgroup && \
    useradd -r -g appgroup -m -d /home/celery celery && \
    useradd -r -g appgroup -m -d /home/watcher watcher

ENV PATH="/watcher/.venv/bin:$PATH" PYTHONUNBUFFERED=1 UV_PYTHON_DOWNLOADS=never

WORKDIR /watcher

COPY --from=builder --chown=watcher:appgroup /watcher /watcher

USER watcher

EXPOSE 8000
CMD ["granian_run.sh"]
