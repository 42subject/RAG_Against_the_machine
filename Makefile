.PHONY: install run run-docs run-code run-answer-docs run-answer-code \
	run-index run-search-dataset run-answer-dataset run-evaluate debug \
	clean lint lint-strict

PYTHON := uv run python
DOCS_DATASET_NAME := dataset_docs_public.json
CODE_DATASET_NAME := dataset_code_public.json
DATASET_NAME ?= $(DOCS_DATASET_NAME)
UNANSWERED_DATASET_DIRECTORY := data/datasets/UnansweredQuestions
ANSWERED_DATASET_DIRECTORY := data/datasets/AnsweredQuestions
OUTPUT_DIRECTORY ?= data/output
UNANSWERED_DATASET_PATH := $(UNANSWERED_DATASET_DIRECTORY)/$(DATASET_NAME)
ANSWERED_DATASET_PATH := $(ANSWERED_DATASET_DIRECTORY)/$(DATASET_NAME)
STUDENT_RESULTS_PATH := $(OUTPUT_DIRECTORY)/$(DATASET_NAME)
K ?= 5

install:
	uv sync

run: run-docs run-code

run-docs: run-index
	$(MAKE) run-search-dataset DATASET_NAME=$(DOCS_DATASET_NAME)
	$(MAKE) run-evaluate DATASET_NAME=$(DOCS_DATASET_NAME)

run-code: run-index
	$(MAKE) run-search-dataset DATASET_NAME=$(CODE_DATASET_NAME)
	$(MAKE) run-evaluate DATASET_NAME=$(CODE_DATASET_NAME)

run-answer-docs:
	$(MAKE) run-answer-dataset DATASET_NAME=$(DOCS_DATASET_NAME)

run-answer-code:
	$(MAKE) run-answer-dataset DATASET_NAME=$(CODE_DATASET_NAME)

run-index:
	$(PYTHON) -m src index

run-search-dataset:
	$(PYTHON) -m src search_dataset \
		$(UNANSWERED_DATASET_PATH) $(OUTPUT_DIRECTORY) --k=$(K)

run-answer-dataset:
	$(PYTHON) -m src answer_dataset \
		$(STUDENT_RESULTS_PATH) $(OUTPUT_DIRECTORY)

run-evaluate:
	$(PYTHON) -m src evaluate \
		$(STUDENT_RESULTS_PATH) $(ANSWERED_DATASET_PATH)

debug:
	$(PYTHON) -m pdb -m src $(ARGS)

clean:
	rm -rf .mypy_cache .pytest_cache .ruff_cache
	find src -type d -name __pycache__ -prune -exec rm -rf {} +
	find src -type f \( -name '*.pyc' -o -name '*.pyo' \) -delete

lint:
	uv run flake8 .
	uv run mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	uv run flake8 .
	uv run mypy . --strict
