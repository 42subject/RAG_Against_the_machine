"""質問を表すモデルを定義する。"""

import uuid

from pydantic import BaseModel, Field

from .source import MinimalSource


class UnansweredQuestion(BaseModel):
    """回答が付与されていない質問を表す。"""

    question_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    question: str


class AnsweredQuestion(UnansweredQuestion):
    """正解の情報源と回答が付与された質問を表す。"""

    sources: list[MinimalSource]
    answer: str
