install:
	uv sync --frozen --compile-bytecode

build:
	docker build -t watcher . && docker images -f "dangling=true" -q | xargs docker rmi

dev-compose:
	docker compose up --build --remove-orphans

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
	uv run -- pytest -vv --tb=short

add-migration:
	# Example: make add-migration msg="I am a message" 
	uv run -- alembic revision --rev-id $(shell date +%Y%m%d%H%M%S) --autogenerate -m "$(msg)"

trigger-migration:
	uv run -- alembic upgrade head

test-db-speed:
	uv run -- python -m src.diagnostics.test_connection_speed

diagnose-db:
	uv run -- python -m src.diagnostics.diagnose_connection
	uv run -- python -m src.diagnostics.diagnose_schema

