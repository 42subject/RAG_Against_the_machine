"""回答前後の質問を表すモデルを定義する。"""

import uuid

from pydantic import BaseModel, Field

from .source import MinimalSource


class UnansweredQuestion(BaseModel):
    """回答が付与されていない質問を表す。

    Attributes:
        question_id: 質問を一意に識別するID。省略時はUUIDを生成する。
        question: 質問文。
    """

    question_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    question: str


class AnsweredQuestion(UnansweredQuestion):
    """正解の情報源と回答が付与された質問を表す。

    Attributes:
        sources: 回答の根拠となる正解の情報源。
        answer: データセットに収録された正解の回答文。
    """

    sources: list[MinimalSource]
    answer: str
