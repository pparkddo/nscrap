# nscrap
주기적으로 Scraper 를 실행하여 기사제목에 특정 키워드가 포함되면 Messenger 를 통해 알림을 발송합니다  

# Installation
```
pip install nscrap
```
Or
```
git clone https://github.com/pparkddo/nscrap.git
pip install -r requirements.txt
```

# Usage

```python
from datetime import datetime

import requests
from bs4 import BeautifulSoup

from nscrap.scraper import ArticleScraper, ArticleConnectionError, ArticleParsingError, Article
from nscrap.runner import ScraperRunner
from nscrap.messenger import TelegramMessenger
from nscrap.press import Press
from nscrap.keywords import Keyword


# Define Scraper
class HkScraper(ArticleScraper):

    def __init__(self):
        self.url = "https://www.hankyung.com/all-news/"

    def get_press_name(self):
        return "한국경제"

    def get_articles(self):
        response = self._get_response()
        parsed = self._parse_articles(response)
        return [
            Article(title=each.text, link=each["href"], timestamp=datetime.now())
            for each in parsed
        ]

    def _get_response(self):
        try:
            return requests.get(self.url)
        except Exception as err:
            raise ArticleConnectionError(f"{self.get_press_name()} scraper requests error") from err

    def _parse_articles(self, response):
        try:
            soup = BeautifulSoup(response.text, "html.parser")
            title_classes = soup.find_all(class_="tit")
            return [title_class.find("a") for title_class in title_classes]
        except Exception as err:
            raise ArticleParsingError(f"{self.get_press_name()} scraper parsing error") from err


# 'telegram-bot-token': 텔레그램에서 발행한 봇토큰을 입력
# 123456789: 메시지를 보낼 대화방 ID
messenger = TelegramMessenger("telegram-bot-token", 123456789)

press = [
    Press("한국경제", True, 30),
]

keywords = [
    Keyword("백신"),
    Keyword("정부"),
]

scrapers = [
    HkScraper(),
]

runner = ScraperRunner(messenger)
runner.add_press(press)
runner.add_keyword(keywords)
runner.add_scraper(scrapers)
runner.start()  # ctrl+c 를 입력하면 스케쥴러 종료
```
Output
```
[+] Send validation message from nscrap
[+] Test succeed: 한국경제 passed test
press: [Press(press_name='한국경제', active=True, delay=30)]
keywords: ['정부', '백신']
scrapers: ['한국경제']
[+] Start nscrap
[+] Start 한국경제 scraper at 2020-12-12 23:23:12
[+] Scrap 기사제목(https://www.hankyung.com/기사링크)
[+] Start 한국경제 scraper at 2020-12-12 23:23:42
...
[+] Stop nscrap
```

# Customization
* nscrap.scraper.ArticleScraper 를 상속하여 여러 scraper 구현 가능
* nscrap.messenger.Messenger 를 상속하여 다양한 메신저 구현가능
* nscrap.container.ArticleContainer 를 상속하여 ArticleRunner 내부에서 사용할 article 저장소 구현가능