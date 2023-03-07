from .protocols import Filter
from .states import GameState
from .types import Update


class MessageFilter(Filter):
    def filter(self, update: Update) -> bool:
        return update.message is not None and update.message.text is not None


class GroupFilter(Filter):
    def filter(self, update: Update) -> bool:
        return update.message.chat.type == "group"  # type: ignore


class OnChatJoinFilter(Filter):
    def filter(self, update: Update):
        return update.message.new_chat_member is not None  # type: ignore


class CommandFilter(Filter):
    def __init__(self, command: str) -> None:
        self._command = command

    def filter(self, update: Update):
        if (entities := update.message.entities) is not None:  # type: ignore # noqa
            if entities[-1].type == "bot_command":
                offset = entities[-1].offset
                length = entities[-1].length
                if (
                    update.message.text[offset : offset + length + 1]  # type: ignore # noqa
                    == self._command
                ):
                    return True
        return False


class CallbackQueryFilter(Filter):
    def __init__(self, data: str) -> None:
        self._data = data

    def filter(self, update: Update):
        return update.callback_query is not None


class StateFilter(Filter):
    def __init__(self, state: GameState) -> None:
        self._state = state

    def filter(self, update: Update):
        return (
            update.state is not None
            and update.state.value.filter_ == self._state.value.filter_
        )
