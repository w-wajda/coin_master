.PONY: run
run:
	@python app/main.py

.PONY: migration
migration:
	@alembic revision --autogenerate -m "migration"

.PONY: migrate
migrate:
	@alembic upgrade head

.PONY: m-history
m-history:
	@alembic history

.PONY: m-down
m-down:
	@alembic downgrade -1

.PONY: test
test:
	@python -m pytest -v

.PONY: test-x
test-x:
	@python -m pytest -x -v

.PONY: coverage
coverage:
	@coverage run -m pytest
	@coverage report -m
	@coverage html
	@open htmlcov/index.html

.PONY: db
db:
	@docker exec --user postgres -it coins-db psql

.PONY: lint
lint:
	black .
	isort .
	flake8 .
	mypy .

