from pydantic import BaseModel, Field

from pathlib import Path
from enum import StrEnum


class InputCommand(StrEnum):
    """CLIで公開するコマンド名を定義する。"""
    INDEX = "index"
    SEARCH = "search"
    SEARCH_DATASET = "search_dataset"
    ANSWER = "answer"
    ANSWER_DATASET = "answer_dataset"
    EVALUATE = "evaluate"


class QueryOptions(BaseModel):
    """単一質問の検索・回答オプション。

    Attributes:
        question: 検索または回答する質問文。
        k: 取得するソースの最大件数。
    """

    question: str
    k: int = Field(ge=1)


class SearchDatasetOptions(BaseModel):
    """データセット検索オプション。

    Attributes:
        dataset_path: 質問データセットのJSONパス。
        save_directory: 検索結果を保存するディレクトリ。
        k: 質問ごとに取得するソースの最大件数。
    """

    dataset_path: Path
    save_directory: Path
    k: int = Field(ge=1)


class IndexOptions(BaseModel):
    """索引作成オプション。

    Attributes:
        max_chunk_size: 1チャンクに含める最大文字数。
    """

    max_chunk_size: int = Field(default=2000, gt=0, le=2000)


class AnswerDatasetOptions(BaseModel):
    """データセット回答生成オプション。

    Attributes:
        student_search_results_path: 検索結果JSONのパス。
        save_directory: 回答結果を保存するディレクトリ。
    """

    student_search_results_path: Path
    save_directory: Path


class EvaluateOptions(BaseModel):
    """検索結果の評価オプション。

    Attributes:
        student_search_results_path: 評価する検索結果JSONのパス。
        dataset_path: 正解付きデータセットJSONのパス。
    """

    student_search_results_path: Path
    dataset_path: Path
