FROM python:3.12-slim-bookworm AS build

# Performance Optimizations
ENV PYTHONBUFFERED=1 UV_LINK_MODE=copy UV_COMPILE_BYTECODE=1

# Get Packages to be able to install uv
RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates && apt-get upgrade -y openssl

# Install uv
ADD https://astral.sh/uv/install.sh /uv-installer.sh
RUN sh /uv-installer.sh && rm /uv-installer.sh

# Set path for uv
ENV PATH="/root/.local/bin:$PATH"

# Set working directory
WORKDIR /watcher

# Copy pyproject.toml and uv.lock to install dependencies. Cache dependencies separately.
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv uv sync --frozen --no-install-project --no-dev

# Copy the rest of the application code. UV sync the project.
COPY . .
RUN --mount=type=cache,target=/root/.cache/uv uv sync --frozen --no-dev

# Multi-stage build for runtime
FROM python:3.12-slim-bookworm AS runtime
WORKDIR /watcher
COPY --from=build /root/.local/bin/uv /usr/.local/bin/uv
COPY --from=build /watcher /watcher
ENV PATH="/root/.local/bin:$PATH"
ENV PATH="/usr/.local/bin:$PATH"

# Create celery user and group with specific UID/GID (needed for Celery workers)
RUN groupadd -r -g 999 celery && useradd -r -u 999 -g celery -m -d /home/celery celery

# Create watcher user and group, add to celery group for shared access
RUN groupadd -r watcher && useradd -r -g watcher -G celery -m -d /home/watcher watcher

# Set ownership to celery group (both users can write via group permissions)
RUN chown -R celery:celery /watcher /home/celery
RUN chown -R watcher:watcher /home/watcher
RUN chmod -R g+w /watcher
USER watcher

EXPOSE 8000
CMD ["uv", "run", "--", "gunicorn", "src.app:app", "-c", "gunicorn.conf.py"]
