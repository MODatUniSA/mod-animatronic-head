from enum import Enum, auto

class InteractionType(Enum):
    NONE = auto()
    IDLE = auto()
    ACTIVATING = auto()
    ACTIVE = auto()
    DEACTIVATING = auto()
