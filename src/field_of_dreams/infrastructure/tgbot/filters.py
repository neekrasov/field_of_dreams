from .protocols import Filter


class MessageFilter(Filter):
    def filter(self, update) -> bool:
        return update.get("message") and update["message"].get("text")


class GroupFilter(Filter):
    def filter(self, update) -> bool:
        message = update.get("message")
        return message and message["chat"]["type"] == "group"


class OnChatJoinFilter(Filter):
    def filter(self, update: dict):
        return (
            update.get("message")
            and update["message"].get("new_chat_member") is not None
        )


class CommandFilter(Filter):
    def __init__(self, command: str) -> None:
        self._command = command

    def filter(self, update: dict):
        if (message := update.get("message")) is not None:
            if (entities := message.get("entities")) is not None:
                offset = entities[0]["offset"]
                length = entities[0]["length"]
                if (
                    message["text"][offset:offset + length + 1]
                    == self._command
                ):
                    return True
        return False


class CallbackQueryFilter(Filter):
    def __init__(self, data: str) -> None:
        self._data = data

    def filter(self, update: dict):
        if (call := update.get("callback_query")) is not None:
            if call.get("data") == self._data:
                return True
        return False
