from pathlib import Path
from bot.utils import utils
import dotenv
# TODO: store everything in the database

config = dotenv.dotenv_values()
images = utils.get_project_root().joinpath(config['IMAGES_FOLDER_NAME'])


def start_stuff(user_id: int):
    #  Does some preliminary stuff, like creating the folder for the user
    user_folder = images.joinpath(str(user_id))
    user_folder.mkdir(exist_ok=True)


def get_all_photo_names(user_id: int):
    user_folder = images.joinpath(str(user_id))
    return [file for file in user_folder.iterdir() if file.is_file()]


