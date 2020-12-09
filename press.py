from dataclasses import dataclass
from typing import List


SETTING_FILE_NAME = "press.json"
ENCODING = "utf-8"

FIELD_PRESS_NAME = "press_name"
FIELD_ACTIVE = "active"
FIELD_DELAY = "delay"
FIELDS = [FIELD_PRESS_NAME, FIELD_ACTIVE, FIELD_DELAY]


@dataclass
class Press:

    press_name: str
    active: bool
    delay: int


def read_press(filename=SETTING_FILE_NAME, encoding=ENCODING):
    # pylint: disable=import-outside-toplevel
    import json
    with open(filename, "r", encoding=encoding) as file:
        press = json.load(file)
    _validate_press(press)
    return press


def _validate_press(press):
    for each in press:
        if set(each) != set(FIELDS):
            raise ValueError(f"Wrong press: {each}")


def validate_press_names(press: List[Press], scraper_press_names: List[str]):
    press_names = [each.press_name for each in press]
    if set(press_names) > set(scraper_press_names):
        raise ValueError(f"Wrong press names: {press_names}")
