from typing import List, Optional, Union
from datetime import datetime
from threading import Lock

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.executors.pool import ThreadPoolExecutor

from .messenger import Messenger, MessengerError
from .scraper import Article, ArticleScraper, validate_scraper
from .press import validate_press_names, Press
from .keywords import Keyword, drop_duplicated_keywords
from .container import ArticleContainer, QueueContainer


class ScraperRunner:

    def __init__(
        self,
        messenger: Messenger,
        scrapers: Optional[List[ArticleScraper]] = None,
        press: Optional[List[Press]] = None,
        keywords: Optional[List[Keyword]] = None,
        article_container: Optional[ArticleContainer] = None,
    ):
        self.messenger = messenger
        self.scheduler = None
        self.scrapers = scrapers if scrapers else []
        self.press = press if press else []
        self.keywords = keywords if keywords else []
        self.article_container = article_container if article_container else QueueContainer()
        self.lock = Lock()

    def _get_scheduler(self):
        executors = {
            "default": ThreadPoolExecutor(len(self.scrapers)),
        }
        return BlockingScheduler(executors=executors)

    def _set_stop_signal_handler(self):
        # pylint: disable=import-outside-toplevel
        import signal
        signal.signal(signal.SIGINT, self.stop)

    def get_scraper_press_names(self) -> List[str]:
        return [each.get_press_name() for each in self.scrapers]

    def validate_messenger(self) -> None:
        try:
            self.messenger.send("Validation message from nscrap")
            print("[+] Send validation message from nscrap")
        except MessengerError as error:
            print(error)
            print("[+] Messenger went wrong, check messenger.send()")
            raise

    def add_press(self, press: Union[Press, List[Press]]) -> None:
        if not isinstance(press, list):
            self.press.append(press)
        else:
            self.press.extend(press)

    def add_keyword(self, keywords: Union[Keyword, List[Keyword]]) -> None:
        if not isinstance(keywords, list):
            self.keywords.append(keywords)
        else:
            self.keywords.extend(keywords)
        self.keywords = drop_duplicated_keywords(self.keywords)

    def add_scraper(self, scrapers: Union[ArticleScraper, List[ArticleScraper]]) -> None:
        if not isinstance(scrapers, list):
            self.scrapers.append(scrapers)
        else:
            self.scrapers.extend(scrapers)

    def send_article_message(self, article: Article) -> None:
        content = article.to_mesage_format()
        print(f"[+] Send message {content}")
        self.messenger.send(content)

    def is_contains_any_keyword(self, word) -> bool:
        return any([keyword.is_in(word) for keyword in self.keywords])

    def get_new_articles(self, scraped_articles: List[Article]) -> List[Article]:
        existing_article_titles = [each.title for each in self.article_container.get_all_articles()]
        if not scraped_articles:
            return []
        return list(filter(lambda x: x.title not in existing_article_titles, scraped_articles))

    def _scrap_articles(self, scraper: ArticleScraper) -> List[Article]:
        print(f"[+] Start {scraper.get_press_name()} scraper at {datetime.now():%Y-%m-%d %H:%M:%S}")
        return scraper.get_articles()

    def scrap(self, scraper: ArticleScraper) -> None:
        try:
            scraped_articles = self._scrap_articles(scraper)
            with self.lock:
                new_articles = self.get_new_articles(scraped_articles)
                self.article_container.add_articles(new_articles)
            for article in new_articles:
                print(f"[+] Scrap {article.to_mesage_format()}")
                if self.is_contains_any_keyword(article.title):
                    self.send_article_message(article)
        except MessengerError:
            # messenger api limit error
            print("[+] MessengerError occurred. Messenger api limit may have been exceeded")

    def print_settings(self) -> None:
        print(f"press: {self.press}")
        print(f"keywords: {[each.keyword for each in self.keywords]}")
        print(f"scrapers: {[each.get_press_name() for each in self.scrapers]}")

    def _add_scheduler_jobs(self):
        scraper_press_names = self.get_scraper_press_names()
        for each in self.press:
            if not each.active:
                continue
            index = scraper_press_names.index(each.press_name)
            scraper = self.scrapers[index]
            scraper_press_name = scraper.get_press_name()
            if not validate_scraper(scraper):
                print(f"[+] Inactive {scraper_press_name} scraper because an error has occurred")
                continue
            self.scheduler.add_job(
                self.scrap,
                "interval",
                args=[scraper],
                seconds=each.delay
            )

    def _start_scheduler(self):
        print("[+] Start nscrap")
        self.scheduler.start()

    def _stop_scheduler(self):
        print("[+] Stop nscrap")
        self.scheduler.shutdown()

    def start(self) -> None:
        validate_press_names(self.press, self.get_scraper_press_names())
        self.scheduler = self._get_scheduler()
        self.validate_messenger()
        self._set_stop_signal_handler()
        self._add_scheduler_jobs()
        self.print_settings()
        self._start_scheduler()

    def stop(self, sig, frame) -> None:
        # pylint: disable=unused-argument
        self._stop_scheduler()
