from aiogram import Router
from aiogram.filters import Command
from aiogram import types
from aiogram import html
from bot.keyboards import keyboards
from bot.user_states import states

import logging

logging.basicConfig(level=logging.DEBUG)

router = Router()


@router.message(lambda message: message.text == 'Upload')
async def upload(message: types.Message):
    user_id = str(message.from_user.id)
    states.change_upload_status(user_id, states.UploadState.ENTERING_NAME)
    await message.answer(
        # TODO: add mentioning of the limitations of the photo-name
        text='Cool! Now enter the name of the photo want to upload.\n'
             f'Format: ["{html.italic("name-of-photo")}"]\n'
             f'For example, if you photo is {html.italic("FunnyWaffle_2009.png")} '
             f'then enter "FunnyWaffle_2009"',
        reply_markup=keyboards.get_upload_name_enter_keyboard()
    )


@router.message(lambda message: message.text == 'Cancel uploading')
async def cancel_upload(message: types.Message):
    states.change_upload_status(str(message.from_user.id), states.UploadState.NOT_STARTED)
    await message.answer(
        text='Alright, the photo uploading has been cancelled',
        reply_markup=keyboards.get_root_keyboard()
    )



