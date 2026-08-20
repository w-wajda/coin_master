.PONY: run
run:
	@uv run python app/main.py

.PONY: migration
migration:
	@uv run alembic revision --autogenerate -m "migration"

.PONY: migrate
migrate:
	@uv run alembic upgrade head

.PONY: m-history
m-history:
	@uv run alembic history

.PONY: m-down
m-down:
	@uv run alembic downgrade -1

.PONY: test
test:
	@uv run pytest -v

.PONY: test-x
test-x:
	@uv run pytest -x -v

.PONY: coverage
coverage:
	@uv run coverage run -m pytest
	@uv run coverage report -m
	@uv run coverage html
	@open htmlcov/index.html

.PONY: db
db:
	@docker exec --user postgres -it coins-db psql

.PONY: lint
lint:
	uv run black .
	uv run isort .
	uv run flake8 .
	uv run mypy .
