from pathlib import Path
from bot.utils import utils
import dotenv
import io
import logging
logging.basicConfig(level=logging.DEBUG)

config = dotenv.dotenv_values()
images = utils.get_project_root().joinpath(config['IMAGES_FOLDER_NAME'])


def start_stuff(user_id: int):
    #  Does some preliminary stuff, like creating the folder for the user
    user_folder = images.joinpath(str(user_id))
    user_folder.mkdir(exist_ok=True)


def get_all_photo_names(user_id: int):
    user_folder = images.joinpath(str(user_id))
    return [file.stem for file in user_folder.iterdir() if file.is_file()]


def save_photo(photo: io.BytesIO, image_name: str, user_id: int) -> bool:
    try:
        user_folder = images.joinpath(str(user_id))
        with open(user_folder.joinpath(image_name + '.jpg'), mode='wb') as file:
            file.write(photo.read())
    except Exception as e:
        logging.debug(e)
        raise e
    else:
        return True



