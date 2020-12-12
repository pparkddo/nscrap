from abc import abstractmethod
from typing import List

from .scraper import Article


class ArticleContainer:

    @abstractmethod
    def get_all_articles(self) -> List[Article]:
        pass

    @abstractmethod
    def add_articles(self, articles: List[Article]) -> None:
        pass


class QueueContainer(ArticleContainer):

    def __init__(self):
        # pylint: disable=import-outside-toplevel
        from queue import Queue
        self._article_container = Queue()

    def get_all_articles(self):
        return list(self._article_container.queue)

    def add_articles(self, articles):
        for article in articles:
            self._article_container.put(article)
