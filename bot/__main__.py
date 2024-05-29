from aiogram import F, Dispatcher, Bot
import asyncio
from bot.config.logging_settings import logger_setup
from aiogram.client.bot import DefaultBotProperties
from aiogram.enums import ParseMode
from bot.handlers import basic_commands
from bot.handlers import keyboard_handlers
from bot.handlers import user_input_handlers
from bot.handlers import carousel
from bot.db import db
from bot.config.config import Config
from bot.middlewares.throttling import ThrottlingMiddleware


async def main():
    config = Config()

    # Setup logger
    logger_setup.setup()

    dp = Dispatcher()

    # include throttling
    dp.update.middleware(ThrottlingMiddleware())

    # Allow interactions in private chats only
    dp.message.filter(F.chat.type == "private")

    db_conn = db.get_connection()
    db.create_table(db_conn)
    dp.workflow_data.update({'db_conn': db_conn})

    dp.include_router(basic_commands.router)
    dp.include_router(keyboard_handlers.router)
    dp.include_router(carousel.router)
    dp.include_router(user_input_handlers.router)

    bot = Bot(
        token=config.telegram_bot.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    # Drop all pending messages
    await bot.delete_webhook(drop_pending_updates=True)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
