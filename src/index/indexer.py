import pickle

from src.input_models import IndexOptions
from src.config import INDEX_FILE, PROCESSED_DIRECTORY, RAW_DIRECTORY

from .index_model import Index


def indexer(option: IndexOptions) -> None:
    """rawディレクトリから索引を構築して永続化する。

    Args:
        option: チャンク最大文字数を含む索引作成オプション。

    Raises:
        OSError: 入力の読み込みまたは索引の保存に失敗した場合。
        RuntimeError: 索引を構築できない場合。
    """
    PROCESSED_DIRECTORY.mkdir(parents=True, exist_ok=True)
    index = Index.from_directory(
        RAW_DIRECTORY,
        option.max_chunk_size,
    )

    with INDEX_FILE.open("wb") as file:
        pickle.dump(index, file)
