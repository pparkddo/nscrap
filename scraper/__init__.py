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


def get_all_article_scrapers() -> List[ArticleScraper]:
    return [each() for each in ArticleScraper.__subclasses__()]
