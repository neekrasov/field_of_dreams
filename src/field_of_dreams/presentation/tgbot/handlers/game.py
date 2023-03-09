import logging
from datetime import timedelta

from field_of_dreams.core.entities.chat import ChatID
from field_of_dreams.core.entities.user import UserID
from field_of_dreams.core.entities.player import Player
from field_of_dreams.infrastructure.tgbot import (
    filters,
    types,
    protocols,
    states,
)
from field_of_dreams.core.common import (
    ApplicationException,
    Mediator,
    QueueAccessError,
    GameOver,
)
from field_of_dreams.core.handlers.create_game import CreateGameCommand
from field_of_dreams.core.handlers.add_player import AddPlayerCommand
from field_of_dreams.core.handlers.start_game import StartGameCommand
from field_of_dreams.core.handlers.letter_turn import LetterTurnCommand
from field_of_dreams.core.handlers.word_turn import WordTurnCommand
from field_of_dreams.core.handlers.get_current_player import (
    GetCurrentPlayerCommand,
)
from field_of_dreams.core.handlers.check_user_queue import (
    CheckUserQueueCommand,
)
from field_of_dreams.core.handlers.idle_turn import IdleTurnCommand
from field_of_dreams.config import Settings
from services.timer import timer

logger = logging.getLogger()


async def create_game(
    update: types.Update,
    bot: protocols.Bot,
    mediator: Mediator,
    settings: Settings,
):
    logger.info("Create game")
    chat_id = update.message.chat.id  # type: ignore
    if bot.get_state(chat_id) not in (states.GameState.FINISHED, None):
        bot.set_state(chat_id, states.GameState.PLUG)
        return

    await mediator.send(
        CreateGameCommand(
            UserID(update.message.from_user.id),  # type: ignore
            update.message.from_user.username,  # type: ignore
            ChatID(chat_id),
            timedelta(seconds=settings.bot.max_turn_time),
        )
    )
    await bot.send_message(
        chat_id,
        text=" ".join(
            [
                "Начинаем сбор игроков.",
                "Чтобы присоединится к игре нажмите на кнопку.",
            ]
        ),
        reply_markup={
            "inline_keyboard": [
                [{"text": "Присоединиться", "callback_data": "join"}],
            ]
        },
    )
    bot.set_state(chat_id, states.GameState.PREPARING)
    update.message.entities = None  # type: ignore
    await bot.handle_update(update)


async def wait_players(
    update: types.Update,
    bot: protocols.Bot,
    mediator: Mediator,
    settings: Settings,
):
    logger.info("Wait players")
    chat_id = update.message.chat.id  # type: ignore
    state = bot.get_state(chat_id)
    if state == states.GameState.PREPARING:
        bot.set_state(chat_id, states.GameState.PREPARED)
    else:
        return

    task = timer(
        settings.bot.players_waiting_time,
        bot,
        chat_id,
        expired_text="Сбор игроков закончен.",
    )
    await task
    bot.set_state(chat_id, states.GameState.STARTED)
    await bot.handle_update(update)


async def join_to_game(
    update: types.Update,
    bot: protocols.Bot,
    mediator: Mediator,
):
    logger.info("Join to game")
    await mediator.send(
        AddPlayerCommand(
            ChatID(update.callback_query.message.chat.id),  # type: ignore
            UserID(update.callback_query.from_user.id),  # type: ignore
            update.callback_query.from_user.username,  # type: ignore
        ),
    )
    await bot.answer_callback_query(
        update.callback_query.id, "Вы присоединились к игре."  # type: ignore
    )


async def start_game(
    update: types.Update,
    bot: protocols.Bot,
    mediator: Mediator,
):
    logger.info("Start game")
    chat_id = update.message.chat.id  # type: ignore
    try:
        await mediator.send(StartGameCommand(ChatID(chat_id)))
        bot.set_state(chat_id, states.GameState.PLAYER_CHOICE)
        await bot.handle_update(update)
    except ApplicationException as e:
        bot.set_state(chat_id, states.GameState.FINISHED)
        raise e


async def player_choice(
    update: types.Update,
    bot: protocols.Bot,
    mediator: Mediator,
    settings: Settings,
):
    logger.info("Player choice")
    if update.message:
        chat_id = update.message.chat.id  # type: ignore
    else:
        chat_id = update.callback_query.message.chat.id  # type: ignore

    current_player: Player = await mediator.send(
        GetCurrentPlayerCommand(ChatID(chat_id))
    )

    await bot.send_message(
        chat_id,
        f"@{current_player.get_username()} что вы будете угадывать?",
        reply_markup={
            "inline_keyboard": [
                [
                    {"text": "Букву", "callback_data": "letter"},
                    {"text": "Слово", "callback_data": "word"},
                ],
                [{"text": "Пропустить ход", "callback_data": "skip"}],
            ]
        },
    )
    task = timer(
        settings.bot.max_turn_time,
        bot,
        chat_id,
        text=("Ожидание хода игрока... \n" "Время хода (в секундах): {}"),
        expired_text=("Истёк срок ожидания ответа от пользователя"),
    )
    state = states.GameState.WAIT_PLAYER_CHOICE
    state.value.set_data({"task": task})
    bot.set_state(chat_id, state)
    await task
    if not task.cancelled():
        await mediator.send(
            IdleTurnCommand(ChatID(chat_id), current_player.user_id)
        )
        state = states.GameState.PLAYER_CHOICE
        state.value.set_data({"task": task})
        bot.set_state(chat_id, state)
        await bot.handle_update(update)


async def skip_turn(
    update: types.Update,
    bot: protocols.Bot,
    mediator: Mediator,
):
    logger.info("Skip Turn")
    user_id = update.callback_query.from_user.id  # type: ignore
    chat_id = update.callback_query.message.chat.id  # type: ignore
    callback_id = update.callback_query.id  # type: ignore
    state = bot.get_state(chat_id)
    task = state.value.data.get("task")

    if task.done() or task.cancelled():
        await bot.answer_callback_query(
            update.callback_query.id, "Время выбора закончилось"  # type: ignore # noqa
        )
        return

    try:
        await mediator.send(
            CheckUserQueueCommand(ChatID(chat_id), UserID(user_id))
        )
    except QueueAccessError as e:
        await bot.answer_callback_query(update.callback_query.id, e.message)  # type: ignore # noqa
        return
    task.cancel()

    await bot.answer_callback_query(
        callback_id, "Ваш ход был принят.", show_alert=False
    )
    current_player: Player = await mediator.send(
        GetCurrentPlayerCommand(ChatID(chat_id))
    )
    await mediator.send(
        IdleTurnCommand(ChatID(chat_id), current_player.user_id)
    )
    await bot.send_message(
        chat_id, f"@{current_player.get_username()} решил пропустить ход."
    )
    bot.set_state(chat_id, states.GameState.PLAYER_CHOICE)
    await bot.handle_update(update)


async def player_turn(
    update: types.Update,
    bot: protocols.Bot,
    mediator: Mediator,
    settings: Settings,
):
    logger.info("Turning letter")
    chat_id = update.callback_query.message.chat.id  # type: ignore
    user_id = update.callback_query.from_user.id  # type: ignore
    username = update.callback_query.from_user.username  # type: ignore
    state = bot.get_state(chat_id)
    task = state.value.data.get("task")

    if task.done() or task.cancelled():
        await bot.answer_callback_query(
            update.callback_query.id, "Время выбора закончилось"  # type: ignore # noqa
        )
        return

    try:
        await mediator.send(
            CheckUserQueueCommand(ChatID(chat_id), UserID(user_id))
        )
        task.cancel()
    except QueueAccessError as e:
        await bot.answer_callback_query(update.callback_query.id, e.message)  # type: ignore # noqa
        return

    await bot.answer_callback_query(update.callback_query.id, "Ваш ход был принят.", show_alert=False)  # type: ignore # noqa

    task = timer(
        settings.bot.max_turn_time,
        bot,
        chat_id,
        text=(f"Ожидание хода игрока @{username}... \n" "Осталось секунд: {}"),
        expired_text=("Истёк срок ожидания ответа от пользователя"),
    )
    if update.callback_query.data == "letter":  # type: ignore
        state = states.GameState.PLAYER_LETTER_TURN
    else:
        state = states.GameState.PLAYER_WORD_TURN

    state.value.set_data({"user_id": user_id, "task": task})
    bot.set_state(chat_id, state)


async def player_word_turn(
    update: types.Update,
    bot: protocols.Bot,
    mediator: Mediator,
    settings: Settings,
):
    chat_id = update.message.chat.id  # type: ignore
    user_id = update.message.from_user.id  # type: ignore
    state = bot.get_state(chat_id)
    user_id_from_state = state.value.data.get("user_id")
    task = state.value.data.get("task")

    if user_id_from_state != user_id or task.done():
        return

    task.cancel()
    text = update.message.text.lower().strip()  # type: ignore
    if len(text) == 0:
        await mediator.send(IdleTurnCommand(ChatID(chat_id), UserID(user_id)))
        bot.set_state(chat_id, states.GameState.PLAYER_CHOICE)
        await bot.handle_update(update)

    try:
        await mediator.send(
            WordTurnCommand(
                ChatID(chat_id),
                UserID(user_id),
                text,
                settings.bot.random_score_from,
                settings.bot.random_score_to,
            )
        )
        bot.set_state(chat_id, states.GameState.PLAYER_CHOICE)
        await bot.handle_update(update)
    except GameOver as e:
        await bot.send_message(chat_id, e.message)
        bot.set_state(chat_id, states.GameState.FINISHED)


async def player_letter_turn(
    update: types.Update,
    bot: protocols.Bot,
    mediator: Mediator,
    settings: Settings,
):
    chat_id = update.message.chat.id  # type: ignore
    user_id = update.message.from_user.id  # type: ignore
    state = bot.get_state(chat_id)
    user_id_from_state = state.value.data.get("user_id")
    task = state.value.data.get("task")

    if user_id_from_state != user_id or task.done():
        return

    task.cancel()
    text = update.message.text.lower().strip()  # type: ignore
    err = False
    if len(text) == 0:
        err = True
    elif len(text) > 1:
        err = True
        await bot.send_message(
            chat_id,
            (
                "Длина ответа при выборе буквы не может превышать 1 символ. \n"
                "Правила игры - /help"
            ),
        )

    if err:
        await mediator.send(IdleTurnCommand(ChatID(chat_id), UserID(user_id)))
        bot.set_state(chat_id, states.GameState.PLAYER_CHOICE)
        await bot.handle_update(update)
        return

    try:
        await mediator.send(
            LetterTurnCommand(
                ChatID(chat_id),
                UserID(user_id),
                text,
                settings.bot.random_score_from,
                settings.bot.random_score_to,
            )
        )
        bot.set_state(chat_id, states.GameState.PLAYER_CHOICE)
        await bot.handle_update(update)
    except GameOver as e:
        await bot.send_message(chat_id, e.message)
        bot.set_state(chat_id, states.GameState.FINISHED)


def setup_handlers(bot: protocols.Bot):
    bot.add_handler(
        join_to_game,
        [
            filters.CallbackQueryFilter("join"),
            filters.StateFilter(states.GameState.PREPARED),
        ],
    )
    bot.add_handler(
        player_turn,
        [
            filters.OrCombinedFilter(
                filters.CallbackQueryFilter("letter"),
                filters.CallbackQueryFilter("word"),
            ),
            filters.StateFilter(states.GameState.WAIT_PLAYER_CHOICE),
        ],
    )
    bot.add_handler(
        skip_turn,
        [
            filters.CallbackQueryFilter("skip"),
            filters.StateFilter(states.GameState.WAIT_PLAYER_CHOICE),
        ],
    )
    bot.add_handler(
        create_game,
        [
            filters.GroupFilter(),
            filters.CommandFilter("/game"),
        ],
    )
    bot.add_handler(
        wait_players,
        [
            filters.MessageFilter(),
            filters.GroupFilter(),
            filters.StateFilter(states.GameState.PREPARING),
        ],
    )
    bot.add_handler(
        start_game,
        [
            filters.MessageFilter(),
            filters.GroupFilter(),
            filters.StateFilter(states.GameState.STARTED),
        ],
    )
    bot.add_handler(
        player_choice,
        [
            filters.StateFilter(states.GameState.PLAYER_CHOICE),
        ],
    )
    bot.add_handler(
        player_letter_turn,
        [
            filters.MessageFilter(),
            filters.GroupFilter(),
            filters.StateFilter(states.GameState.PLAYER_LETTER_TURN),
        ],
    )
    bot.add_handler(
        player_word_turn,
        [
            filters.MessageFilter(),
            filters.GroupFilter(),
            filters.StateFilter(states.GameState.PLAYER_WORD_TURN),
        ],
    )
