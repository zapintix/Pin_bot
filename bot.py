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

waiting_for_pin: dict[str, str] = {}


@collector.command(
    "/pin",
    description="Закрепить сообщение",
)
async def pin_command(
    message: IncomingMessage,
    bot: Bot,
) -> None:
    print("🔥🔥🔥 PIN HANDLER CALLED")
    print("message",message)
    chat_id = os.environ["CHAT_ID"]
    print("CHAT_ID",chat_id)
    user_huid = str(message.sender.huid)
    print("USER_ID",user_huid)
    waiting_for_pin[chat_id] = user_huid
    print("waiting_for_pin", waiting_for_pin)
    await bot.answer_message(
        "📌 Отправьте сообщение, которое нужно закрепить."
    )


@collector.command(
    "/unpin",
    description="Открепить сообщение",
)
async def unpin_command(
    message: IncomingMessage,
    bot: Bot,
) -> None:
    waiting_for_pin.pop(str(message.chat.id), None)

    await bot.unpin_message(
        bot_id=message.bot.id,
        chat_id=os.environ["CHAT_ID"],
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
    user_huid = str(message.sender.huid)

    if waiting_for_pin.get(chat_id) != user_huid:
        return

    waiting_for_pin.pop(chat_id, None)

    await bot.pin_message(
        bot_id=message.bot.id,
        chat_id=os.environ["CHAT_ID"],
        sync_id=message.sync_id,
    )

    await bot.answer_message(
        "📌 Сообщение закреплено!"
    )


print(
    "REGISTERED COMMANDS:",
    collector._user_commands_handlers.keys(),
)

bot = Bot(
    collectors=[collector],
    bot_accounts=[
        BotAccountWithSecret(
            id=os.environ["EXPRESS_BOT_ID"],
            cts_url=os.environ["EXPRESS_HOST"],
            secret_key=os.environ["EXPRESS_SECRET_KEY"],
        )
    ],
)