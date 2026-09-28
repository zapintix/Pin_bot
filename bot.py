import os

from uuid import UUID
from dotenv import load_dotenv
from pybotx import (
    Bot,
    BotAccountWithSecret,
    HandlerCollector,
    IncomingMessage,
)

load_dotenv()

collector = HandlerCollector()

waiting_for_pin: dict[str, dict[str, str]] = {}


@collector.command(
    "/pin",
    description="Закрепить сообщение",
)
async def pin_command(
    message: IncomingMessage,
    bot: Bot,
) -> None:
    print("🔥🔥🔥 PIN HANDLER CALLED")

    chat_id = os.environ["CHAT_ID"]
    user_huid = str(message.sender.huid)

    print("CHAT_ID", chat_id)
    print("USER_ID", user_huid)

    waiting_for_pin[chat_id] = {
        "user_huid": user_huid,
        "reply_chat_id": str(message.chat.id),
    }

    print("waiting_for_pin", waiting_for_pin)

    await bot.answer_message(
        "📌 Отправьте в чат сообщение, которое нужно закрепить."
    )


@collector.command(
    "/unpin",
    description="Открепить сообщение",
)
async def unpin_command(
    message: IncomingMessage,
    bot: Bot,
) -> None:
    chat_id = os.environ["CHAT_ID"]

    waiting_for_pin.pop(chat_id, None)

    await bot.unpin_message(
        bot_id=message.bot.id,
        chat_id=UUID(chat_id),
    )

    await bot.answer_message(
        "📌 Сообщение откреплено."
    )


@collector.default_message_handler
async def message_handler(
    message: IncomingMessage,
    bot: Bot,
) -> None:
    chat_id = os.environ["CHAT_ID"]
    user_huid = str(message.sender.huid)

    print("MESSAGE - chat_id:", chat_id)
    print("MESSAGE - user_huid:", user_huid)

    waiting = waiting_for_pin.get(chat_id)

    if not waiting:
        return

    if waiting["user_huid"] != user_huid:
        print("ERROR WITH user_huid")
        return

    reply_chat_id = UUID(waiting["reply_chat_id"])

    waiting_for_pin.pop(chat_id, None)

    print(
        "DATA FOR PIN:",
        message.bot.id,
        UUID(chat_id),
        message.sync_id,
    )

    await bot.pin_message(
        bot_id=message.bot.id,
        chat_id=UUID(chat_id),
        sync_id=message.sync_id,
    )

    await bot.send_message(
        bot_id=message.bot.id,
        chat_id=reply_chat_id,
        body="📌 Сообщение закреплено!",
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