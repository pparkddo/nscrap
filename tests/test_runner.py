from unittest import TestCase
from threading import Thread
from datetime import datetime

from nscrap.runner import ScraperRunner
from nscrap.messenger import Messenger
from nscrap.scraper import Article


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

        articles = [Article(index, index, datetime.now()) for index in range(number_of_articles)]

        threads = [
            Thread(target=self.runner.add_new_articles, args=(articles,))
            for _ in range(number_of_threads)
        ]

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        self.assertEqual(
            len(self.runner.get_all_articles()),
            number_of_articles * number_of_threads
        )
