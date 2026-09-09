"""質問データセットを表すモデルを定義する。"""

from pydantic import BaseModel

from .question import AnsweredQuestion, UnansweredQuestion


class RagDataset(BaseModel):
    """RAGの質問データセットを表す。"""

    rag_questions: list[AnsweredQuestion | UnansweredQuestion]
