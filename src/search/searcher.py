
import pickle
from collections import defaultdict


from src.config import INDEX_FILE
from src.input_models import QueryOptions
from src.index import Index

from .search_models import MinimalSource


def searcher(option: QueryOptions) -> list[MinimalSource]:
    with INDEX_FILE.open("rb") as file:
        index = pickle.load(file)
    if not isinstance(index, Index):
        raise TypeError("Loaded object is not an Index")

    chunk_scores: dict[int, float] = defaultdict(float)
    for word in option.question.split():
        for chunk_id, score in index.scores[word]:
            chunk_scores[chunk_id] += score
    top_chunks = sorted(
        chunk_scores.items(),
        key=lambda item: item[1],
        reverse=True,
    )[:option.k]

    return [
        MinimalSource(
            file_path=index.chunks[chunk_id].file_path,
            first_character_index=(
                index.chunks[chunk_id].first_character_index
            ),
            last_character_index=(
                index.chunks[chunk_id].last_character_index
            ),
        )
        for chunk_id, _score in top_chunks
    ]
