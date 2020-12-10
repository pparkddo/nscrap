from dataclasses import dataclass
from typing import List


@dataclass
class Press:

    press_name: str
    active: bool
    delay: int


def validate_press_names(press: List[Press], scraper_press_names: List[str]):
    press_names = [each.press_name for each in press]
    if set(scraper_press_names) > set(press_names):
        raise ValueError(f"Wrong press names: {press_names}")
