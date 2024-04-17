import re
from pathlib import Path

def check_filename(filename: str) -> bool:
    return bool(re.match(r'^[A-Z0-9a-z]+$', filename))


def get_project_root():
    return Path(__file__).parent.parent.parent