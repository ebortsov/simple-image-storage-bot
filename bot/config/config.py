from dataclasses import dataclass
from environs import Env
from pathlib import Path


@dataclass
class TelegramBot:
    bot_token: str


@dataclass
class Databases:
    images_database: Path


@dataclass
class Logs:
    important_logs: Path
    info_logs: Path


class Config:
    _telegram_bot = TelegramBot
    _databases = Databases
    _logs = Logs

    def __init__(self, path: str | None = None):
        env = Env()
        env.read_env(path)
        self.telegram_bot = self._telegram_bot(
            bot_token=env.str('TOKEN')
        )
        self.databases = self._databases(
            images_database=Path(env.str('IMAGES_DB'))
        )
        self.logs = self._logs(
            important_logs=env.str('IMPORTANT_LOGS'),
            info_logs=env.str('INFO_LOGS')
        )
