from aiogram import F, Dispatcher, Bot
import asyncio
import dotenv
import logging
from aiogram.client.bot import DefaultBotProperties
from aiogram.enums import ParseMode
from bot.handlers import basic_commands
from bot.handlers import keyboard_handlers
from bot.handlers import user_input_handlers

async def main():
    # Set up level for logger
    logging.basicConfig(level=logging.INFO)
    # Read some configuration files (like bot token etc.)
    config = dotenv.dotenv_values()

    dp = Dispatcher()
    bot = Bot(token=config['TOKEN'], default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    # Allow interactions in private chats only
    dp.message.filter(F.chat.type == "private")

    dp.include_router(basic_commands.router)
    dp.include_router(keyboard_handlers.router)
    dp.include_router(user_input_handlers.router)

    # Drop all pending messages
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
