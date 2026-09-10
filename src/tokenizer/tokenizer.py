import re


def tokenizer(text: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9]+", text.casefold())
