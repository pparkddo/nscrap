from datetime import datetime

import requests
from bs4 import BeautifulSoup

from db.models import Article
from scraper import ArticleScraper, ArticleConnectionError, ArticleParsingError


# Allow in robots.txt
URL = "https://www.yna.co.kr/news"
TITLE_CLASS_NAME = "tit-wrap"


def get_full_link(partial_link):
    return f"http:{partial_link}"


class YnaScraper(ArticleScraper):

    def get_press_name(self):
        return "연합뉴스"

    def get_articles(self):
        try:
            response = requests.get(URL)
        except Exception as err:
            raise ArticleConnectionError(f"{self.get_press_name()} scraper requests error") from err

        try:
            soup = BeautifulSoup(response.text, "html.parser")
            articles = soup.find_all("a", class_=TITLE_CLASS_NAME)
            return [
                Article(
                    title=each.find("strong").text,
                    link=get_full_link(each["href"]),
                    timestamp=datetime.now()
                )
                for each in articles
            ]
        except Exception as err:
            raise ArticleParsingError(f"{self.get_press_name()} scraper parsing error") from err
