from datetime import datetime

import requests
from bs4 import BeautifulSoup

from db.models import Article
from scraper import ArticleScraper, ArticleConnectionError, ArticleParsingError


# Allow in robots.txt
BASE_URL = "https://asiae.co.kr"
URL = f"{BASE_URL}/realtime/sokbo_left.htm"


def get_full_link(partial_link):
    return f"{BASE_URL}{partial_link}"


class AsiaeScraper(ArticleScraper):

    def get_press_name(self):
        return "아시아경제"

    def get_articles(self):
        try:
            response = requests.get(URL)
        except Exception as err:
            raise ArticleConnectionError(f"{self.get_press_name()} scraper requests error") from err

        try:
            response.encoding = "euc-kr"
            soup = BeautifulSoup(response.text, "html.parser")
            tags = soup.find_all("a")
            articles = [tag for tag in tags if tag.has_attr("title")]
            return [
                Article(title=each.text, link=get_full_link(each["href"]), timestamp=datetime.now())
                for each in articles
            ]
        except Exception as err:
            raise ArticleParsingError(f"{self.get_press_name()} scraper parsing error") from err
