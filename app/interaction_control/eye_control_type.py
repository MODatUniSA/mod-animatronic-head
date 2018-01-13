from enum import Enum, auto

class EyeControlType(Enum):
    NONE = auto()
    TRACK = auto()
    INHERIT = auto()
    FIXED = auto()
    RANDOM = auto()
