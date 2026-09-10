from tqdm import tqdm

import pickle
from collections import defaultdict

from src.config import INDEX_FILE
from src.input_models import QueryOptions, SearchDatasetOptions
from src.index import Index
from src.models import (
    MinimalSearchResults,
    RetrievedSource,
    RagDataset,
    StudentSearchResults,
)
from src.tokenizer import tokenizer


def _get_index() -> Index:
    with INDEX_FILE.open("rb") as file:
        index = pickle.load(file)
    if not isinstance(index, Index):
        raise TypeError("Loaded object is not an Index")
    return index


def _search(
    index: Index,
    question: str,
    k: int,
) -> list[RetrievedSource]:
    chunk_scores: dict[int, float] = defaultdict(float)
    for word in tokenizer(question):
        for chunk_id, score in index.scores[word]:
            chunk_scores[chunk_id] += score
    top_chunks = sorted(
        chunk_scores.items(),
        key=lambda item: item[1],
        reverse=True,
    )[:k]

    return [
        RetrievedSource(
            text=index.chunks[chunk_id].text,
            file_path=index.chunks[chunk_id].file_path,
            first_character_index=(
                index.chunks[chunk_id].first_character_index
            ),
            last_character_index=(
                index.chunks[chunk_id].last_character_index
            ),
        )
        for chunk_id, _ in top_chunks
    ]


def searcher(option: QueryOptions) -> list[RetrievedSource]:
    return _search(
        _get_index(),
        option.question,
        option.k,
    )


def dataset_searcher(options: SearchDatasetOptions) -> None:
    with options.dataset_path.open("r", encoding="UTF-8") as file:
        dataset = RagDataset.model_validate_json(file.read())

    search_results: list[MinimalSearchResults] = []
    index = _get_index()

    for unanswered in tqdm(
        dataset.rag_questions,
        desc="Searching",
        unit="searched"
    ):
        question, question_id = unanswered.question, unanswered.question_id

        sources = _search(
            index,
            question,
            options.k,
        )
        search_results.append(MinimalSearchResults(
            question_id=question_id,
            question=question,
            retrieved_sources=sources
        ))

    student_search_results = StudentSearchResults(
        search_results=search_results,
        k=options.k,
    )

    options.save_directory.mkdir(parents=True, exist_ok=True)
    output_path = options.save_directory / options.dataset_path.name

    with output_path.open("w", encoding="UTF-8") as file:
        file.write(student_search_results.model_dump_json(indent=2))
