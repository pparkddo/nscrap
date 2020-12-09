import sys
import signal
from datetime import datetime
from typing import List

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.executors.pool import ThreadPoolExecutor

from db import Session
from db.models import Article
from db.utils import create_all_tables
from messenger import Messenger, MessengerError
from press import read_press, validate_press_names
from keywords import read_keywords, is_keyword_match
# pylint: disable=wrong-import-order
from settings import read_settings
from backup import dump, should_backup
from scraper import (
    ArticleScraper,
    ArticleConnectionError,
    ArticleParsingError,
    get_all_article_scrapers
)


def signal_handler(sig, frame):
    # pylint: disable=unused-argument
    print("[+] Stop nscrap")
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)


SETTINGS = read_settings()
KEYWORDS = read_keywords()
PRESS = read_press()
MESSENGER = Messenger()
SCRAPERS = get_all_article_scrapers()
SCRAPER_PRESS_NAMES = [each.get_press_name() for each in SCRAPERS]
validate_press_names(PRESS, SCRAPER_PRESS_NAMES)


def setup():
    create_all_tables()
    print("[+] Completely set Database")
    first_timestamp = Article.get_first_timestamp()
    if should_backup(first_timestamp, backup_period) or SETTINGS["force_reset_database"]:
        articles = Article.get_all_articles()
        dump(articles)
        print("[+] Backup(dump) existing database")
        Session.query(Article).delete()
        print("[+] Delete all existing articles")


def get_new_articles(scraped_articles):
    existing_articles = Article.get_all_articles()
    existing_article_titles = [each.title for each in existing_articles]
    return list(filter(lambda x: x.title not in existing_article_titles, scraped_articles))


def send_article_message(article: Article):
    content = article.to_mesage_format()
    print(f"[+] Send message {content}")
    MESSENGER.send(content)


def scrap_new_articles(scraper: ArticleScraper) -> List[Article]:
    # pylint: disable=redefined-outer-name
    print(f"[+] Start {scraper.get_press_name()} scraper at {datetime.now():%Y-%m-%d %H:%M:%S}")
    articles = scraper.get_articles()
    return get_new_articles(articles)


def add_new_articles(new_articles: List[Article]):
    Session.add_all(new_articles)


def scrap(scraper: ArticleScraper):
    # pylint: disable=redefined-outer-name
    new_articles = scrap_new_articles(scraper)
    add_new_articles(new_articles)
    for article in new_articles:
        print(f"[+] Scrap {article.to_mesage_format()}")
        if is_keyword_match(article.title, KEYWORDS):
            send_article_message(article)


def run_scrap(scraper: ArticleScraper):
    # pylint: disable=redefined-outer-name
    try:
        scrap(scraper)
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


def validate_messenger():
    try:
        MESSENGER.send("Validation message from nscrap")
        print("[+] Send validation message from nscrap")
    except MessengerError as error:
        print(error)
        print("[+] Messenger went wrong, check settings.json...?")
        raise


if __name__ == "__main__":
    try:
        setup()
        Session.commit()
    except:
        Session.rollback()
        raise
    finally:
        Session.close()

    validate_messenger()

    executors = {
        "default": ThreadPoolExecutor(len(SCRAPERS)),
    }
    scheduler = BlockingScheduler(executors=executors)

    for each in PRESS:
        if not each["active"]:
            continue
        index = SCRAPER_PRESS_NAMES.index(each["press_name"])
        scraper = SCRAPERS[index]
        if not validate_scraper(scraper):
            print(f"[+] Inactive {scraper.get_press_name()} scraper because an error has occurred")
            continue
        scheduler.add_job(run_scrap, "interval", args=[scraper], seconds=each["delay"])

    print("[+] Start nscrap")
    scheduler.start()
