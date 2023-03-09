import asyncio
from field_of_dreams.infrastructure.tgbot import types, bot


def timer(
    seconds: int,
    bot_: bot.Bot,
    message: types.Message,
    chat_id: int,
    text: str,
    expired_text: str,
) -> asyncio.Task:
    async def start_timer(
        seconds: int, bot: bot.Bot, message: types.Message, chat_id: int
    ) -> None:
        sec = seconds
        for i in range(sec):
            if i == sec // 2:
                sec = i
                await bot.edit_message(
                    chat_id,
                    message.message_id,
                    text.format(seconds),
                )
            await asyncio.sleep(1)

        await bot.edit_message(
            chat_id,
            message.message_id,
            expired_text,
        )

    task = asyncio.create_task(start_timer(seconds, bot_, message, chat_id))
    return task
