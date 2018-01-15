from enum import Enum, auto

# REVISE: May not need FIXED or RANDOM.

class EyeControlType(Enum):
    NONE = auto()
    TRACK = auto()
    INHERIT = auto()
    FIXED = auto()
    RANDOM = auto()
