import logging
import sqlite3

from aiogram import Router
from aiogram import types
from aiogram.filters.callback_data import CallbackData

from bot.db import db
from bot.keyboards import keyboards


# The idea that the callback will contain the information about the current photo on the carousel
class CarouselCallback(CallbackData, prefix='carousel'):
    action: int
    current_photoname: str
    user_id: int


router = Router()


@router.callback_query(CarouselCallback.filter())
async def change_photo(callback: types.CallbackQuery, callback_data: CarouselCallback, db_conn: sqlite3.Connection):
    message = callback.message
    user_id = callback_data.user_id
    current_photoname = callback_data.current_photoname
    try:
        photonames = db.get_photonames(db_conn, user_id)

        # User deleted all photos
        if not photonames:
            await message.answer(text="You haven't stored anything yet!")
            return

        # Get new photonames (if user deleted photo showed on the message,
        # just pick some other photo among the stored ones)
        new_photoname = (
            photonames[(len(photonames) + photonames.index(current_photoname) +
                        callback_data.action) % len(photonames)]  # some arithmetics to obtain next/prev photo
            if current_photoname in photonames
            else photonames[0]
        )
        new_photo = db.get_photo(db_conn, new_photoname, user_id)

        logging.info(f"user {user_id} switched photo on the message {message.message_id}")

        # Change photo
        await callback.message.edit_media(
            media=types.InputMediaPhoto(media=new_photo['telegram_file_id'])
        )

        # Change reply keyboard
        await callback.message.edit_reply_markup(
            reply_markup=keyboards.get_carousel_keyboard(new_photoname, user_id)
        )

        await callback.answer()
    except Exception as e:
        logging.info(e)
        await message.answer("Oops, something went wrong")
