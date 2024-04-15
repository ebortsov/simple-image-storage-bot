from enum import Enum, auto

# TODO: create some single class for 'text enter' stuff


class UploadState(Enum):
    NOT_STARTED = auto(),
    ENTERING_NAME = auto(),
    UPLOADING_PHOTO = auto()


_users_upload_state = dict()


def change_upload_status(user_id: str, upload_state: UploadState) -> None:
    _users_upload_state[user_id] = upload_state


class DeleteState(Enum):
    NOT_STARTED = auto()
    ENTERING_NAME = auto(),
    UPLOADING_PHOTO = auto()


_users_delete_state = dict()


def change_delete_status(user_id: str, upload_stade: DeleteState) -> None:
    _users_delete_state[user_id] = upload_stade


def drop_states(user_id: str) -> None:
    change_delete_status(user_id, DeleteState.NOT_STARTED)
    change_upload_status(user_id, UploadState.NOT_STARTED)