import logging
from bot.config.logging_settings import logging_filters
from bot.utils import utils
from bot.config.config import Config
import sys


# HOW IT WORKS: All messages that come to the root logger are handled by various handlers
# DEBUG logs got to stdout
# INFO logs to separate file
# WARNING logs go to stderr
# ERROR and CRITICAL logs go to separate file

def setup():
    logging.basicConfig(level=logging.INFO)
    config = Config()
    # Error logs contain information about exceptions (errors) and critical errors (i.e. level >= logging.ERROR)
    errors_log = utils.get_project_root().joinpath(config.logs.important_logs)
    # Info logs contain information about user's action (e.g. user uploaded photo etc.)
    info_log = utils.get_project_root().joinpath(config.logs.info_logs)

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
    info_handler.addFilter(logging_filters.InfoFilter())

    # All DEBUG logs go to stdout
    debug_handler = logging.StreamHandler()
    debug_handler.setFormatter(default_formatter)
    debug_handler.addFilter(logging_filters.DebugFilter())

    # Attach handlers to the root logger
    root_logger = logging.getLogger()
    root_logger.addHandler(error_handler)
    root_logger.addHandler(warning_handler)
    root_logger.addHandler(info_handler)
    root_logger.addHandler(debug_handler)
