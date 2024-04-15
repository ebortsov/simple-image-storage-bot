from aiogram import Router
from aiogram.filters import Command
from aiogram import types
from aiogram import html
from bot.keyboards import keyboards
from bot.user_states import states

import logging
logging.basicConfig(level=logging.DEBUG)

router = Router()


@router.message(Command('start'))
async def start_cmd(message: types.Message):
    states.drop_states(str(message.from_user.id))
    await message.answer(
        html.bold("Welcome to my image saver bot!") +
        "With this bot you can:\n"
        "- Manage your photos\n"
        "- View your photos\n"
        "- Create amazing carousel " + html.italic('soon will be available!') + '\n'
        "And all it is using nice keyboard without any command!",
        reply_markup=keyboards.get_root_keyboard()
    )
