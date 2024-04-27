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
from datetime import datetime
import sqlite3

logging.basicConfig(level=logging.DEBUG)


def get_router(db_conn: sqlite3.Connection) -> Router:
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
        photoname = await utils.handle_raw_photoname_check(message)
        if not photoname:
            return
        try:
            if photoname in db.get_photonames(db_conn, user_id):
                await message.answer("Photo with passed name already exists!")
                return

            saved_photonames[user_id] = photoname
            states.user_states[user_id] = states.States.UPLOAD_PHOTO_LOADING
            await message.answer(
                "Now you can upload your photo",
            )
        except Exception as e:
            logging.error(e)
            await message.answer("Oops, something went wrong")

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

            # Handle case when for some reason the image wasn't downloaded
            if not image:
                raise RuntimeError("Image wasn't downloaded")

            db.save_photo(db_conn, saved_photonames[user_id], image, user_id, message.photo[-1].file_id)

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
    async def delete_name_enter(message: types.Message):
        try:
            user_id = message.from_user.id
            photoname = await utils.handle_raw_photoname_check(message)
            if not photoname:
                return

            # Check that the photo with passed name exists
            if photoname not in db.get_photonames(db_conn, user_id):
                await message.answer("Photo with passed name does not exist!")
                return

            db.delete_photo(db_conn, photoname, user_id)

            # Drop the state, return to the original keyboard
            states.user_states[user_id] = states.States.MAIN
            await message.answer(
                f"The photo {html.italic(photoname)} has been successfully deleted!",
                reply_markup=keyboards.get_root_keyboard()
            )
        except Exception as e:
            logging.error(e)
            await message.answer("Oops, something went wrong")

    # Handle input of the photo name to show the photo
    @router.message(
        lambda message: message.text and
        states.user_states[message.from_user.id] == states.States.SHOW_PHOTO
    )
    async def show_photo(message: types.Message):
        try:
            user_id = message.from_user.id
            photoname = await utils.handle_raw_photoname_check(message)
            if not photoname:
                return

            # Check that the photo with passed name exists
            if photoname not in db.get_photonames(db_conn, user_id):
                await message.answer("Photo with passed name does not exist!")
                return

            photo_info = db.get_photo(db_conn, photoname, user_id)

            await message.answer_photo(
                photo=photo_info['telegram_file_id'],
                caption=f"{html.bold('Name: ')}"
                        f"{html.quote(photo_info['photoname'])} "
            )
        except Exception as e:
            logging.error(e)
            await message.answer("Oops, something went wrong")

    return router
