from enum import Enum

class InteractionType(Enum):
    NONE = 0
    IDLE = 1
    ACTIVATING = 2
    INTERRUPTED_ACTIVATING = 3
    ACTIVE = 4
    DEACTIVATING = 5
    INTERRUPTED_DEACTIVATING = 6
