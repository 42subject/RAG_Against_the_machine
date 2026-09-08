from pydantic import BaseModel, Field

from pathlib import Path
from enum import StrEnum


class InputCommand(StrEnum):
    INDEX = "index"
    SEARCH = "search"
    SEARCH_DATASET = "search_dataset"
    ANSWER = "answer"
    ANSWER_DATASET = "answer_dataset"
    EVALUATE = "evaluate"


class QueryOptions(BaseModel):
    """クエリ作成オプション"""

    question: str
    k: int = Field(ge=1)


class SearchDatasetOptions(BaseModel):
    """サーチデータセット作成オプション"""

    dataset_path: Path
    save_directory: Path
    k: int = Field(ge=1)


class IndexOptions(BaseModel):
    """インデックス作成オプション"""

    max_chunk_size: int = Field(default=2000, gt=0, le=2000)


class AnswerDatasetOptions(BaseModel):
    """アンサーデータセット作成オプション"""

    student_search_results_path: Path
    save_directory: Path


class EvaluateOptions(BaseModel):
    """evaluateオプション"""

    student_search_results_path: Path
    dataset_path: Path
