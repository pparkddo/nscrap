from datetime import datetime

import requests
from bs4 import BeautifulSoup

from db.models import Article
from scraper import ArticleScraper, ArticleConnectionError, ArticleParsingError


# Allow in robots.txt
BASE_URL = "http://www.thebell.co.kr/free/content/"
URL = f"{BASE_URL}Article.asp?svccode=00"


def get_full_link(partial_link):
    return f"{BASE_URL}{partial_link}"


class TheBellScraper(ArticleScraper):

    def get_press_name(self):
        return "더벨"

    def get_articles(self):
        try:
            response = requests.get(URL)
        except Exception as err:
            raise ArticleConnectionError(f"{self.get_press_name()} scraper requests error") from err

        try:
            soup = BeautifulSoup(response.text, "html.parser")
            tags = soup.find_all("a")
            articles = [tag for tag in tags if tag.has_attr("title")]
            return [
                Article(
                    title=each.find("dt").text,
                    link=get_full_link(each["href"]),
                    timestamp=datetime.now()
                )
                for each in articles
            ]
        except Exception as err:
            raise ArticleParsingError(f"{self.get_press_name()} scraper parsing error") from err
