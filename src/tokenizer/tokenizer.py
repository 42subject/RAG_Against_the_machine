import re


def tokenizer(text: str) -> list[str]:
    """英文とコードを英数字の小文字化済みトークンへ分割する。

    Args:
        text: 分割対象の本文または質問文。

    Returns:
        出現順に並んだ英数字トークン。
    """
    return re.findall(r"[A-Za-z0-9]+", text.casefold())
