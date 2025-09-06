install:
	uv sync --frozen --compile-bytecode

build:
	docker build -t watcher . && docker images -f "dangling=true" -q | xargs docker rmi

docker-run:
	docker run --rm -p 8000:8000 \
		--name watcher_dev \
		-v $(shell pwd):/watcher \
		-v /watcher/.venv watcher \
		sh -c "uv run -- uvicorn src.app:app --reload --host 0.0.0.0 --port 8000" && \
	docker logs watcher_dev --follow

docker-stop:
	docker stop watcher_dev || true
	docker rm watcher_dev || true

docker-clean:
	docker container prune -f
	docker images -f "dangling=true" -q | xargs -r docker rmi
	docker volume prune -f
	docker network prune -f

start:
	uv run uvicorn src.app:app --reload

format: lint
	uv run -- ruff format

lint:
	uv run -- ruff check --fix

test:
	uv run -- pytest -v --tb=short

add-migration:
	# Example: make add-migration msg="I am a message" 
	uv run -- alembic revision --rev-id $(shell date +%Y%m%d%H%M%S) --autogenerate -m "$(msg)"

trigger-migration:
	uv run -- alembic upgrade head