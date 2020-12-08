from datetime import datetime

import requests
from bs4 import BeautifulSoup

from db.models import Article
from scraper import ArticleScraper, ArticleConnectionError, ArticleParsingError


# Allow in robots.txt
BASE_URL = "https://dealsite.co.kr"
URL = f"{BASE_URL}/categories/9"
TITLE_CLASS_NAME = "dyn std"


def get_full_link(partial_link):
    return f"{BASE_URL}{partial_link}"


class DealSiteScraper(ArticleScraper):

    def get_press_name(self):
        return "딜사이트"

    def get_articles(self):
        try:
            response = requests.get(URL)
        except Exception as err:
            raise ArticleConnectionError(f"{self.get_press_name()} scraper requests error") from err

        try:
            soup = BeautifulSoup(response.text, "html.parser")
            articles = soup.find_all(class_=TITLE_CLASS_NAME)
            return [
                Article(title=each.text, link=get_full_link(each["href"]), timestamp=datetime.now())
                for each in articles
            ]
        except Exception as err:
            raise ArticleParsingError(f"{self.get_press_name()} scraper parsing error") from err
