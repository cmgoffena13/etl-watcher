FROM python:3.12-slim-bookworm
ENV PYTHONBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates && apt-get upgrade -y openssl

ADD https://astral.sh/uv/install.sh /uv-installer.sh
RUN sh /uv-installer.sh && rm /uv-installer.sh

ENV PATH="/root/.local/bin/:$PATH"
ENV UV_LINK_MODE=copy

WORKDIR /watcher

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --compile-bytecode

# Create celery user and group
RUN groupadd -r celery && useradd -r -g celery -m -d /home/celery celery
RUN chown -R celery:celery /watcher
RUN chown -R celery:celery /home/celery

COPY . .

EXPOSE 8000
CMD ["uv", "run", "--", "gunicorn", "src.app:app", "-c", "gunicorn.conf.py"]
