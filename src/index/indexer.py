import pickle

from src.input_models import IndexOptions
from src.config import INDEX_FILE, PROCESSED_DIRECTORY, RAW_DIRECTORY

from .index_model import Index


def indexer(option: IndexOptions) -> None:
    PROCESSED_DIRECTORY.mkdir(parents=True, exist_ok=True)
    index = Index.from_directory(
        RAW_DIRECTORY,
        option.max_chunk_size,
    )

    with INDEX_FILE.open("wb") as file:
        pickle.dump(index, file)
