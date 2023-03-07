import asyncio
import logging
from datetime import timedelta

from field_of_dreams.core.entities.chat import ChatID
from field_of_dreams.core.entities.user import UserID
from field_of_dreams.infrastructure.tgbot import (
    filters,
    types,
    protocols,
    states,
)
from field_of_dreams.core.common import ApplicationException, Mediator
from field_of_dreams.core.handlers.create_game import CreateGameCommand
from field_of_dreams.core.handlers.add_player import AddPlayerCommand
from field_of_dreams.core.handlers.start_game import StartGameCommand
from field_of_dreams.config import Settings

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
        raise ApplicationException("Дождитесь завершения прошлой игры.")

    await mediator.send(
        CreateGameCommand(
            UserID(update.message.from_user.id),  # type: ignore
            update.message.from_user.username,  # type: ignore
            ChatID(chat_id),
            timedelta(seconds=settings.bot.max_turn_time),
        )
    )
    message_notify = await bot.send_message(
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
    state = states.GameState.PREPARING
    state.value.set_data({"message_notify_id": message_notify.message_id})
    bot.set_state(chat_id, state)
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
    message_notify_id = state.value.data["message_notify_id"]  # type: ignore
    notify_time = settings.bot.players_waiting_time
    message = await bot.send_message(chat_id, f"До начала игры: {notify_time}")
    for i in range(settings.bot.max_turn_time, 0, -1):
        if i == notify_time // 2:
            notify_time = i
            await bot.edit_message(
                chat_id,
                message.message_id,
                f"Секунд до начала игры: {notify_time}.",
            )
        await asyncio.sleep(1)
    await bot.edit_message(
        chat_id,
        message_notify_id,
        text="Начинаем сбор игроков.",
    )
    await bot.edit_message(
        chat_id,
        message.message_id,
        "Сбор игроков закончен.",
    )
    bot.set_state(chat_id, states.GameState.STARTED)
    await bot.handle_update(update)


async def start_game(
    update: types.Update,
    bot: protocols.Bot,
    mediator: Mediator,
):
    logger.info("Start game")
    chat_id = update.message.chat.id  # type: ignore
    try:
        await mediator.send(StartGameCommand(ChatID(chat_id)))
    except ApplicationException as e:
        bot.set_state(chat_id, states.GameState.FINISHED)
        raise e
    bot.set_state(chat_id, states.GameState.PLAYER_TURN)
    await bot.handle_update(update)


async def player_turn(
    update: types.Update,
    bot: protocols.Bot,
    mediator: Mediator,
):
    logger.info("Player turn")
    chat_id = update.message.chat.id  # type: ignore
    await bot.send_message(chat_id, "Not implemented")


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


def setup_handlers(bot: protocols.Bot):
    bot.add_handler(
        join_to_game,
        [
            filters.CallbackQueryFilter("join"),
            filters.StateFilter(states.GameState.PREPARING),
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
        player_turn,
        [
            filters.MessageFilter(),
            filters.GroupFilter(),
            filters.StateFilter(states.GameState.PLAYER_TURN),
        ],
    )
