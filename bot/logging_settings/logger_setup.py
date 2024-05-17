import logging
import dotenv
from bot.logging_settings import logging_filters
from bot.utils import utils
from pathlib import Path


# I know that for this project such a logging may seem redundant,
# but I wrote all this just to practice the logging module :D
def setup():
    config = dotenv.dotenv_values()
    errors_log = utils.get_project_root().joinpath(config['IMPORTANT_LOGS'])
    info_log = utils.get_project_root().joinpath(config['INFO_LOGS'])

    default_formatter = logging.Formatter(
        fmt='#%(levelname)s [%(asctime)s] %(filename)s:%(lineno)d - %(message)s'
    )

    # All logs with level ERROR or higher go to errors_log file
    error_handler = logging.FileHandler(filename=errors_log, mode='a', encoding='utf-8')
    error_handler.setFormatter(default_formatter)
    error_handler.addFilter(logging_filters.ErrorOrHigherFilter())
    error_handler.setLevel(logging.ERROR)

    # All logs with level WARNING go to stderr
    warning_handler = logging.StreamHandler()
    warning_handler.setFormatter(default_formatter)
    warning_handler.addFilter(logging_filters.WarningFilter())

    # All logs with level INFO go to info_log file
    info_handler = logging.FileHandler(filename=info_log, mode='a', encoding='utf-8')
    info_handler.setFormatter(default_formatter)
    info_handler.addFilter(logging_filters.InfoNotFromAiogramFilter())

    # All DEBUG loggers go to stdout
    debug_handler = logging.StreamHandler()
    debug_handler.setFormatter(default_formatter)
    debug_handler.addFilter(logging_filters.DebugFilter())

    # This guy will catch everything
    default_handler = logging.StreamHandler()
    default_handler.setFormatter(default_formatter)
    default_handler.setLevel(logging.DEBUG)

    # Attach handlers to the root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(error_handler)
    root_logger.addHandler(warning_handler)
    root_logger.addHandler(info_handler)
    root_logger.addHandler(debug_handler)
    root_logger.addHandler(default_handler)

