install:
	pip install -e .

dev:
	pip install -r requirements.txt

test:
	pytest

lint:
	ruff check .

format:
	ruff format .

typecheck:
	mypy scholaros