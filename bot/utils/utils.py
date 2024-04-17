import re
from pathlib import Path


# Check that string is indeed wrapped in quotes
def wrapped_in_quotes(filename: str) -> bool:
    return len(filename) >= 2 and filename.startswith('"') and filename.endswith('"')


# Check the filename, i.e.:
# - the length <= 128
# - the filename is not empty
# - filename consists of valid characters
def check_filename(filename: str) -> bool:
    return 0 < len(filename) <= 128 or bool(re.match("^[A-Za-z0-9_]+$", filename))


def get_project_root():
    return Path(__file__).parent.parent.parent