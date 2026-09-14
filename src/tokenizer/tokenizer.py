import re


WORD_PATTERN = re.compile(r"[A-Za-z0-9]+")
STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "do",
    "does",
    "for",
    "from",
    "how",
    "in",
    "is",
    "it",
    "of",
    "on",
    "or",
    "the",
    "to",
    "what",
    "when",
    "where",
    "which",
    "who",
    "why",
    "with",
}


def tokenizer(text: str) -> list[str]:
    """英文とコードを検索用トークンへ分割する。

    Args:
        text: 分割対象の本文または質問文。

    Returns:
        一般的な質問語を除いた小文字の英数字トークン。
    """
    return [
        token
        for token in WORD_PATTERN.findall(text.casefold())
        if token not in STOPWORDS
    ]
