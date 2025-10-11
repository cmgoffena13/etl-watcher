.PHONY: dev-compose dev-kube-stop format lint test add-migration trigger-migration load-test docs

dev-compose:
	docker compose up --build --remove-orphans

dev-compose-stop:
	docker compose down

dev-kube:
	docker build -t watcher:latest .
	docker-compose up -d postgres redis --remove-orphans
	sleep 10
	helm upgrade --install watcher ./watcher -f watcher/values-dev.yaml
	kubectl wait --for=condition=available --timeout=300s deployment/watcher
	kubectl port-forward service/watcher 8000:80

dev-kube-stop:
	helm uninstall watcher || true
	docker-compose down

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

load-test:
	uv run -- locust -f src/diagnostics/locustfile.py --host=http://localhost:8000 --users=1000 --spawn-rate=10

docs:
	uv run sphinx-build -b html docs docs/_build/html

docs-serve:
	uv run sphinx-autobuild docs docs/_build/html --open-browser --port 8080

docs-watch:
	uv run sphinx-autobuild docs docs/_build/html --watch src/ --port 8080