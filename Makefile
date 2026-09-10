.PHONY: install run run-index run-search run-search-dataset run-answer \
	run-answer-dataset run-evaluate debug clean lint lint-strict

PYTHON := uv run python
DATASET_NAME ?= dataset_docs_public.json
UNANSWERED_DATASET_PATH ?= data/datasets/UnansweredQuestions/$(DATASET_NAME)
ANSWERED_DATASET_PATH ?= data/datasets/AnsweredQuestions/$(DATASET_NAME)
OUTPUT_DIRECTORY ?= data/output
STUDENT_RESULTS_PATH ?= $(OUTPUT_DIRECTORY)/$(DATASET_NAME)
K ?= 5

install:
	uv sync

run:
	$(PYTHON) -m src $(ARGS)

run-index:
	$(PYTHON) -m src index $(ARGS)

run-search:
	$(PYTHON) -m src search $(ARGS)

run-search-dataset:
	$(PYTHON) -m src search_dataset \
		$(UNANSWERED_DATASET_PATH) $(OUTPUT_DIRECTORY) --k=$(K)

run-answer:
	$(PYTHON) -m src answer $(ARGS)

run-answer-dataset:
	$(PYTHON) -m src answer_dataset \
		$(STUDENT_RESULTS_PATH) $(OUTPUT_DIRECTORY)

run-evaluate:
	$(PYTHON) -m src evaluate \
		$(STUDENT_RESULTS_PATH) $(ANSWERED_DATASET_PATH)

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
