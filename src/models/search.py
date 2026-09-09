"""検索結果を表すモデルを定義する。"""

from pydantic import BaseModel

from .source import MinimalSource


class MinimalSearchResults(BaseModel):
    """1件の質問に対する検索結果を表す。"""

    question_id: str
    question: str
    retrieved_sources: list[MinimalSource]


class StudentSearchResults(BaseModel):
    """検索結果の提出データを表す。"""

    search_results: list[MinimalSearchResults]
    k: int
