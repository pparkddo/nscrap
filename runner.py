from typing import List, Optional
from datetime import datetime

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.executors.pool import ThreadPoolExecutor

from messenger import Messenger, MessengerError
from db import Session
from db.models import Article
from db.utils import create_all_tables
from scraper import ArticleScraper, ArticleConnectionError, ArticleParsingError
from backup import should_backup, dump
from press import validate_press_names, Press
from keywords import Keyword


def get_new_articles(scraped_articles: List[Article]):
    existing_articles = Article.get_all_articles()
    existing_article_titles = [each.title for each in existing_articles]
    return list(filter(lambda x: x.title not in existing_article_titles, scraped_articles))


def scrap_new_articles(scraper: ArticleScraper) -> List[Article]:
    # pylint: disable=redefined-outer-name
    print(f"[+] Start {scraper.get_press_name()} scraper at {datetime.now():%Y-%m-%d %H:%M:%S}")
    articles = scraper.get_articles()
    return get_new_articles(articles)


def add_new_articles(new_articles: List[Article]):
    Session.add_all(new_articles)


def validate_scraper(scraper: ArticleScraper) -> bool:
    # pylint: disable=redefined-outer-name
    scraper_press_name = scraper.get_press_name()
    try:
        new_articles = scrap_new_articles(scraper)
        add_new_articles(new_articles)
        print(f"[+] Test succeed: {scraper_press_name} passed test")
        return True
    except ArticleConnectionError:
        print(f"[+] Test failed: {scraper_press_name} scraper could not connect to web site")
        return False
    except ArticleParsingError:
        # pylint: disable=line-too-long
        print(f"[+] Test failed: {scraper_press_name} scraper could not parse web page. Web page may have been changed.")
        return False
    except Exception as error:  # pylint: disable=broad-except
        print(error)
        print(f"[+] Test failed: Unhandled error occurred in {scraper_press_name} scraper")
        return False
    finally:
        Session.rollback()
        Session.close()


class ScraperRunner:

    def __init__(
        self,
        messenger: Messenger,
        backup_period: int,
        force_reset_database: bool,
        scrapers: Optional[List[ArticleScraper]] = None,
        press: Optional[List[Press]] = None,
        keywords: Optional[List[Keyword]] = None,
    ):
        self.messenger = messenger
        self.backup_period = backup_period
        self.force_reset_database = force_reset_database
        self.scheduler = None
        self.scrapers = scrapers if scrapers else []
        self.press = press if press else []
        self.keywords = keywords if keywords else []

    def _get_scheduler(self):
        executors = {
            "default": ThreadPoolExecutor(len(self.scrapers)),
        }
        return BlockingScheduler(executors=executors)

    def get_scraper_press_names(self) -> List[str]:
        return [each.get_press_name() for each in self.scrapers]

    def setup(self) -> None:
        create_all_tables()
        print("[+] Completely set Database")
        first_timestamp = Article.get_first_timestamp()
        if should_backup(first_timestamp, self.backup_period) or self.force_reset_database:
            articles = Article.get_all_articles()
            dump(articles)
            print("[+] Backup(dump) existing database")
            Session.query(Article).delete()
            print("[+] Delete all existing articles")

    def validate_messenger(self) -> None:
        try:
            self.messenger.send("Validation message from nscrap")
            print("[+] Send validation message from nscrap")
        except MessengerError as error:
            print(error)
            print("[+] Messenger went wrong, check settings.json...?")
            raise

    def add_press(self, press: Press) -> None:
        self.press.append(press)

    def add_keyword(self, keyword: Keyword) -> None:
        self.keywords.append(keyword)

    def send_article_message(self, article: Article):
        content = article.to_mesage_format()
        print(f"[+] Send message {content}")
        self.messenger.send(content)

    def is_contains_any_keyword(self, word):
        return any([keyword.is_in(word) for keyword in self.keywords])

    def scrap(self, scraper: ArticleScraper):
        # pylint: disable=redefined-outer-name
        new_articles = scrap_new_articles(scraper)
        add_new_articles(new_articles)
        for article in new_articles:
            print(f"[+] Scrap {article.to_mesage_format()}")
            if self.is_contains_any_keyword(article.title):
                self.send_article_message(article)

    def run_scrap(self, scraper: ArticleScraper):
        # pylint: disable=redefined-outer-name
        try:
            self.scrap(scraper)
            Session.commit()
        except MessengerError as error:
            # messenger api limit error
            print("[+] MessengerError occurred. Messenger api limit may have been exceeded")
            print(error)
            Session.commit()
        except Exception:
            Session.rollback()
            raise
        finally:
            Session.close()

    def run(self):
        try:
            self.setup()
            Session.commit()
        except:
            Session.rollback()
            raise
        finally:
            Session.close()

        scraper_press_names = self.get_scraper_press_names()
        validate_press_names(self.press, scraper_press_names)

        self.scheduler = self._get_scheduler()
        self.validate_messenger()

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
                self.run_scrap,
                "interval",
                args=[scraper],
                seconds=each.delay
            )

        print("[+] Start nscrap")
        self.scheduler.start()
