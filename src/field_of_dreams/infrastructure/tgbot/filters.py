from .protocols import Filter
from .states import GameState
from .types import Update


class MessageFilter(Filter):
    def filter(self, update: Update) -> bool:
        return update.message is not None and update.message.text is not None


class GroupFilter(Filter):
    def filter(self, update: Update) -> bool:
        group_types = ("group", "supergroup")
        if msg := update.message:
            return msg.chat.type in group_types

        if call := update.callback_query:
            return call.chat is not None and call.chat.type in group_types

        return False


class CommandFilter(Filter):
    def __init__(self, command: str) -> None:
        self._command = command

    def filter(self, update: Update):
        if (entities := update.message.entities) is not None:  # type: ignore # noqa
            if entities[-1].type == "bot_command":
                offset = entities[-1].offset
                length = entities[-1].length
                if (
                    self._command in update.message.text[offset : offset + length + 1]  # type: ignore # noqa
                ):
                    return True
        return False


class CallbackQueryFilter(Filter):
    def __init__(self, data: str) -> None:
        self._data = data

    def filter(self, update: Update):
        return (
            update.callback_query is not None
            and update.callback_query.data == self._data
        )


class StateFilter(Filter):
    def __init__(self, state: GameState) -> None:
        self._state = state

    def filter(self, update: Update):
        return (
            update.state is not None
            and update.state.value.filter_ == self._state.value.filter_
        )


class OrCombinedFilter(Filter):
    def __init__(self, first: Filter, second: Filter) -> None:
        self._first = first
        self._second = second

    def filter(self, update: Update):
        return self._first.filter(update) or self._second.filter(update)
