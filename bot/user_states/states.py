from enum import Enum, auto
from collections import defaultdict

# Class wrapper around dict, so I can add some additional features later
class UserStates:

    def __init__(self, states_enum: Enum, default_state: Enum | None = None):
        if default_state and not isinstance(default_state, states_enum):
            raise ValueError(f"Value must be a member of {self.states_enum.__name__}")

        self.states = defaultdict(lambda: default_state) if default_state else dict()
        self.states_enum = states_enum

    def __getitem__(self, user_id: int) -> Enum:
        return self.states[user_id]

    def __setitem__(self, user_id: int, value) -> None:
        if not isinstance(value, self.states_enum):
            raise ValueError(f"Value must be a member of {self.states_enum.__name__}")
        self.states[user_id] = value


class States(Enum):
    MAIN = auto()
    UPLOAD_NAME_ENTERING = auto(),
    UPLOAD_PHOTO_LOADING = auto(),
    DELETE_PHOTO = auto()


user_states = UserStates(states_enum=States, default_state=States.MAIN)
