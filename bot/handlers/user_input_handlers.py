"""
This module contains handlers for accepting text input from user. This handlers must be included after
all other handlers, since they theoretically may interfere with other keyboard handlers
"""
from aiogram import Bot
from aiogram import Router
from aiogram import types
from aiogram import html
from bot.user_states import states
from bot.utils import utils
from bot.db import db
import logging
from bot.keyboards import keyboards
from aiogram import F
import io

logging.basicConfig(level=logging.DEBUG)

router = Router()

# Contains filenames for photo uploading
saved_photonames = dict()


# Handle name input for photo upload
@router.message(
    lambda message: states.user_states[message.from_user.id]
                    == states.States.UPLOAD_NAME_ENTERING
)
async def upload_name_enter(message: types.Message):
    user_id = message.from_user.id
    # Check that filename is wrapped in double quotes. Like "AwesomeFilename"
    logging.debug(message.text)
    if len(message.text) <= 2 or not message.text.startswith('"') or not message.text.endswith('"'):
        await message.answer(
            'Wrap your photo name in two double quotes!\n'
            'Like that: {}'.format(html.italic('"AwesomeFilename"')),
        )
        return

    photoname = message.text[1:-1]
    # Check that the filename consists only of allowed symbols
    if not utils.check_filename(photoname):
        await message.answer(
            "Photo name contains invalid symbols!",
        )
        return

    # Check the length of the filename
    if len(photoname) >= 128:
        await message.answer(
            f"The length of photo name should be {html.bold('less')} than 128 characters!",
        )
        return

    # Check that the filename is unique
    if photoname in db.get_all_photo_names(user_id):
        await message.answer(
            'The photo with given name already exists!',
        )
        return

    saved_photonames[user_id] = photoname
    states.user_states[user_id] = states.States.UPLOAD_PHOTO_LOADING
    await message.answer(
        "Now you can upload your photo",
    )


@router.message(
    F.photo,
    lambda message: states.user_states[message.from_user.id] == states.States.UPLOAD_PHOTO_LOADING
)
async def upload_photo(message: types.Message, bot: Bot):
    try:
        image = await bot.download(message.photo[-1].file_id)
        user_id = message.from_user.id
        db.save_photo(image, saved_photonames[user_id], user_id)
        states.user_states[user_id] = states.States.MAIN
        await message.answer(
            "You photo has been successfully saved!",
            reply_markup=keyboards.get_root_keyboard()
        )
    except Exception as e:
        logging.debug(e)
        await message.answer(
            "Oops, something went wrong while uploading photo",
        )
