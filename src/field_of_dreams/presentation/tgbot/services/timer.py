import asyncio
from typing import Optional
from field_of_dreams.infrastructure.tgbot import bot


def timer(
    seconds: int,
    bot_: bot.Bot,
    chat_id: int,
    text: Optional[str] = None,
    expired_text: Optional[str] = None,
) -> asyncio.Task:
    async def start_timer() -> None:
        nonlocal seconds
        if text:
            await bot_.send_message(chat_id, text.format(seconds))
        await asyncio.sleep(seconds)
        if expired_text:
            await bot_.send_message(chat_id, expired_text.format(seconds))

    task = asyncio.create_task(start_timer())
    return task
