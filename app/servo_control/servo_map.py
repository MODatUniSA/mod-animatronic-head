""" Provides mapping from servo names to harware pins
"""

from enum import Enum

class ServoMap(Enum):
    JAW = 1
    LIPS_UPPER = 2
    LIPS_LOWER = 3
    LIPS_LEFT = 4
    LIPS_RIGHT = 5
