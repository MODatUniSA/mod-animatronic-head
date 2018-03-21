from enum import Enum

class InteractionType(Enum):
    NONE = 0
    IDLE = 1
    ACTIVATING = 2
    ACTIVE = 3
    DEACTIVATING = 4
