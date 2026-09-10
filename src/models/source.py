"""取得した情報源を表すモデルを定義する。"""

from pydantic import BaseModel


class MinimalSource(BaseModel):
    """情報源が存在するファイル上の位置を表す。

    Attributes:
        file_path: 情報源が含まれるファイルのパス。
        first_character_index: 情報源の開始文字位置。
        last_character_index: 情報源の終了文字位置。
    """

    file_path: str
    first_character_index: int
    last_character_index: int


class RetrievedSource(MinimalSource):
    """検索で取得した情報源の本文と位置を表す。

    Attributes:
        text: 情報源として取得した本文。
    """

    text: str
