from aiogram import F, Dispatcher, Bot
from aiogram.filters import Command, CommandObject
from aiogram.client.bot import DefaultBotProperties
from aiogram.types import Message
from aiogram import types
from aiogram.enums import ParseMode
from aiogram import html
from aiogram.utils.media_group import MediaGroupBuilder
from aiogram.types.input_file import FSInputFile
import asyncio
import dotenv
import logging
import re
from collections import defaultdict
from enum import Enum, auto
from pathlib import Path
from datetime import datetime
import random

'''
Simple bot that simulates simple cloud image storage with some basic functionality.
Commands:
1) /upload - start command for bot to prepare for uploading photo
After the command the bot will ask user to choose name for the photo.
After that, the bot will ask user to upload the photo 

2) /reset - used to cancel photo uploading

3) /delete <name-of-photo> - deletes photo with name-of-photo.
After the command tells user if the command was successful

4) /show_names - shows the list of names of all uploaded photos

6) /show_photo <name-of-photo> - shows a photo with passed name (if such photo exists)

5) /generate_album - picks several random photos from the uploaded ones and creates album of picked photos
'''

logging.basicConfig(level=logging.DEBUG)

config = dotenv.dotenv_values()
bot = Bot(token=config['TOKEN'], default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# the storage is organized as follows:
# all user photos are stored in the folder with name of chat's id
# all user folders are stored in folder with the name stored in variable storage
# like image_folder/4519822341/kitten.png
storage = config['IMAGE_FOLDER_NAME']
storage_path = Path(__file__).parent.parent.joinpath(storage)


# while uploading photo, the program may be in three states
class UploadStates(Enum):
    NOT_STARTED = auto(),  # user hasn't started uploading photo (i.e. /upload command has not been called)
    ENTERING_NAME = auto(),  # user called /upload. Now the program prompts the user for the photo name
    UPLOADING_PHOTO = auto()  # user entered valid name and now user should upload the photo


upload_states = defaultdict(lambda: UploadStates.NOT_STARTED)  # stores UploadStates for users. The keys are chats' ids
photo_names = defaultdict(str)  # stores photo names for users used while uploading photo. The keys are chats' ids


# Handler for command /start
@dp.message(Command('start'))
async def start(message: types.Message):
    await message.answer(
        html.bold("This is my simple image saver bot!\n\n") +
        "To show the list of available commands user /help command"
    )


# Handler for command /help
@dp.message(Command('help'))
async def help_cmd(message: types.Message):
    await message.answer(
        html.quote(
            "Currently, this bot supports the following commands:\n"
            "• /upload - upload photo (only photos, no file-format for now, sorry)\n\n"
            "• /reset - cancel photo uploading\n\n"
            "• /delete <name-of-photo> - delete photo\n\n"
            "• /show_names - shows the list of names of all uploaded photos\n\n"
            "• /show_photo <name-of-photo> - shows a photo with passed name (if such photo exists)\n\n"
            "• /generate_album - picks several random photos "
            "from the uploaded ones and creates album of picked photos\n\n") +
        html.italic("but pretty soon, only buttons will be here...")
    )


# Handler for command /upload
@dp.message(Command('upload'))
async def upload(message: Message):
    upload_states[message.chat.id] = UploadStates.ENTERING_NAME  # mark that user has started uploading photo
    await message.answer(f'Cool! Now send me the name of the uploaded photo!\n'
                         f'But {html.bold("note")}, that the name may contain {html.italic("only")} '
                         f'latin letters (a-z, A-Z), digits (0-9) and underscores (\'_\')')


@dp.message(Command('reset'))  # This command resets upload state for user
async def reset(message):
    upload_states[message.chat.id] = UploadStates.NOT_STARTED
    photo_names[message.chat.id] = str()
    await message.answer(rf"As you wish! You can start uploading photo again")


# Prompt user to enter name of the photo (used only after /upload command)
@dp.message(lambda message: message.text and upload_states[message.chat.id] == UploadStates.ENTERING_NAME)
async def set_name(message):
    photo_name = message.text
    # perform some checks
    # 1) The name of file may only consist of latin letters, digits, and underscores
    alnum_check = bool(re.match(r'^[A-Za-z0-9_]+$', photo_name))
    # 2) The length of photo name should be less than 128 characters
    length_check = len(message.text) < 128
    # 3) The photo name must be unique (i.e. no files with the same photo name are stored by user)
    # Additional alnum_check is used to prevent malicious code from coming to .glob()
    uniqueness_check = (
        not list(storage_path.joinpath(str(message.chat.id)).glob(f"{photo_name}.*"))
        if alnum_check else False
    )

    if alnum_check and length_check and uniqueness_check:
        # everything is correct
        photo_names[message.chat.id] = message.text
        upload_states[message.chat.id] = UploadStates.UPLOADING_PHOTO
        await message.answer("Cool! Now you can upload your photo")
    elif not length_check:
        # photo name is too long
        await message.answer(f"The length of photo name should be {html.bold('less')} than 128 characters!")
    elif not alnum_check:
        # photo name contains invalid characters
        await message.answer(f"The photo name contains invalid character!")
    elif not uniqueness_check:
        # the photo name is not unique
        await message.answer('The photo with given photo name already exists!')


@dp.message(F.photo, lambda message: upload_states[message.chat.id] == UploadStates.UPLOADING_PHOTO)
async def upload_photo(message: Message):
    # For some reason, aiogram handles all photos when user sends media group,
    # So additional check is required
    if upload_states[message.chat.id] != UploadStates.UPLOADING_PHOTO:
        return

    # download photo sent by user
    path_to_photo = (storage_path
                     .joinpath(str(message.chat.id))
                     .joinpath(f"{photo_names[message.chat.id]}.jpg"))

    # first, handle case when user has never uploaded any photos (so the user folder has never been created)
    if not path_to_photo.parent.exists():
        path_to_photo.parent.mkdir(parents=True, exist_ok=True)
    # reset some parameters
    upload_states[message.chat.id] = UploadStates.NOT_STARTED
    photo_names[message.chat.id] = str()

    await bot.download(
        message.photo[-1],
        destination=str(path_to_photo)
    )
    await message.answer("The photo has been successfully saved!")


@dp.message(Command('show_names'))
async def show_names(message: Message):
    # Show names and dates of all uploaded photos
    # Format: "Name: <photo-name> Created: <creation-date>

    # list of object of type Path of user photos
    user_photos = list(storage_path.joinpath(str(message.chat.id)).iterdir())

    if not user_photos:
        reply = "Looks like you have not uploaded any photos yet!"
    else:
        # Form reply of format "Name: <photo_name> Time of creation: <time of creation>" for all stored photos
        reply = (
                f'{html.bold("Here is the list of your photos:")}\n' +
                '\n'.join(
                    f"{html.bold('Name: ')}"
                    f"{html.quote(photo.name)} | "
                    f"{html.bold('Time of creation: ')}" +
                    datetime.fromtimestamp(photo.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
                    for photo in user_photos
                )
        )
    await message.answer(reply)


@dp.message(Command('show_photo'))
async def show_photo(message: Message, command: CommandObject):
    photo_name = command.args
    if not photo_name:
        # user did not pass photo name as an argument for /show_photo
        await message.answer(
            'Wrong command format!\n'
            f'Format: /show_photo {html.quote("<photo_name>")}'
        )
        return

    # Finds a photo with passed name among stored ones
    # If such photo does not exist the tuple will be empty
    path_to_photo = tuple(
        photo
        # if users folder does not exist, this will not raise error and simply return 'empty' generator
        for photo in storage_path.joinpath(str(message.chat.id)).iterdir()
        if photo.stem == photo_name
    )  # the problem with iglob is that user can probably send some malicious string, so I do not use it here

    if not path_to_photo:
        # user has not stored photo with passed name
        await message.answer(
            f"Oops, look like you haven't saved photo with name "
            f"{html.italic(html.quote(f'{photo_name}'))}"
        )
    else:
        # otherwise show the photo to use and some stats about the photo
        path_to_photo = path_to_photo[0]
        await message.answer_photo(
            photo=FSInputFile(path_to_photo),
            caption=f"{html.bold('Name: ')}"
                    f"{html.quote(path_to_photo.name)} "
                    f"{html.bold('Time of creation: ')}" +
                    datetime.fromtimestamp(path_to_photo.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
        )


@dp.message(Command('delete'))
async def delete(message: Message, command: CommandObject):
    # delete stored photo
    photo_name = command.args
    if not photo_name:
        # user did not pass photo name as an argument for /delete
        await message.answer('Wrong command format!\n'
                             f'Format: /delete {html.quote("<photo_name>")}')
        return

    # Finds a photo with passed name among stored ones
    # If such photo does not exist the tuple will be empty
    path_to_photo = tuple(
        photo
        # if users folder does not exist, this will not raise error and simply return 'empty' generator
        for photo in storage_path.joinpath(str(message.chat.id)).iterdir()
        if photo.stem == photo_name
    )

    if not path_to_photo:
        # user has not stored photo with passed name
        await message.answer(
            f"Oops, look like you haven't saved photo with name "
            f"{html.italic(html.quote(f'{photo_name}'))}"
        )
    else:
        # delete photo otherwise
        path_to_photo[0].unlink()
        await message.answer(
            f"Alright, the photo with name {html.italic(html.quote(f'{photo_name}'))} "
            f"has been successfully {html.bold('deleted')}"
        )


@dp.message(Command('generate_album'))
async def generate_album(message: Message):
    desired_media_group_size = 7
    # Generate album of min(ALBUM_SIZE, actual_album_size) random photos from the album
    # Does not support album generation if user's storage contains less than 3 photos

    # list of Pathlike objects - photos uploaded by user
    # if users folder does not exist, this will not raise error and simply return 'empty' generator
    user_photos = list(storage_path.joinpath(str(message.chat.id)).iterdir())

    if len(user_photos) < 3:
        # user's storage contains less than three photos
        await message.answer(f'Wow there, to use our {html.bold(html.italic("cool"))} feature '
                             f'for generating random album of your photos, '
                             f'you need to first upload at least {html.bold("three")} photos!')
    else:
        # number of photos in the media group
        media_group_size = min(desired_media_group_size, len(user_photos))

        # now, generate album_group_builder and feed it with random uploaded photos
        album_group_builder = MediaGroupBuilder(caption=html.bold("Here is some of photos from your album:"))
        for photo in random.sample(user_photos, k=media_group_size):  # feed album_group_builder with random photos
            album_group_builder.add_photo(media=FSInputFile(photo))

        await message.answer_media_group(
            media=album_group_builder.build()
        )


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
