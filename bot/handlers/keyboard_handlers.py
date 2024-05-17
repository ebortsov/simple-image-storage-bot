"""
This module contains handlers for reply keyboards
"""
from aiogram import Router
from aiogram.filters import Command
from aiogram import types
from aiogram import html
from bot.keyboards import keyboards
from bot.user_states import states
from bot.utils import utils
import logging
from datetime import datetime
import sqlite3
from bot.db import db


def get_router(db_conn: sqlite3.Connection) -> Router:
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
                 f'For example, if you want to upload photo under the name {html.italic("FunnyWaffle_2009.png")} ' +
                 'then enter "FunnyWaffle_2009"'.format(html.italic('"FunnyWaffle_2009"')),
            reply_markup=keyboards.get_upload_cancel_keyboard()
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
                 f'For example, if you uploaded photo under the name {html.italic("CuteCucumbers")} ' +
                 'then enter {}'.format(html.italic('"CuteCucumbers"')),
            reply_markup=keyboards.get_delete_cancel_keyboard()
        )

    @router.message(
        lambda message: message.text == 'Cancel deletion' and
        states.user_states[message.from_user.id] == states.States.DELETE_PHOTO
    )
    async def cancel_deletion(message: types.Message):
        user_id = message.from_user.id
        states.user_states[user_id] = states.States.MAIN
        await message.answer(
            text='Alright, the photo deletion has been cancelled',
            reply_markup=keyboards.get_root_keyboard()
        )

    @router.message(
        lambda message: message.text == "Show..." and
        states.user_states[message.from_user.id] == states.States.MAIN
    )
    async def menu_for_show(message: types.Message):
        user_id = message.from_user.id
        states.user_states[user_id] = states.States.SHOW
        await message.answer(
            text='There you can see the statistics of your photos, '
                 'or pick a particular photo and check it',
            reply_markup=keyboards.get_show_keyboard()
        )

    @router.message(
        lambda message: message.text == 'Back' and
        states.user_states[message.from_user.id] == states.States.SHOW
    )
    async def return_from_show_to_main(message: types.Message):
        user_id = message.from_user.id
        states.user_states[user_id] = states.States.MAIN
        await message.answer(
            text='Here\'s main menu',
            reply_markup=keyboards.get_root_keyboard()
        )

    @router.message(
        lambda message: message.text == 'Show photonames' and
        states.user_states[message.from_user.id] == states.States.SHOW
    )
    async def show_photonames(message: types.Message):
        try:
            user_id = message.from_user.id
            photonames = db.get_photonames(db_conn, user_id)
            if photonames:
                reply = (
                        f'{html.bold("Here is the list of your photos:")}\n' +
                        '\n'.join(
                            f"{html.bold('Name: ')}"
                            f"{html.quote(photoname)}"
                            for photoname in photonames
                        )
                )
                await message.answer(text=reply)
            else:
                await message.answer(text="You haven't stored anything yet!")
        except Exception as e:
            logging.error(e)
            await message.answer("Oops, something went wrong")

    @router.message(
        lambda message: message.text == 'Show photo' and
        states.user_states[message.from_user.id] == states.States.SHOW
    )
    async def show_photo(message: types.Message):
        user_id = message.from_user.id
        states.user_states[user_id] = states.States.SHOW_PHOTO
        await message.answer(
            text='Enter the name of the photo you want to see.\n'
                 f'Format: "{html.italic("name-of-photo")}"\n',
            reply_markup=keyboards.get_show_photo_cancel_keyboard()
        )

    @router.message(
        lambda message: message.text == 'Back' and
        states.user_states[message.from_user.id] == states.States.SHOW_PHOTO
    )
    async def cancel_show_photo(message: types.Message):
        user_id = message.from_user.id
        states.user_states[user_id] = states.States.SHOW
        await message.answer(
            text='There you can see the statistics of your photos, '
                 'or pick a particular photo and check it',
            reply_markup=keyboards.get_show_keyboard()
        )

    @router.message(
        lambda message: message.text == 'Carousel' and
        states.user_states[message.from_user.id] == states.States.MAIN
    )
    async def show_carousel(message: types.Message):
        try:
            user_id = message.from_user.id
            photonames = db.get_photonames(db_conn, user_id)

            # User hasn't stored any photos
            if not photonames:
                await message.answer(text="You haven't stored anything yet!")
                return

            # Otherwise show first photo and attach inline keyboard
            photo = db.get_photo(db_conn, photonames[0], user_id)
            await message.answer_photo(
                photo=photo['telegram_file_id'],
                reply_markup=keyboards.get_carousel_keyboard(photo['photoname'], user_id)
            )

        except Exception as e:
            logging.error(e)
            await message.answer("Oops, something went wrong")

    return router
