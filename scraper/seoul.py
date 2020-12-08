from datetime import datetime

import requests
from bs4 import BeautifulSoup

from db.models import Article
from scraper import ArticleScraper, ArticleConnectionError, ArticleParsingError


# Allow in robots.txt
BASE_URL = "https://www.seoul.co.kr"
URL = f"{BASE_URL}/news/newsList.php?section=seoul_allNews"


def get_full_link(partial_link):
    return f"{BASE_URL}{partial_link}"


class SeoulScraper(ArticleScraper):

    def get_press_name(self):
        return "서울신문"

    def get_articles(self):
        try:
            response = requests.get(URL)
        except Exception as err:
            raise ArticleConnectionError(f"{self.get_press_name()} scraper requests error") from err

        try:
            response.encoding = "euc-kr"
            soup = BeautifulSoup(response.text, "html.parser")
            articles_container = soup.find(id="articleListDiv")
            articles_container = articles_container.find_all("div", class_="tit lineclamp2")
            articles = [each.find("a") for each in articles_container]
            return [
                Article(
                    title=each["title"],
                    link=get_full_link(each["href"]),
                    timestamp=datetime.now()
                )
                for each in articles
            ]
        except Exception as err:
            raise ArticleParsingError(f"{self.get_press_name()} scraper parsing error") from err
