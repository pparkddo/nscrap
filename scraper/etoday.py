from datetime import datetime

import requests
from bs4 import BeautifulSoup

from db.models import Article
from scraper import ArticleScraper, ArticleConnectionError, ArticleParsingError


# Allow in robots.txt
URL = "https://www.etoday.co.kr/news/flashnews/flash_list"


def get_article_link(article_id):
    return f"https://www.etoday.co.kr/news/flashnews/flash_view?idxno={article_id}"


def get_article_id(href):
    start = href.find("(") + 1
    end = href.find(")")
    return href[start:end]


class ETodayScraper(ArticleScraper):

    def get_press_name(self):
        return "이투데이"

    def get_articles(self):
        try:
            response = requests.get(URL)
        except Exception as err:
            raise ArticleConnectionError(f"{self.get_press_name()} scraper requests error") from err

        try:
            soup = BeautifulSoup(response.text, "html.parser")
            articles = [
                each.find("a")
                for each in soup.find_all("div", class_="flash_tab_txt t_reduce")
            ]
            return [
                Article(
                    title=each.text,
                    link=get_article_link(get_article_id(each["href"])),
                    timestamp=datetime.now()
                )
                for each in articles
            ]
        except Exception as err:
            raise ArticleParsingError(f"{self.get_press_name()} scraper parsing error") from err
