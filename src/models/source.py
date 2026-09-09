"""取得した情報源を表すモデルを定義する。"""

from pydantic import BaseModel


class MinimalSource(BaseModel):
    """取得した情報源を表す。"""

    text: str
    file_path: str
    first_character_index: int
    last_character_index: int
