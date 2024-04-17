from pathlib import Path
from bot.utils import utils
import dotenv
import io
import logging
logging.basicConfig(level=logging.DEBUG)

config = dotenv.dotenv_values()
images = utils.get_project_root().joinpath(config['IMAGES_FOLDER_NAME'])

# TODO: save file-ids, to decrease the load on Telegram Servers


def start_stuff(user_id: int):
    #  Does some preliminary stuff, like creating the folder for the user
    user_folder = images.joinpath(str(user_id))
    user_folder.mkdir(exist_ok=True)


def get_paths_to_all_photos(user_id: int):
    try:
        user_folder = images.joinpath(str(user_id))
        return (file for file in user_folder.iterdir() if file.is_file())
    except Exception as e:
        # For some reason could not get access to user folder
        logging.critical(e)
        raise e


def save_photo(photo: io.BytesIO, photoname: str, user_id: int) -> None:
    try:
        user_folder = images.joinpath(str(user_id))
        with open(user_folder.joinpath(photoname + '.jpg'), mode='wb') as file:
            file.write(photo.read())
    except Exception as e:
        logging.error(e)
        raise e


def delete_photo(photoname: str, user_id: int) -> None:
    try:
        path_to_photo = images.joinpath(str(user_id)).joinpath(photoname + '.jpg')
        path_to_photo.unlink()
    except Exception as e:
        logging.error(e)
        raise e


def is_present(photoname: str, user_id: int) -> bool:
    logging.debug(photoname)
    logging.debug(list(photo.stem for photo in get_paths_to_all_photos(user_id)))
    return photoname in (photo.stem for photo in get_paths_to_all_photos(user_id))


# Get photo as io.BytesIO
def get_photo_as_bytes(photoname: str, user_id: int) -> io.BytesIO:
    try:
        path_to_photo = images.joinpath(str(user_id)).joinpath(photoname + '.jpg')
        photo = io.BytesIO()
        with open(path_to_photo, mode='rb') as file:
            photo.write(file.read())
        return photo
    except Exception as e:
        logging.error(e)
        raise e


# Get photo as Pathlike object
def get_photo_as_pathlike(photoname: str, user_id: int) -> Path:
    try:
        path_to_photo = images.joinpath(str(user_id)).joinpath(photoname + '.jpg')
        return path_to_photo
    except Exception as e:
        logging.error(e)
        raise e


# get os.stat() of the photo by its name
def get_statistics_of_photo(photoname: str, user_id: int):
    try:
        path_to_photo = images.joinpath(str(user_id)).joinpath(photoname + '.jpg')
        return path_to_photo.stat()
    except Exception as e:
        logging.error(e)
        raise e
