from abc import abstractmethod
from typing import List

from db.models import Article


class ArticleScraper:

    @abstractmethod
    def get_press_name(self) -> str:
        pass

    @abstractmethod
    def get_articles(self) -> List[Article]:
        pass


class ArticleConnectionError(Exception):
    pass


class ArticleParsingError(Exception):
    pass
