import json
from typing import List

from db.models import Article


def _get_backup_filename():
    # pylint: disable=import-outside-toplevel
    from datetime import date
    return f"{date.today():%y%m%d}_nscrap_db.json"


def dump(articles: List[Article]):
    filename = _get_backup_filename()
    with open(filename, "w", encoding="utf8") as file:
        json.dump(articles, file, default=str, ensure_ascii=False)
