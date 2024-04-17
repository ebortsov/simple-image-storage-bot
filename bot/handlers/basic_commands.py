from aiogram import Router
from aiogram.filters import Command
from aiogram import types
from aiogram import html
from bot.keyboards import keyboards
from bot.user_states import states
from bot.db import db
import logging
logging.basicConfig(level=logging.DEBUG)

router = Router()


@router.message(Command('start'))
async def start_cmd(message: types.Message):
    user_id = message.from_user.id
    states.user_states[user_id] = states.States.MAIN
    db.start_stuff(user_id)

    await message.answer(
        html.bold("Welcome to my image saver bot!\n") +
        "With this bot you can:\n"
        "- Manage your photos\n"
        "- View your photos\n"
        "- Create amazing carousel " + html.italic('soon will be available!') + '\n'
        "And all it is using nice keyboard without any command!",
        reply_markup=keyboards.get_root_keyboard()
    )
