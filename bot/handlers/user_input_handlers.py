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
import asyncio

logging.basicConfig(level=logging.DEBUG)

router = Router()

# Contains filenames for photo uploading
saved_photonames = dict()


# Handle name input for photo uploading
@router.message(
    lambda message: message.text and
    states.user_states[message.from_user.id] == states.States.UPLOAD_NAME_ENTERING
)
async def upload_name_enter(message: types.Message):
    user_id = message.from_user.id
    # Check that filename is wrapped in double quotes. Like "AwesomeFilename"
    if not utils.wrapped_in_quotes(message.text):
        await message.answer(
            'Wrap your photo name in two double quotes!\n'
            'Like that: {}'.format(html.italic('"AwesomeFilename"')),
        )
        return

    photoname = message.text[1:-1]
    # Check that the filename
    if not utils.check_filename(photoname):
        await message.answer(
            "Something is wrong with your filename. "
            "Please, check that your photo name satisfy these conditions:\n"
            "• The length does not exceed 128 characters\n"
            "• The filename is not empty\n"
            "• Contains only latin letters, arabic digits and underscore symbols ('_')\n"
        )
        return

    if db.is_present(photoname, user_id):
        await message.answer("Photo with passed already exists!")
        return

    saved_photonames[user_id] = photoname
    states.user_states[user_id] = states.States.UPLOAD_PHOTO_LOADING
    await message.answer(
        "Now you can upload your photo",
    )


# user uploads photo
@router.message(
    F.photo,
    lambda message: states.user_states[message.from_user.id] == states.States.UPLOAD_PHOTO_LOADING
)
async def upload_photo(message: types.Message, bot: Bot):
    user_id = message.from_user.id
    try:
        # The additional check is added to prevent strange behavior when user sends group of photos
        if states.user_states[user_id] != states.States.UPLOAD_PHOTO_LOADING:
            return

        # change the state in the beginning to prevent other handlers call
        states.user_states[user_id] = states.States.MAIN

        # accept the photo as BytesIO and pass it to the corresponding function
        image = await bot.download(message.photo[-1].file_id)
        db.save_photo(image, saved_photonames[user_id], user_id)

        # and return to the original keyboard
        await message.answer(
            "You photo has been successfully saved!",
            reply_markup=keyboards.get_root_keyboard()
        )
    except Exception as e:
        logging.error(e)
        states.user_states[user_id] = states.States.UPLOAD_PHOTO_LOADING
        await message.answer(
            "Oops, something went wrong while uploading photo",
        )


# Handle name input for photo deletion
@router.message(
    lambda message: message.text and
    states.user_states[message.from_user.id] == states.States.DELETE_PHOTO
)
async def upload_name_enter(message: types.Message):
    try:
        user_id = message.from_user.id
        # Check that the filename is wrapped in double quotes. Like "AwesomeFilename"
        if not utils.wrapped_in_quotes(message.text):
            await message.answer(
                'Wrap your photo name in two double quotes!\n'
                'Like that: {}'.format(html.italic('"AwesomeFilename"')),
            )
            return

        photoname = message.text[1:-1]
        logging.debug(photoname)

        # Check that the filename satisfies all format conditions
        if not utils.check_filename(photoname):
            await message.answer(
                "You, probably, made a typo in your photo name. "
                "Please, check that your photo name satisfy these conditions:\n"
                "• The length does not exceed 128 characters\n"
                "• The filename is not empty\n"
                "• Contains only latin letters, arabic digits and underscore symbols ('_')\n"
            )
            return

        # Check that the photo with passed name exists
        if not db.is_present(photoname, user_id):
            await message.answer("Photo with passed does not exist!")
            return

        db.delete_photo(photoname, user_id)

        # Drop the state, return to the original keyboard
        states.user_states[user_id] = states.States.MAIN
        await message.answer(
            f"The photo {html.italic(photoname)} has been successfully deleted!",
            reply_markup=keyboards.get_root_keyboard()
        )
    except Exception as e:
        logging.error(e)
        await message.answer("Oops, something went wrong")

