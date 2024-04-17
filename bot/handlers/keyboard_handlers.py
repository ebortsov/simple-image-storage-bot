from aiogram import Router
from aiogram.filters import Command
from aiogram import types
from aiogram import html
from bot.keyboards import keyboards
from bot.user_states import states
from bot.utils import utils
import logging

logging.basicConfig(level=logging.DEBUG)

router = Router()


@router.message(
    lambda message: message.text == 'Upload' and
                    states.user_states[int(message.from_user.id)] == states.States.MAIN
)
async def upload(message: types.Message):
    user_id = message.from_user.id
    states.user_states[user_id] = states.States.UPLOAD_NAME_ENTERING
    await message.answer(
        text='Enter the name under what you want upload your photo.\n'
             f'Format: "{html.italic("name-of-photo")}"\n'
             f'For example, if you want to upload photo under the name {html.italic("FunnyWaffle_2009.png")} '
             'then enter {}'.format(html.italic('"FunnyWaffle_2009"')),
        reply_markup=keyboards.get_upload_keyboard()
    )


@router.message(
    lambda message: message.text == 'Cancel uploading' and
    states.user_states[message.from_user.id] in
    (states.States.UPLOAD_NAME_ENTERING, states.States.UPLOAD_PHOTO_LOADING)
)
async def cancel_upload(message: types.Message):
    user_id = message.from_user.id
    states.user_states[user_id] = states.States.MAIN
    await message.answer(
        text='Alright, the photo uploading has been cancelled',
        reply_markup=keyboards.get_root_keyboard()
    )


@router.message(
    lambda message: message.text == 'Delete' and
    states.user_states[message.from_user.id] == states.States.MAIN
)
async def delete(message: types.Message):
    user_id = message.from_user.id
    states.user_states[user_id] = states.States.DELETE_PHOTO
    await message.answer(
        text='Enter the name of the photo you want to delete.\n'
             f'Format: "{html.italic("name-of-photo")}"\n'
             f'For example, if you uploaded photo under the name {html.italic("CuteCucumbers")} '
             'then enter {}'.format(html.italic('"CuteCucumbers"')),
        reply_markup=keyboards.get_delete_keyboard()
    )