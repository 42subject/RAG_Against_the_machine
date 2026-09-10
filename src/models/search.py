"""検索結果を表すモデルを定義する。"""

from pydantic import BaseModel

from .source import RetrievedSource


class MinimalSearchResults(BaseModel):
    """1件の質問に対する検索結果を表す。

    Attributes:
        question_id: 検索対象の質問を一意に識別するID。
        question: 検索に使用した質問文。
        retrieved_sources: 検索によって取得した情報源。
    """

    question_id: str
    question: str
    retrieved_sources: list[RetrievedSource]


class StudentSearchResults(BaseModel):
    """質問ごとの検索結果をまとめた提出データを表す。

    Attributes:
        search_results: 質問ごとの検索結果。
        k: 各質問で取得する検索結果の最大件数。
    """

    search_results: list[MinimalSearchResults]
    k: int
