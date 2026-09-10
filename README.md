*This project has been created as part of the 42 curriculum by smiyata.*

# RAG Against the Machine

## Description

RAG Against the Machine is a local Retrieval-Augmented Generation (RAG)
system that answers questions about the vLLM source tree. It indexes Python,
Markdown, and text files, retrieves the most relevant source fragments with
BM25, and supplies those fragments to `Qwen/Qwen3-0.6B` so that an answer can
be generated from repository evidence instead of unsupported outside
knowledge.

The project also supports batch retrieval and answer generation with JSON
datasets. Retrieval quality can be measured with Recall@k by comparing the
returned file paths and character ranges with annotated sources.

## System Architecture

```text
data/raw/vllm-0.10.1
          |
          v
  file-specific chunking
  (.py / .md / .txt)
          |
          v
 BM25 inverted index -----> data/processed/index.pkl
          |
          v
 question -> tokenizer -> top-k source chunks
                              |
                 +------------+------------+
                 |                         |
                 v                         v
          retrieval JSON           grounded prompt
                                           |
                                           v
                                  Qwen/Qwen3-0.6B
                                           |
                                           v
                                      answer JSON
```

The main components are:

- `src/index`: reads the corpus, creates chunks, precomputes BM25 scores, and
  saves the index.
- `src/search`: tokenizes a query, accumulates BM25 scores for the question,
  and returns the top-k source locations.
- `src/answer`: formats retrieved text as model context and generates an
  answer using the local Qwen model.
- `src/evaluate`: calculates Recall@k from a ground-truth dataset.
- `src/models`: Pydantic models shared between pipeline stages.
- `src/__main__.py`: the Python Fire command-line interface.

## Chunking Strategy

Chunk size is configurable with `--max_chunk_size`, defaults to 2,000
characters, and cannot exceed 2,000 characters.

The indexer uses separate strategies according to file type:

- Python files are accumulated line by line and split before a top-level
  `class` declaration or when adding a line would exceed the size limit.
- Markdown files are accumulated line by line and split before headings or
  at the size limit.
- Text files are accumulated line by line and split at blank lines or at the
  size limit.
- A single line longer than the configured limit is divided into bounded
  pieces.

Every chunk retains its exact project-relative `file_path` and its original
one-based, inclusive `first_character_index` and `last_character_index`.

## Retrieval Method

The project uses BM25 lexical retrieval. During indexing, each token is mapped
to postings containing the chunk identifier and its BM25 contribution. Query
tokens are looked up directly in these postings, their scores are accumulated
per chunk, and chunks are sorted by descending total score.

Tokenization extracts alphanumeric terms and applies `casefold()` to make
matching case-insensitive.

The implementation uses the standard BM25 parameters `k1 = 1.5` and
`b = 0.75`.

## Requirements

- Python 3.12 or later
- [uv](https://docs.astral.sh/uv/)
- vLLM
- The datasets

## Instructions

Install the dependencies from the repository root:

```bash
make install
```

Build the index. The default maximum chunk size is 2,000 characters:

```bash
uv run python -m src index --max_chunk_size 2000
```

Search a single question:

```bash
uv run python -m src search \
  --question="What is PagedAttention?" \
  --k=5
```

Search all questions in a dataset:

```bash
uv run python -m src search_dataset \
  --dataset_path=data/datasets/UnansweredQuestions/dataset_docs_public.json \
  --save_directory=data/output/search_results/UnansweredQuestions \
  --k=5
```

Generate an answer for one question:

```bash
uv run python -m src answer \
  --question="What is PagedAttention?" \
  --k=5
```

Generate answers from saved search results:

```bash
uv run python -m src answer_dataset \
  --student_search_results_path=data/output/search_results/UnansweredQuestions/dataset_docs_public.json \
  --save_directory=data/output/search_results_and_answer/UnansweredQuestions
```

Run the project's local Recall@k evaluator:

```bash
uv run python -m src evaluate \
  --student_search_results_path=data/output/search_results/UnansweredQuestions/dataset_docs_public.json \
  --dataset_path=data/datasets/AnsweredQuestions/dataset_docs_public.json
```

```bash
make lint
```

Convenience targets are also available:

```bash
make run-docs
make run-code
make run-answer-docs
make run-answer-code
```

## Data Flow and Output

`search_dataset` reads a `RagDataset` JSON file and writes a
`StudentSearchResults` JSON file. Each result contains the original question
identifier, question text, and ranked sources. A source records its exact
path, character range, and the retrieved text used by the answer stage.

`answer_dataset` preserves those retrieval results and adds one generated
answer per question, producing a `StudentSearchResultsAndAnswer` JSON file.
Pydantic validates data exchanged between the stages.

## Performance Analysis

The assignment limits are:

- Index the complete corpus in at most five minutes.
- Retrieve answers for 200 questions in at most 90 seconds.
- Reach at least 80% Recall@5 on documentation questions.
- Reach at least 50% Recall@5 on code questions.

During local development, the case-sensitive BM25 implementation obtained
`0.78` Recall@5 on the 100 public documentation questions. A controlled local
comparison using case-insensitive tokenization obtained `0.83`.

## Design Decisions

- BM25 was selected because its document-length normalization minimizes the
  scoring differences caused by variable chunk lengths.
- Different chunking rules are used for source code and prose because their
  useful structural boundaries differ.

## Challenges Faced

### Tokenization for normalizing spelling variations

The original tokenizer used only `str.split()`. As a result, differences in
capitalization, such as `LLM` and `llm`, and surrounding punctuation caused
words with the same intended meaning to be treated as different tokens.
Applying the same `casefold()` normalization to both corpus text and questions
improved lexical matching without changing source text or character offsets.

## Resources

- [Qwen3-0.6B model card](https://huggingface.co/Qwen/Qwen3-0.6B)
- [Pydantic documentation](https://docs.pydantic.dev/)
- [Python Fire documentation](https://google.github.io/python-fire/)
- [tqdm documentation](https://tqdm.github.io/)

AI was used to review the assignment requirements, inspect implementation
contracts, compare retrieval improvements, and draft this documentation.
