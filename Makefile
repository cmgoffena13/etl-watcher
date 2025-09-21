dev-compose:
	docker compose up --build --remove-orphans

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
