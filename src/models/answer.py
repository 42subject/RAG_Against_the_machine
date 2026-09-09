"""生成された回答を表すモデルを定義する。"""

from pydantic import BaseModel

from .search import MinimalSearchResults


class MinimalAnswer(MinimalSearchResults):
    """1件の検索結果と生成された回答を表す。"""

    answer: str


class StudentSearchResultsAndAnswer(BaseModel):
    """検索結果と回答を含む提出データを表す。"""

    search_results: list[MinimalAnswer]
    k: int
