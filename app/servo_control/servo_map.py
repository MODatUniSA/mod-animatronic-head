""" Provides mapping from servo names to harware pins
"""

from enum import Enum

class ServoMap(Enum):
    JAW = 0
    LIPS_UPPER = 1
    LIPS_LOWER = 2
    LIPS_RIGHT = 3
    LIPS_LEFT = 4
