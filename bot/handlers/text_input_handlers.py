"""
This module contains handlers for accepting text input from user. This handlers must be included after
all other handlers, since they theoretically may interfere with other keyboard handlers
"""
from aiogram import Router
from aiogram import types
from aiogram import html
from bot.user_states import states
from bot.utils import utils
from bot.db import db
import logging

logging.basicConfig(level=logging.DEBUG)

router = Router()

# Contains filenames for photo uploading
saved_filenames = dict()


# Handle name input for photo upload
@router.message(
    lambda message: states.user_states[message.from_user.id]
                    == states.States.UPLOAD_NAME_ENTERING
)
async def upload_name_enter(message: types.Message):
    user_id = message.from_user.id
    # Check that filename is wrapped in double quotes. Like "AwesomeFilename"
    if not len(message.text) <= 2 or not message.text.startswith('"') or not message.text.endswith('"'):
        await message.answer('Wrap your filename in two double quotes!\n'
                             'Like that: {}'.format(html.italic('"AwesomeFilename"')))
        return

    filename = message[1:-1]
    # Check that the filename consists only of allowed symbols
    if not utils.check_filename(filename):
        await message.answer("Filename contains invalid symbols!")
        return

    # Check the length of the filename
    if len(filename) >= 128:
        await message.answer(f"The length of photo name should be {html.bold('less')} than 128 characters!")

    # Check that the filename is unique
    if filename in db.get_all_photo_names(user_id):
        await message.answer('The photo with given name already exists!')

    saved_filenames[user_id] = filename
