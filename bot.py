import asyncio
import os

from dotenv import load_dotenv
from pybotx import (
    Bot,
    BotAccountWithSecret,
    HandlerCollector,
    IncomingMessage,
)

load_dotenv()

collector = HandlerCollector()

bot_account = BotAccountWithSecret(
    id=os.getenv("EXPRESS_BOT_ID"),
    cts_url=os.getenv("EXPRESS_HOST"),
    secret_key=os.getenv("EXPRESS_SECRET_KEY"),
)

bot = Bot(
    collectors=[collector],
    bot_accounts=[bot_account],
)


waiting_for_pin: dict[str, str] = {}


@collector.command(
    "/pin",
    description="Закрепить сообщение",
)
async def pin_command(
    message: IncomingMessage,
    bot: Bot,
) -> None:
    chat_id = str(message.chat.id)
    user_id = str(message.sender.id)

    waiting_for_pin[chat_id] = user_id

    await bot.answer_message(
        "📌 Введите сообщение, которое нужно закрепить."
    )


@collector.command(
    "/unpin",
    description="Открепить сообщение",
)
async def unpin_command(
    message: IncomingMessage,
    bot: Bot,
) -> None:
    chat_id = str(message.chat.id)

    waiting_for_pin.pop(chat_id, None)

    await bot.unpin_message(
        bot_id=message.bot.id,
        chat_id=message.chat.id,
    )

    await bot.answer_message(
        "📌 Сообщение откреплено."
    )


@collector.default_message_handler
async def message_handler(
    message: IncomingMessage,
    bot: Bot,
) -> None:
    chat_id = str(message.chat.id)
    user_id = str(message.sender.id)

    expected_user_id = waiting_for_pin.get(chat_id)

    if expected_user_id != user_id:
        return

    waiting_for_pin.pop(chat_id, None)

    await bot.pin_message(
        bot_id=message.bot.id,
        chat_id=message.chat.id,
        sync_id=message.sync_id,
    )

    await bot.answer_message(
        "📌 Сообщение закреплено!"
    )


async def main() -> None:
    await bot.startup()
    print("Запуск бота...")

    try:
        await asyncio.Event().wait()
        print("Бот получил команду")
    finally:
        await bot.shutdown()


if __name__ == "__main__":
    asyncio.run(main())