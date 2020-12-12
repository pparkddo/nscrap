from unittest import TestCase
from threading import Thread
from datetime import datetime

from nscrap.runner import ScraperRunner
from nscrap.messenger import Messenger
from nscrap.scraper import Article
from nscrap.keywords import Keyword


class NoneMesseneger(Messenger):

    def send(self, content):
        pass


class RunnerTestCase(TestCase):

    def setUp(self):
        self.messenger = NoneMesseneger()
        self.runner = ScraperRunner(self.messenger)

    def test_shared_article(self):
        number_of_articles = 30
        number_of_threads = 30

        articles = [
            Article(str(index), str(index), datetime.now())
            for index in range(number_of_articles)
        ]

        threads = [
            Thread(target=self.runner.article_container.add_articles, args=(articles,))
            for _ in range(number_of_threads)
        ]

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        self.assertEqual(
            len(self.runner.article_container.get_all_articles()),
            number_of_articles * number_of_threads
        )

    def test_get_new_articles(self):
        existing_articles = [
            Article("1", "1", datetime.now()),
            Article("2", "2", datetime.now()),
            Article("3", "3", datetime.now()),
        ]
        new_articles = [
            Article("4", "4", datetime.now()),
            Article("5", "5", datetime.now()),
        ]
        scraped_articles = existing_articles + new_articles
        self.runner.article_container.add_articles(existing_articles)
        self.assertEqual(self.runner.get_new_articles(scraped_articles), new_articles)

    def test_is_contains_any_keyword(self):
        keywords = [
            Keyword("a"),
            Keyword("b"),
        ]
        self.runner.add_keyword(keywords)
        self.assertTrue(self.runner.is_contains_any_keyword("a"))
        self.assertTrue(self.runner.is_contains_any_keyword("A"))
        self.assertTrue(self.runner.is_contains_any_keyword("b"))
        self.assertFalse(self.runner.is_contains_any_keyword("c"))
