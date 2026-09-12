.PHONY: install run run-docs run-code run-answer-docs run-answer-code \
	run-evaluate-docs run-evaluate-code run-search-docs run-search-code \
	run-index debug \
	clean lint lint-strict

PYTHON := uv run python
DOCS_DATASET_NAME := dataset_docs_public.json
CODE_DATASET_NAME := dataset_code_public.json
UNANSWERED_DATASET_DIRECTORY := data/datasets/UnansweredQuestions
ANSWERED_DATASET_DIRECTORY := data/datasets/AnsweredQuestions
OUTPUT_DIRECTORY ?= data/output
DATASET_SCOPE ?= UnansweredQuestions
SEARCH_RESULTS_DIRECTORY := $(OUTPUT_DIRECTORY)/search_results/$(DATASET_SCOPE)
ANSWER_RESULTS_DIRECTORY := $(OUTPUT_DIRECTORY)/search_results_and_answer/$(DATASET_SCOPE)
K ?= 5

install:
	uv sync

run: run-docs run-code

run-docs: run-evaluate-docs

run-code: run-evaluate-code

run-search-docs run-evaluate-docs run-answer-docs: \
	DATASET_NAME := $(DOCS_DATASET_NAME)
run-search-code run-evaluate-code run-answer-code: \
	DATASET_NAME := $(CODE_DATASET_NAME)

run-search-docs run-search-code: run-index
	$(PYTHON) -m src search_dataset \
		$(UNANSWERED_DATASET_DIRECTORY)/$(DATASET_NAME) \
		$(SEARCH_RESULTS_DIRECTORY) --k=$(K)

run-evaluate-docs: run-search-docs

run-evaluate-code: run-search-code

run-evaluate-docs run-evaluate-code:
	$(PYTHON) -m src evaluate \
		$(SEARCH_RESULTS_DIRECTORY)/$(DATASET_NAME) \
		$(ANSWERED_DATASET_DIRECTORY)/$(DATASET_NAME)

run-answer-docs: run-search-docs

run-answer-code: run-search-code

run-answer-docs run-answer-code:
	$(PYTHON) -m src answer_dataset \
		$(SEARCH_RESULTS_DIRECTORY)/$(DATASET_NAME) \
		$(ANSWER_RESULTS_DIRECTORY)

run-index:
	$(PYTHON) -m src index

debug:
	$(PYTHON) -m pdb -m src $(ARGS)

clean:
	rm -rf .mypy_cache .pytest_cache
	find src -type d -name __pycache__ -prune -exec rm -rf {} +

fclean: clean
	rm -rf .venv

lint:
	uv run flake8 .
	uv run mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	uv run flake8 .
	uv run mypy . --strict
