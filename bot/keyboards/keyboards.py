from aiogram.utils import keyboard
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from bot.handlers import carousel


# Get the initial keyboard. This keyboard is shown to user when he enters /start command
def get_root_keyboard() -> ReplyKeyboardMarkup:
    # Construct keyboard builder and add some buttons
    builder = keyboard.ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text='Upload'))
    builder.add(KeyboardButton(text='Show...'))
    builder.add(KeyboardButton(text='Delete'))
    builder.add(KeyboardButton(text='Carousel'))
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)


# When user wants to upload photo, they prompt to the name of photo.
# This keyboard will be shown while user is typing the photo-name.
def get_upload_cancel_keyboard() -> ReplyKeyboardMarkup:
    builder = keyboard.ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text='Cancel uploading'))
    builder.adjust(1)
    return builder.as_markup(
        resize_keyboard=True,
        input_field_placeholder='Enter the name of the photo',
        one_time_keyboard=True
    )


# This keyboard is shown, when user prompts to enter the name of the photo they want to delete
def get_delete_cancel_keyboard() -> ReplyKeyboardMarkup:
    builder = keyboard.ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text='Cancel deletion'))
    builder.adjust(1)
    return builder.as_markup(
        resize_keyboard=True,
        input_field_placeholder='Enter the name of the photo',
        one_time_keyboard=True
    )


def get_show_keyboard() -> ReplyKeyboardMarkup:
    builder = keyboard.ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text='Show photonames'))
    builder.add(KeyboardButton(text='Show photo'))
    builder.add(KeyboardButton(text='Back'))
    builder.adjust(2)
    return builder.as_markup(
        resize_keyboard=True
    )


def get_show_photo_cancel_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text='Back')]],
        resize_keyboard=True
    )


def get_carousel_keyboard(current_photoname: str, user_id: int) -> InlineKeyboardMarkup:
    builder = keyboard.InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(
            text='◀️',
            callback_data=carousel.CarouselCallback(
                action=-1,
                current_photoname=current_photoname,
                user_id=user_id
            ).pack()
        )
    )
    builder.add(
        InlineKeyboardButton(
            text='▶️',
            callback_data=carousel.CarouselCallback(
                action=1,
                current_photoname=current_photoname,
                user_id=user_id
            ).pack()
        )
    )
    builder.adjust(2)
    return builder.as_markup()
