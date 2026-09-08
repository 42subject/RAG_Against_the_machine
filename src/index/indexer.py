import pickle

from src.input_models import IndexOptions
from src.config import (RAW_DIRECTORY, PROCESSED_DIRECTORY,
                        INDEX_FILE, CHUNK_FILE)

from .index_model import Index


def indexer(option: IndexOptions) -> None:
    PROCESSED_DIRECTORY.mkdir(parents=True, exist_ok=True)
    index = Index.from_directory(
        RAW_DIRECTORY,
        option.max_chunk_size,
    )

    RAW_DIRECTORY.mkdir(parents=True, exist_ok=True)
    with INDEX_FILE.open("wb") as file:
        pickle.dump(index.scores, file)
    with CHUNK_FILE.open("wb") as file:
        pickle.dump(index.chunks, file)
