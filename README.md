# SETUP
1. Install `uv`
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```
2. Install python 3.12
```bash
uv python install 3.12
```
3. Check installation
```bash
uv python list
```
4. Sync python packages
```bash
uv sync
```
5. Add in pre-commits (you might need to run `source .venv/bin/activate` if your uv environment is not being recognized)
```bash
pre-commit install
pre-commit install --hook-type pre-push
```

## Documentation
The repo utilizes scalar for API documentation found at the `/scalar` route.


## Development
Utilize the `make start` command to launch locally. The `/scalar` endpoint makes it super easy to trigger other endpoints with arguments.
### Adding in a new table
1. Make sure to add the model to `src.database.models.__init__.py` so its part of SQLModel's metadata.
2. Generate the database migration utilizing the make command below
```
make add-migration msg="this is a message"
```
3. Trigger the migration
```
make trigger-migration
```

## Initial Setup Documentation (For my reference)
1. Had to initialize uv project
```bash
uv init
```
2. Had to initialize alembic
```bash
uv run -- alembic -t async migrations
```
3. Had to edit `script.py.mako` and `env.py` referencing: https://testdriven.io/blog/fastapi-sqlmodel/ in the alembic `migrations` folder.