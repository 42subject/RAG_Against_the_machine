from src.input_models import IndexOptions
from src.config import RAW_DIRECTORY, PROCESSED_DIRECTORY

from .index_model import Index


def indexer(option: IndexOptions) -> None:
    PROCESSED_DIRECTORY.mkdir(parents=True, exist_ok=True)
    index = Index.from_directory(
        RAW_DIRECTORY,
        option.max_chunk_size,
    )
    print(index.scores)
