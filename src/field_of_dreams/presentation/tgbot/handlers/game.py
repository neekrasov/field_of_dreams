import asyncio
import logging
from functools import partial
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
)
from field_of_dreams.core.handlers.create_game import CreateGameCommand
from field_of_dreams.core.handlers.add_player import AddPlayerCommand
from field_of_dreams.core.handlers.start_game import StartGameCommand
from field_of_dreams.core.handlers.letter_turn import LetterTurnCommand
from field_of_dreams.core.handlers.word_turn import WordTurnCommand
from field_of_dreams.core.handlers.finish_game import FinishGameCommand
from field_of_dreams.core.handlers.check_is_last import CheckLastPlayerCommand
from field_of_dreams.core.handlers.get_current_player import (
    GetCurrentPlayerCommand,
)
from field_of_dreams.core.handlers.check_user_queue import (
    CheckUserQueueCommand,
)
from field_of_dreams.core.handlers.idle_turn import IdleTurnCommand
from field_of_dreams.config import Settings
from services.timer import create_timer
from keyboards import game as game_kb

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
                "\n🕑 Время ожидания (в секундах): "
                f"{settings.bot.max_turn_time}",
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


async def finish(
    update: types.Update,
    bot: protocols.Bot,
    mediator: Mediator,
    settings: Settings,
):
    logger.info("Finish game")
    chat_id = update.message.chat.id  # type: ignore
    state = bot.get_state(chat_id)
    if state == states.GameState.FINISHED:
        await bot.send_message(chat_id, "Игра уже завершена.")
        return

    user_id = update.message.from_user.id  # type: ignore
    username = update.message.from_user.username  # type: ignore
    admins = await bot.get_chat_administrators(chat_id)
    is_admin = False
    for admin in admins:
        if admin.user.id == user_id:
            is_admin = True
            break

    await mediator.send(
        FinishGameCommand(ChatID(chat_id), UserID(user_id), is_admin)
    )
    timer = bot.get_or_create_timer(chat_id)
    timer.del_all()
    bot.set_state(chat_id, states.GameState.FINISHED)
    await bot.send_message(
        chat_id, f"Игра завершена пользователем @{username}"
    )


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

    timer = bot.get_or_create_timer(chat_id)
    task = timer.run(
        create_timer(
            settings.bot.players_waiting_time,
            bot,
            chat_id,
            expired_text="❗Сбор игроков закончен.",
        )
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
    settings: Settings,
):
    logger.info("Start game")
    chat_id = update.message.chat.id  # type: ignore
    try:
        await mediator.send(StartGameCommand(ChatID(chat_id)))
        await bot.send_message(
            chat_id,
            (
                "🕑❗ Время на прочтение условия: "
                f"{settings.bot.question_read_time}"
            ),
        )
        bot.set_state(chat_id, states.GameState.PLUG)
        timer = bot.get_or_create_timer(chat_id)
        task = timer.run(
            partial(asyncio.sleep, delay=settings.bot.question_read_time)
        )
        await task
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

    bot.set_state(chat_id, states.GameState.PLUG)

    current_player: Player = await mediator.send(
        GetCurrentPlayerCommand(ChatID(chat_id))
    )
    is_last: bool = await mediator.send(
        CheckLastPlayerCommand(ChatID(chat_id))
    )
    if not is_last:
        message = await bot.send_message(
            chat_id,
            (
                f"@{current_player.get_username()} что вы будете угадывать?"
                "\n🕑 Ограничение по времени хода: "
                f"{settings.bot.max_turn_time}"
            ),
            reply_markup=game_kb.choice_letter_or_word(),
        )
    else:
        message = await bot.send_message(
            chat_id,
            (
                f"@{current_player.get_username()}, вы остались последним, "
                "вам доступен только выбор слова."
                "\n🕑 Ограничение по времени хода: "
                f"{settings.bot.max_turn_time}"
            ),
            reply_markup=game_kb.only_word_choice(),
        )

    timer = bot.get_or_create_timer(chat_id)
    task = timer.run(
        create_timer(
            settings.bot.max_turn_time,
            bot,
            chat_id,
            expired_text=(
                "🕑 Истёк срок ожидания ответа "
                f"от пользователя {current_player.get_username()}"
            ),
        )
    )
    bot.set_state(chat_id, states.GameState.WAIT_PLAYER_CHOICE)
    await task
    if not task.cancelled():
        await bot.delete_message(chat_id, message.message_id)
        await mediator.send(IdleTurnCommand(ChatID(chat_id)))
        bot.set_state(chat_id, states.GameState.PLAYER_CHOICE)
        await bot.handle_update(update)


async def skip_turn(
    update: types.Update,
    bot: protocols.Bot,
    mediator: Mediator,
):
    logger.info("Skip Turn")
    user_id = update.callback_query.from_user.id  # type: ignore
    chat_id = update.callback_query.message.chat.id  # type: ignore
    message_id = update.callback_query.message.message_id  # type: ignore
    callback_id = update.callback_query.id  # type: ignore

    timer = bot.get_or_create_timer(chat_id)
    if timer.all_done():
        await bot.answer_callback_query(
            update.callback_query.id, "🕑 Время выбора закончилось"  # type: ignore # noqa
        )
        return

    await mediator.send(
        CheckUserQueueCommand(ChatID(chat_id), UserID(user_id))
    )
    timer.del_all()
    await bot.delete_message(chat_id, message_id)
    await bot.answer_callback_query(
        callback_id, "Ваш ход был принят.", show_alert=False
    )
    current_player: Player = await mediator.send(
        GetCurrentPlayerCommand(ChatID(chat_id))
    )
    await mediator.send(IdleTurnCommand(ChatID(chat_id)))
    await bot.send_message(
        chat_id,
        f"@{current_player.get_username()} решил пропустить ход. 🚶‍♂️",
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
    message_id = update.callback_query.message.message_id  # type: ignore
    username = update.callback_query.from_user.username  # type: ignore

    timer = bot.get_or_create_timer(chat_id)
    if timer.all_done():
        await bot.answer_callback_query(
            update.callback_query.id, "🕑 Время выбора закончилось"  # type: ignore # noqa
        )
        return

    await mediator.send(
        CheckUserQueueCommand(ChatID(chat_id), UserID(user_id))
    )
    timer.del_all()

    await bot.delete_message(chat_id, message_id)
    await bot.answer_callback_query(update.callback_query.id, "Ваш ход был принят.", show_alert=False)  # type: ignore # noqa

    options = {"letter": "букву", "word": "слово"}
    timer.run(
        create_timer(
            settings.bot.max_turn_time,
            bot,
            chat_id,
            text=(
                f"Игрок @{username} выбирает "
                f"{options[update.callback_query.data]}... \n"  # type: ignore
                "🕑 Ограничение по времени (в секундах): {}"
            ),
            expired_text=("🕑 Истёк срок ожидания ответа от пользователя"),
        )
    )
    if update.callback_query.data == "letter":  # type: ignore
        state = states.GameState.PLAYER_LETTER_TURN
    else:
        state = states.GameState.PLAYER_WORD_TURN

    state.value.set_data({"user_id": user_id})
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
    timer = bot.get_or_create_timer(chat_id)
    if user_id_from_state != user_id or timer.all_done():
        return

    timer.del_all()
    text = update.message.text.lower().strip()  # type: ignore
    if len(text) == 0:
        await mediator.send(IdleTurnCommand(ChatID(chat_id)))
        bot.set_state(chat_id, states.GameState.PLAYER_CHOICE)
        await bot.handle_update(update)

    await mediator.send(
        WordTurnCommand(
            ChatID(chat_id),
            text,
            settings.bot.random_score_from,
            settings.bot.random_score_to,
        )
    )
    bot.set_state(chat_id, states.GameState.PLAYER_CHOICE)
    await bot.handle_update(update)


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
    timer = bot.get_or_create_timer(chat_id)
    if user_id_from_state != user_id or timer.all_done():
        return

    is_last: bool = await mediator.send(
        CheckLastPlayerCommand(ChatID(chat_id))
    )
    if is_last:
        await bot.answer_callback_query(
            update.callback_query.id, "Вам доступен только выбор слова."  # type: ignore # noqa
        )
        return

    timer.del_all()
    text = update.message.text.lower().strip()  # type: ignore
    err = False
    if len(text) == 0:
        err = True
    elif len(text) > 1:
        err = True
        await bot.send_message(
            chat_id,
            (
                "🫣 Длина ответа при выборе буквы "
                "не может превышать 1 символ."
            ),
        )

    if err:
        await mediator.send(IdleTurnCommand(ChatID(chat_id)))
        bot.set_state(chat_id, states.GameState.PLAYER_CHOICE)
        await bot.handle_update(update)
        return

    await mediator.send(
        LetterTurnCommand(
            ChatID(chat_id),
            text,
            settings.bot.random_score_from,
            settings.bot.random_score_to,
        )
    )
    bot.set_state(chat_id, states.GameState.PLAYER_CHOICE)
    await bot.handle_update(update)


def setup_handlers(bot: protocols.Bot):
    bot.add_handler(
        finish,
        [
            filters.GroupFilter(),
            filters.CommandFilter("/finish"),
        ],
    )
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
