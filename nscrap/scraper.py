from abc import abstractmethod
from typing import List, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Article:

    title: str
    link: str
    timestamp: datetime
    content: Optional[str] = None

    def to_mesage_format(self):
        return f"{self.title}({self.link})"


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


def validate_scraper(scraper: ArticleScraper) -> bool:
    scraper_press_name = scraper.get_press_name()
    try:
        scraper.get_articles()
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
