"""質問データセットを表すモデルを定義する。"""

from pydantic import BaseModel

from .question import AnsweredQuestion, UnansweredQuestion


class RagDataset(BaseModel):
    """RAGで使用する質問データセットを表す。

    Attributes:
        rag_questions: 正解情報の有無を問わない質問の一覧。
    """

    rag_questions: list[AnsweredQuestion | UnansweredQuestion]
