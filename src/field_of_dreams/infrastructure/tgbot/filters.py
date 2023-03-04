from .protocols import Filter


class MessageFilter(Filter):
    @staticmethod
    def filter(update) -> bool:
        return update.get("message") and update["message"].get("text")


class GroupFilter(Filter):
    @staticmethod
    def filter(update) -> bool:
        message = update.get("message")
        return message and message["chat"]["type"] == "group"
