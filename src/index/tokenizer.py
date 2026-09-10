"""自然言語とソースコードで共通利用するTokenizerを定義する。"""

import re
import unicodedata


TOKEN_PATTERN = re.compile(r"[A-Za-z0-9]+(?:_[A-Za-z0-9]+)*")
CAMEL_CASE_PATTERN = re.compile(
    r"[A-Z]+(?=[A-Z][a-z]|[0-9]|$)|[A-Z]?[a-z]+|[0-9]+"
)


def tokenize(text: str) -> list[str]:
    """文章と識別子をBM25で使用する検索語へ分割する。

    Args:
        text: 分割対象の文章またはソースコード。

    Returns:
        正規化した検索語。snake_caseやCamelCaseの識別子については、
        完全形に加えて構成語も含む。
    """
    normalized_text = unicodedata.normalize("NFKC", text)
    terms: list[str] = []
    for raw_token in TOKEN_PATTERN.findall(normalized_text):
        normalized_token = raw_token.casefold()
        terms.append(normalized_token)

        identifier_parts: list[str] = []
        for snake_part in raw_token.split("_"):
            camel_parts = CAMEL_CASE_PATTERN.findall(snake_part)
            if camel_parts:
                identifier_parts.extend(
                    part.casefold() for part in camel_parts
                )
            else:
                identifier_parts.append(snake_part.casefold())

        if len(identifier_parts) > 1:
            terms.extend(identifier_parts)

    return terms
