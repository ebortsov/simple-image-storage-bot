from enum import Enum, auto


class UserStates:

    def __init__(self, states_enum: Enum):
        self.states_enum = states_enum
        self.states = dict()

    def __getitem__(self, user_id: int) -> Enum:
        return self.states[user_id]

    def __setitem__(self, user_id: int, value) -> None:
        if not isinstance(value, self.states_enum):
            raise ValueError(f"Value must be a member of {self.states_enum.__name__}")
        self.states[user_id] = value


class States(Enum):
    MAIN = auto()
    UPLOAD_NAME_ENTERING = auto(),
    UPLOAD_PHOTO_LOADING = auto()


user_states = UserStates(states_enum=States)
