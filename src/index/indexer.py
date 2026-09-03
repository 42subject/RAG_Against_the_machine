from src.input_models import IndexOptions
from src.config import RAW_DIRECTORY


def indexer(option: IndexOptions) -> None:
    for path in RAW_DIRECTORY.rglob("*"):
        if path.suffix == ".py":
            print(path)
        elif path.suffix in [".txt", ".md"]:
            print(path)
