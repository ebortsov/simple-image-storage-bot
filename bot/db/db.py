from pathlib import Path
from bot.utils import utils
import dotenv
import io
import logging
import sqlite3
from typing import Tuple, List


config = dotenv.dotenv_values()
database_path = utils.get_project_root().joinpath(config['IMAGES_DB'])


CREATE_TABLE = """CREATE TABLE IF NOT EXISTS images (
    photoname TEXT NOT NULL,
    photo BLOB NOT NULL,
    telegram_user_id INTEGER NOT NULL,
    telegram_file_id TEXT NOT NULL,
    UNIQUE(photoname, telegram_user_id)
);"""
SAVE_PHOTO = """INSERT INTO images VALUES (?, ?, ?, ?)"""  # photoname, photo, telegram_user_id, telegram_file_id
DELETE_PHOTO = """DELETE FROM images WHERE photoname = ? AND telegram_user_id = ?"""
GET_PHOTO = """SELECT * FROM images WHERE photoname = ? AND telegram_user_id = ?"""
GET_PHOTONAMES = """SELECT photoname FROM images WHERE telegram_user_id = ?"""


def get_connection() -> sqlite3.Connection:
    con = sqlite3.connect(database_path)
    con.row_factory = sqlite3.Row
    return con


def create_table(db_conn: sqlite3.Connection):
    with db_conn:
        db_conn.execute(CREATE_TABLE)


def save_photo(
        db_conn: sqlite3.Connection,
        photoname: str,
        photo: io.BytesIO,
        telegram_user_id: int,
        telegram_file_id: str
) -> None:
    with db_conn:
        db_conn.execute(SAVE_PHOTO, (photoname, photo.read(), telegram_user_id, telegram_file_id))


def delete_photo(
        db_conn: sqlite3.Connection,
        photoname: str,
        telegram_user_id: int,
) -> None:
    with db_conn:
        db_conn.execute(DELETE_PHOTO, (photoname, telegram_user_id))


def get_photo(
        db_conn: sqlite3.Connection,
        photoname: str,
        telegram_user_id: int
):
    with db_conn:
        return db_conn.execute(GET_PHOTO, (photoname, telegram_user_id)).fetchone()


def get_photonames(
        db_conn: sqlite3.Connection,
        telegram_user_id: int
) -> List[str]:
    with db_conn:
        return [row['photoname'] for row in db_conn.execute(GET_PHOTONAMES, (telegram_user_id, )).fetchall()]

