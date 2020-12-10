from abc import abstractmethod

from telegram.bot import Bot


class MessengerError(Exception):
    pass


class Messenger:

    @abstractmethod
    def send(self, content: str) -> None:
        pass


class TelegramMessenger(Messenger):

    def __init__(self, token, chat_id):
        self.token = token
        self.chat_id = chat_id
        self.bot = Bot(self.token)

    def send(self, content: str) -> None:
        try:
            self.bot.send_message(chat_id=self.chat_id, text=content)
        except Exception as error:
            raise MessengerError("Unexpected error occurred at messenger send()") from error
