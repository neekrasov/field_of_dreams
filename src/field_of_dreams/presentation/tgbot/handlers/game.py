import asyncio
import logging
from functools import partial
from datetime import timedelta

from field_of_dreams.core.entities.chat import ChatID
from field_of_dreams.core.entities.user import UserID
from field_of_dreams.core.entities.player import Player
from field_of_dreams.infrastructure.tgbot import filters, types, protocols
from field_of_dreams.core.common import ApplicationException, Mediator
from field_of_dreams.core.handlers.create_game import CreateGameCommand
from field_of_dreams.core.handlers.add_player import AddPlayerCommand
from field_of_dreams.core.handlers.start_game import StartGameCommand
from field_of_dreams.core.handlers.letter_turn import LetterTurnCommand
from field_of_dreams.core.handlers.word_turn import WordTurnCommand
from field_of_dreams.core.handlers.finish_game import FinishGameCommand
from field_of_dreams.core.handlers.check_is_last import CheckLastPlayerCommand
from field_of_dreams.core.handlers.idle_turn import IdleTurnCommand
from field_of_dreams.presentation.tgbot.middlewares.throttling import (
    throttling,
)
from field_of_dreams.core.handlers.get_current_player import (
    GetCurrentPlayerCommand,
)
from field_of_dreams.core.handlers.check_user_queue import (
    CheckUserQueueCommand,
)
from field_of_dreams.presentation.tgbot.states import (
    GameStatus,
    GameState,
)
from field_of_dreams.config import Settings
from services.timer import create_timer
from keyboards import game as game_kb

logger = logging.getLogger()


@throttling()
async def create_game(
    update: types.Update,
    bot: protocols.Bot,
    mediator: Mediator,
    settings: Settings,
    storage: protocols.Storage,
):
    chat_id = update.message.chat.id  # type: ignore
    logger.info("Create game in chat %s", chat_id)
    state = await storage.get_state(chat_id)

    if state and state.state not in (GameStatus.FINISHED, None):
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
                "\n🕑 Время ожидания (в секундах): "
                f"{settings.bot.players_waiting_time}",
            ]
        ),
        reply_markup={
            "inline_keyboard": [
                [{"text": "Присоединиться", "callback_data": "join"}],
            ]
        },
    )
    await storage.set_state(chat_id, GameState(GameStatus.PREPARING))
    update.message.entities = None  # type: ignore
    await bot.handle_update(update)


@throttling()
async def finish(
    update: types.Update,
    bot: protocols.Bot,
    mediator: Mediator,
    storage: protocols.Storage,
):
    chat_id = update.message.chat.id  # type: ignore
    logger.info("Finish game in chat %s", chat_id)
    user_id = update.message.from_user.id  # type: ignore
    username = update.message.from_user.username  # type: ignore

    admins = await bot.get_chat_administrators(chat_id)
    is_admin = any(admin.user.id == user_id for admin in admins)
    await mediator.send(
        FinishGameCommand(ChatID(chat_id), UserID(user_id), is_admin)
    )
    await storage.set_state(chat_id, GameState(GameStatus.FINISHED))
    timer = bot.get_timer(chat_id)
    if timer:
        timer.del_all()
    await bot.send_message(
        chat_id, f"Игра завершена пользователем @{username}"
    )


async def wait_players(
    update: types.Update,
    bot: protocols.Bot,
    mediator: Mediator,
    settings: Settings,
    storage: protocols.Storage,
):
    chat_id = update.message.chat.id  # type: ignore
    logger.info("Wait players in chat %s", chat_id)
    state = await storage.get_state(chat_id)
    if state.state != GameStatus.PREPARING:  # type: ignore
        return

    await storage.set_state(chat_id, GameState(GameStatus.PREPARED))
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
    await storage.set_state(chat_id, GameState(GameStatus.STARTED))
    await bot.handle_update(update)


async def join_to_game(
    update: types.Update,
    bot: protocols.Bot,
    mediator: Mediator,
):
    chat_id = update.callback_query.message.chat.id  # type: ignore
    user_id = update.callback_query.from_user.id  # type: ignore
    username = update.callback_query.from_user.username  # type: ignore
    logger.info("User %s join to game in chat %s", user_id, chat_id)
    await mediator.send(
        AddPlayerCommand(ChatID(chat_id), UserID(user_id), username),
    )
    await bot.answer_callback_query(
        update.callback_query.id, "Вы присоединились к игре."  # type: ignore
    )


async def start_game(
    update: types.Update,
    bot: protocols.Bot,
    mediator: Mediator,
    settings: Settings,
    storage: protocols.Storage,
):
    chat_id = update.message.chat.id  # type: ignore
    logger.info("Start game in chat %s", chat_id)

    await storage.set_state(chat_id, GameState(GameStatus.PLUG))
    try:
        await mediator.send(StartGameCommand(ChatID(chat_id)))
        await bot.send_message(
            chat_id,
            (
                "🕑❗ Время на прочтение условия: "
                f"{settings.bot.question_read_time}"
            ),
        )
        timer = bot.get_timer(chat_id)
        if not timer:
            timer = bot.create_timer(chat_id)
        task = timer.run(
            partial(asyncio.sleep, delay=settings.bot.question_read_time)
        )
        await task
        await storage.set_state(chat_id, GameState(GameStatus.PLAYER_CHOICE))
        await bot.handle_update(update)
    except ApplicationException as e:
        await storage.set_state(chat_id, GameState(GameStatus.FINISHED))
        raise e


async def player_choice(
    update: types.Update,
    bot: protocols.Bot,
    mediator: Mediator,
    settings: Settings,
    storage: protocols.Storage,
):
    if update.message:
        chat_id = update.message.chat.id  # type: ignore
    else:
        chat_id = update.callback_query.message.chat.id  # type: ignore

    logger.info("Player choice in chat %s", chat_id)
    await storage.set_state(chat_id, GameState(GameStatus.PLUG))

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
                f"@{current_player.username} что вы будете угадывать?"
                "\n🕑 Ограничение по времени хода: "
                f"{settings.bot.max_turn_time}"
            ),
            reply_markup=game_kb.choice_letter_or_word(),
        )
    else:
        message = await bot.send_message(
            chat_id,
            (
                f"@{current_player.username}, вы остались последним, "
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
                f"от пользователя {current_player.username}"
            ),
        )
    )
    await storage.set_state(chat_id, GameState(GameStatus.WAIT_PLAYER_CHOICE))
    await task
    if not task.cancelled():
        await bot.delete_message(chat_id, message.message_id)
        await mediator.send(IdleTurnCommand(ChatID(chat_id)))
        await storage.set_state(chat_id, GameState(GameStatus.PLAYER_CHOICE))
        await bot.handle_update(update)


async def skip_turn(
    update: types.Update,
    bot: protocols.Bot,
    mediator: Mediator,
    storage: protocols.Storage,
):
    user_id = update.callback_query.from_user.id  # type: ignore
    chat_id = update.callback_query.message.chat.id  # type: ignore
    message_id = update.callback_query.message.message_id  # type: ignore
    callback_id = update.callback_query.id  # type: ignore

    logger.info("User %s skipped turn in chat %s", user_id, chat_id)
    timer = bot.get_timer(chat_id)
    if timer and timer.all_done():
        await bot.answer_callback_query(
            callback_id, "🕑 Время выбора закончилось"  # type: ignore # noqa
        )
        return

    await mediator.send(
        CheckUserQueueCommand(ChatID(chat_id), UserID(user_id))
    )
    if timer:
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
        f"@{current_player.username} решил пропустить ход. 🚶‍♂️",
    )
    await storage.set_state(chat_id, GameState(GameStatus.PLAYER_CHOICE))
    await bot.handle_update(update)


async def player_turn(
    update: types.Update,
    bot: protocols.Bot,
    mediator: Mediator,
    settings: Settings,
    storage: protocols.Storage,
):
    chat_id = update.callback_query.message.chat.id  # type: ignore
    user_id = update.callback_query.from_user.id  # type: ignore
    message_id = update.callback_query.message.message_id  # type: ignore
    username = update.callback_query.from_user.username  # type: ignore
    call_id = update.callback_query.id  # type: ignore

    logger.info("The user %s has chosen a letter in chat %s", user_id, chat_id)
    timer = bot.get_timer(chat_id)
    if timer and timer.all_done():
        await bot.answer_callback_query(call_id, "🕑 Время выбора закончилось")
        return

    await mediator.send(
        CheckUserQueueCommand(ChatID(chat_id), UserID(user_id))
    )
    if timer:
        timer.del_all()

    await bot.delete_message(chat_id, message_id)
    await bot.answer_callback_query(
        call_id, "Ваш ход был принят.", show_alert=False
    )

    options = {"letter": "букву", "word": "слово"}
    if not timer:
        timer = bot.create_timer(chat_id)
    task = timer.run(
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
        state = GameState(GameStatus.PLAYER_LETTER_TURN)
    else:
        state = GameState(GameStatus.PLAYER_WORD_TURN)

    state.data = {"user_id": user_id}
    await storage.set_state(chat_id, state)

    await task
    if not task.cancelled():
        await mediator.send(IdleTurnCommand(ChatID(chat_id)))
        await storage.set_state(chat_id, GameState(GameStatus.PLAYER_CHOICE))
        await bot.handle_update(update)


async def player_word_turn(
    update: types.Update,
    bot: protocols.Bot,
    mediator: Mediator,
    storage: protocols.Storage,
):
    chat_id = update.message.chat.id  # type: ignore
    user_id = update.message.from_user.id  # type: ignore

    logger.info("The user %s has chosen a word in chat %s", user_id, chat_id)
    state = await storage.get_state(chat_id)
    timer = bot.get_timer(chat_id)
    user_id_from_state = state.data.get("user_id")  # type: ignore
    if user_id_from_state != user_id or (timer and timer.all_done()):
        return
    if timer:
        timer.del_all()
    text = update.message.text.lower().strip()  # type: ignore
    if len(text) == 0:
        await mediator.send(IdleTurnCommand(ChatID(chat_id)))
        await storage.set_state(chat_id, GameState(GameStatus.PLAYER_CHOICE))
        await bot.handle_update(update)

    await mediator.send(WordTurnCommand(ChatID(chat_id), text))
    await storage.set_state(chat_id, GameState(GameStatus.PLAYER_CHOICE))
    await bot.handle_update(update)


async def player_letter_turn(
    update: types.Update,
    bot: protocols.Bot,
    mediator: Mediator,
    storage: protocols.Storage,
):
    chat_id = update.message.chat.id  # type: ignore
    user_id = update.message.from_user.id  # type: ignore
    state = await storage.get_state(chat_id)
    if not state:
        return
    timer = bot.get_timer(chat_id)
    if state.data.get("user_id") != user_id or (timer and timer.all_done()):
        return

    is_last: bool = await mediator.send(
        CheckLastPlayerCommand(ChatID(chat_id))
    )
    if is_last:
        await bot.answer_callback_query(
            update.callback_query.id, "Вам доступен только выбор слова."  # type: ignore # noqa
        )
        return

    if timer:
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
        await storage.set_state(chat_id, GameState(GameStatus.PLAYER_CHOICE))
        await bot.handle_update(update)
        return

    await mediator.send(LetterTurnCommand(ChatID(chat_id), text))
    await storage.set_state(chat_id, GameState(GameStatus.PLAYER_CHOICE))
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
            filters.StateFilter(GameStatus.PREPARED),
        ],
    )
    bot.add_handler(
        player_turn,
        [
            filters.StateFilter(GameStatus.WAIT_PLAYER_CHOICE),
            filters.OrCombinedFilter(
                filters.CallbackQueryFilter("letter"),
                filters.CallbackQueryFilter("word"),
            ),
        ],
    )
    bot.add_handler(
        skip_turn,
        [
            filters.CallbackQueryFilter("skip"),
            filters.StateFilter(GameStatus.WAIT_PLAYER_CHOICE),
        ],
    )
    bot.add_handler(
        create_game,
        [
            filters.MessageFilter(),
            filters.GroupFilter(),
            filters.CommandFilter("/game"),
        ],
    )
    bot.add_handler(
        wait_players,
        [
            filters.MessageFilter(),
            filters.GroupFilter(),
            filters.StateFilter(GameStatus.PREPARING),
        ],
    )
    bot.add_handler(
        start_game,
        [
            filters.MessageFilter(),
            filters.GroupFilter(),
            filters.StateFilter(GameStatus.STARTED),
        ],
    )
    bot.add_handler(
        player_choice,
        [
            filters.StateFilter(GameStatus.PLAYER_CHOICE),
        ],
    )
    bot.add_handler(
        player_letter_turn,
        [
            filters.MessageFilter(),
            filters.GroupFilter(),
            filters.StateFilter(GameStatus.PLAYER_LETTER_TURN),
        ],
    )
    bot.add_handler(
        player_word_turn,
        [
            filters.MessageFilter(),
            filters.GroupFilter(),
            filters.StateFilter(GameStatus.PLAYER_WORD_TURN),
        ],
    )
