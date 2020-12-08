from datetime import datetime

import requests
from bs4 import BeautifulSoup

from db.models import Article
from scraper import ArticleScraper, ArticleConnectionError, ArticleParsingError


# Allow in robots.txt
URL = "https://www.lawissue.co.kr/list.php?ct=g0200"
TITLE_CLASS_NAME = "tit"


class LawIssueScraper(ArticleScraper):

    def get_press_name(self):
        return "로이슈"

    def get_articles(self):
        try:
            response = requests.get(URL)
        except Exception as err:
            raise ArticleConnectionError(f"{self.get_press_name()} scraper requests error") from err

        try:
            soup = BeautifulSoup(response.text, "html.parser")
            articles = soup.find_all(class_=TITLE_CLASS_NAME)
            return [
                Article(title=each.text, link=each["href"], timestamp=datetime.now())
                for each in articles
            ]
        except Exception as err:
            raise ArticleParsingError(f"{self.get_press_name()} scraper parsing error") from err
