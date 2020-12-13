from unittest import TestCase
from threading import Thread
from datetime import datetime

from nscrap.runner import ScraperRunner
from nscrap.messenger import Messenger
from nscrap.scraper import Article, ArticleScraper
from nscrap.keywords import Keyword


class NoneMesseneger(Messenger):

    def send(self, content):
        pass


class TestScraper(ArticleScraper):

    def get_press_name(self):
        return "test"

    def get_articles(self):
        return [Article("test", "test", datetime.now())]


class RunnerTestCase(TestCase):

    def setUp(self):
        self.messenger = NoneMesseneger()
        self.runner = ScraperRunner(self.messenger)

    def test_shared_article(self):
        number_of_threads = 100

        scraper = TestScraper()

        threads = [
            Thread(target=self.runner.scrap, args=(scraper,))
            for _ in range(number_of_threads)
        ]

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        self.assertEqual(len(self.runner.article_container.get_all_articles()), 1)

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
