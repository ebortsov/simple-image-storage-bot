from aiogram.utils import keyboard
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


# Get the initial keyboard. This keyboard is shown to user when he enters /start command
def get_root_keyboard() -> ReplyKeyboardMarkup:
    # Construct keyboard builder and add some buttons
    builder = keyboard.ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text='Upload'))
    builder.add(KeyboardButton(text='Show...'))
    builder.add(KeyboardButton(text='Delete'))
    # builder.add(KeyboardButton(text='carousel')) WILL BE ADDED PRETTY SOON!!!
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)


# When user wants to upload photo, they prompt to the name of photo.
# This keyboard will be shown while user is typing the photo-name.
def get_upload_keyboard() -> ReplyKeyboardMarkup:
    builder = keyboard.ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text='Cancel uploading'))
    builder.adjust(1)
    return builder.as_markup(
        resize_keyboard=True,
        input_field_placeholder='Enter the name of the photo',
        one_time_keyboard=True
    )
