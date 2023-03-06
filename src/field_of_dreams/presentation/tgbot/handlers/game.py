import asyncio
from datetime import timedelta

from field_of_dreams.infrastructure.tgbot.bot import TelegramBot
from field_of_dreams.application.common import Mediator
from field_of_dreams.application.handlers.create_game import CreateGameCommand
from field_of_dreams.application.handlers.add_player import AddPlayerCommand
from field_of_dreams.application.handlers.start_game import StartGameCommand
from field_of_dreams.config import Settings


async def start_game(
    update: dict, bot: TelegramBot, mediator: Mediator, settings: Settings
):
    author_id = update["message"]["from"]["id"]
    author_name = update["message"]["from"]["username"]
    chat_id = update["message"]["chat"]["id"]
    max_turn_time = settings.max_turn_time
    await mediator.send(
        CreateGameCommand(
            author_id, author_name, chat_id, timedelta(seconds=max_turn_time)
        )
    )
    # TODO: Вынести всё во view
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
                [{"text": "Присоединиться", "callback_data": "join"}]
            ]
        },
    )
    notify_time = settings.players_waiting_time
    message = await bot.send_message(
        chat_id, f"Секунд до начала игры: {notify_time}"
    )
    for i in range(max_turn_time, 0, -1):
        if i == notify_time // 2:
            notify_time = i
            await bot.edit_message(
                chat_id,
                message["result"]["message_id"],
                f"Секунд до начала игры: {notify_time}.",
            )
        await asyncio.sleep(1)
    await bot.edit_message(
        chat_id,
        message_notify["result"]["message_id"],
        text="Начинаем сбор игроков.",
    )
    await bot.edit_message(
        chat_id,
        message["result"]["message_id"],
        "Сбор игроков закончен.",
    )
    await mediator.send(StartGameCommand(chat_id))


async def join_to_game(
    update: dict,
    bot: TelegramBot,
    mediator: Mediator,
):
    user_id = update["callback_query"]["from"]["id"]
    chat_id = update["callback_query"]["message"]["chat"]["id"]
    username = update["callback_query"]["from"]["username"]

    await mediator.send(AddPlayerCommand(chat_id, user_id, username))

    await bot.send_message(chat_id, f"{username} присоединился к игре.")
