import re


def check_filename(filename: str) -> bool:
    return bool(re.match(r'^[A-Z0-9a-z]+$', filename))
