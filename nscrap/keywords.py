from typing import List


class Keyword:

    def __init__(self, keyword: str):
        self.keyword = _sanitize(keyword)

    def is_in(self, word: str) -> bool:
        return self.keyword in word.upper()


def _sanitize(keyword):
    if not keyword:
        raise ValueError("Keyword can not be empty")
    return keyword.strip().upper()


def drop_duplicated_keywords(keywords: List[Keyword]):
    return list(set(keywords))
