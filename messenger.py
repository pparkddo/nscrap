from telegram.bot import Bot

from settings import read_settings


SETTINGS = read_settings()
BOT_TOKEN = SETTINGS["bot_token"]


class MessengerError(Exception):
    pass


class Messenger:

    def __init__(self, token=None):
        # pylint: disable=unused-argument
        self.token = token if token is not None else BOT_TOKEN
        self.bot = Bot(self.token)

    def send(self, content: str, to: int) -> None:
        # pylint: disable=invalid-name
        try:
            self.bot.send_message(chat_id=to, text=content)
        except Exception as error:
            raise MessengerError("Unexpected error occurred at messenger send()") from error
