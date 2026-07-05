.PHONY: setup ingest run docker-up docker-down test

setup:
	uv venv
	uv pip install -e .

ingest:
	uv run python -m src.infrastructure.parser.pdf_ingestor

run:
	uv run uvicorn src.presentation.api.main:app --reload

docker-up:
	docker-compose up --build

docker-down:
	docker-compose down

test-graph:
	uv run python test_graph.py

test:
	PYTHONPATH=. uv run pytest tests/ -v
