"""生成された回答を表すモデルを定義する。"""

from pydantic import BaseModel

from .search import MinimalSearchResults


class MinimalAnswer(MinimalSearchResults):
    """1件の検索結果と生成された回答を表す。

    Attributes:
        answer: LLMが検索結果を根拠に生成した回答文。
    """

    answer: str


class StudentSearchResultsAndAnswer(BaseModel):
    """検索結果と生成された回答をまとめた提出データを表す。

    Attributes:
        search_results: 質問ごとの検索結果と生成済み回答。
        k: 各質問で取得した検索結果の最大件数。
    """

    search_results: list[MinimalAnswer]
    k: int
