from datetime import datetime

import requests
from bs4 import BeautifulSoup

from db.models import Article
from scraper import ArticleScraper, ArticleConnectionError, ArticleParsingError


# Allow in robots.txt
BASE_URL = "http://news.heraldcorp.com/"
URL = f"{BASE_URL}list.php?ct=010000000000"


def get_full_link(partial_link):
    return f"{BASE_URL}{partial_link}"


class HeraldScraper(ArticleScraper):

    def get_press_name(self):
        return "헤럴드"

    def get_articles(self):
        try:
            response = requests.get(URL)
        except Exception as err:
            raise ArticleConnectionError(f"{self.get_press_name()} scraper requests error") from err

        try:
            soup = BeautifulSoup(response.text, "html.parser")
            titles = soup.find_all(class_="list_t1 ellipsis")
            links = [each.parent.parent["href"] for each in titles]
            return [
                Article(title=title.text, link=get_full_link(link), timestamp=datetime.now())
                for title, link in zip(titles, links)
            ]
        except Exception as err:
            raise ArticleParsingError(f"{self.get_press_name()} scraper parsing error") from err
