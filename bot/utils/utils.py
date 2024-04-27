import re
from pathlib import Path
from aiogram import types, html


# Check that string is wrapped in quotes
def wrapped_in_quotes(photoname: str) -> bool:
    return len(photoname) >= 2 and photoname.startswith('"') and photoname.endswith('"')


# Check the filename, i.e.:
# - the length <= 128
# - the filename is not empty
# - filename consists of valid characters
def check_photoname(filename: str) -> bool:
    return 0 < len(filename) <= 128 and bool(re.match("^[A-Za-z0-9_]+$", filename))


def get_project_root():
    return Path(__file__).parent.parent.parent


async def handle_raw_photoname_check(message: types.Message) -> None | str:
    # Check that filename is wrapped in double quotes. Like "AwesomeFilename"
    if not wrapped_in_quotes(message.text):
        await message.answer(
            'Wrap your photo name in two double quotes!\n'
            'Like that: {}'.format(html.italic('"AwesomeFilename"')),
        )
        return None

    photoname = message.text[1:-1]
    # Check that the filename
    if not check_photoname(photoname):
        await message.answer(
            "Something is wrong with your filename. "
            "Please, check that your photo name satisfy these conditions:\n"
            "• The length does not exceed 128 characters\n"
            "• The filename is not empty\n"
            "• Contains only latin letters, arabic digits and underscore symbols ('_')\n"
        )
        return None
    return photoname
