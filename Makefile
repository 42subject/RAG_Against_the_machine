.PHONY: install run run-index run-search run-search-dataset run-answer \
	run-answer-dataset run-evaluate debug clean lint lint-strict

PYTHON := uv run python

install:
	uv sync

run:
	$(PYTHON) -m src $(ARGS)

run-index:
	$(PYTHON) -m src index $(ARGS)

run-search:
	$(PYTHON) -m src search $(ARGS)

run-search-dataset:
	$(PYTHON) -m src search_dataset $(ARGS)

run-answer:
	$(PYTHON) -m src answer $(ARGS)

run-answer-dataset:
	$(PYTHON) -m src answer_dataset $(ARGS)

run-evaluate:
	$(PYTHON) -m src evaluate $(ARGS)

debug:
	$(PYTHON) -m pdb -m src $(ARGS)

clean:
	rm .venv

lint:
	uv run flake8 .
	uv run mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	uv run flake8 .
	uv run mypy . --strict
