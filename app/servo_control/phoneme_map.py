""" Maps phonemes to mouth shape positions. Phonemes/Positions taken from http://www.garycmartin.com/phoneme_examples.html and output of Papagayo.
"""

# IDEA: Take mapping from CSV

from enum import Enum, auto

from app.servo_control.servo_map import ServoMap
from app.servo_control.servo_position_map import ServoPositionMap

class Phonemes(Enum):
    REST = auto()
    AI = auto()
    ETC = auto()
    E = auto()
    O = auto()
    U = auto()
    L = auto()
    FV = auto()
    MBP = auto()
    WQ = auto()
    CLOSED = auto()

class PhonemeMap(ServoPositionMap):
    def _build_map(self):
        self['names'] = {}
        self['pins'] = {}

        self['names'][Phonemes.CLOSED]  = { ServoMap.JAW : 2200, ServoMap.LIPS_UPPER : 1363, ServoMap.LIPS_LOWER : 1363, ServoMap.LIPS_LEFT : 800, ServoMap.LIPS_RIGHT : 2200 }
        self['names'][Phonemes.REST]  = { ServoMap.JAW : 2200, ServoMap.LIPS_UPPER : 1363, ServoMap.LIPS_LOWER : 1363, ServoMap.LIPS_LEFT : 800, ServoMap.LIPS_RIGHT : 2200 }
        self['names'][Phonemes.AI]    = { ServoMap.JAW : 1000, ServoMap.LIPS_UPPER : 2199, ServoMap.LIPS_LOWER : 2199, ServoMap.LIPS_LEFT : 1610, ServoMap.LIPS_RIGHT : 1389 }
        self['names'][Phonemes.ETC]   = { ServoMap.JAW : 1832, ServoMap.LIPS_UPPER : 2196, ServoMap.LIPS_LOWER : 2196, ServoMap.LIPS_LEFT : 1244, ServoMap.LIPS_RIGHT : 1755 }
        self['names'][Phonemes.E]     = { ServoMap.JAW : 1832, ServoMap.LIPS_UPPER : 2196, ServoMap.LIPS_LOWER : 2196, ServoMap.LIPS_LEFT : 1244, ServoMap.LIPS_RIGHT : 1755 }
        self['names'][Phonemes.O]     = { ServoMap.JAW : 1000, ServoMap.LIPS_UPPER : 2130, ServoMap.LIPS_LOWER : 2130, ServoMap.LIPS_LEFT : 1916, ServoMap.LIPS_RIGHT : 1083 }
        self['names'][Phonemes.U]     = { ServoMap.JAW : 2200, ServoMap.LIPS_UPPER : 2087, ServoMap.LIPS_LOWER : 2087, ServoMap.LIPS_LEFT : 1018, ServoMap.LIPS_RIGHT : 1981 }
        self['names'][Phonemes.L]     = { ServoMap.JAW : 1700, ServoMap.LIPS_UPPER : 1200, ServoMap.LIPS_LOWER : 1700, ServoMap.LIPS_LEFT : 1300, ServoMap.LIPS_RIGHT : 1700 }
        self['names'][Phonemes.FV]    = { ServoMap.JAW : 1400, ServoMap.LIPS_UPPER : 1500, ServoMap.LIPS_LOWER : 1500, ServoMap.LIPS_LEFT : 1500, ServoMap.LIPS_RIGHT : 1500 }
        self['names'][Phonemes.MBP]   = { ServoMap.JAW : 2200, ServoMap.LIPS_UPPER : 933, ServoMap.LIPS_LOWER : 933, ServoMap.LIPS_LEFT : 1039, ServoMap.LIPS_RIGHT : 1960 }
        self['names'][Phonemes.WQ]    = { ServoMap.JAW : 2200, ServoMap.LIPS_UPPER : 1151, ServoMap.LIPS_LOWER : 1151, ServoMap.LIPS_LEFT : 2199, ServoMap.LIPS_RIGHT : 800 }

        self['pins'] = type(self).mapping_to_servo_positions(self['names'])
