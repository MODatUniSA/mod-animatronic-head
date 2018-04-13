""" Maps phonemes to mouth shape positions. Phonemes/Positions taken from http://www.garycmartin.com/phoneme_examples.html and output of Papagayo.
"""

# IDEA: Take mapping from CSV

from enum import Enum

from app.servo_control.servo_map import ServoMap
from app.servo_control.servo_position_map import ServoPositionMap

class Phonemes(Enum):
    REST = 0
    AI = 1
    ETC = 2
    E = 3
    O = 4
    U = 5
    L = 6
    FV = 7
    MBP = 8
    WQ = 9
    CLOSED = 10

class PhonemeMap(ServoPositionMap):
    def _build_map(self):
        self['names'] = {}
        self['pins'] = {}

        self['names'][Phonemes.CLOSED]  = { ServoMap.JAW : 2200, ServoMap.LIPS_UPPER : 1363, ServoMap.LIPS_LOWER : 1363, ServoMap.LIPS_LEFT : 800, ServoMap.LIPS_RIGHT : 2200 }
        self['names'][Phonemes.REST]  = { ServoMap.JAW : 2200, ServoMap.LIPS_UPPER : 1363, ServoMap.LIPS_LOWER : 1363, ServoMap.LIPS_LEFT : 800, ServoMap.LIPS_RIGHT : 2200 }
        self['names'][Phonemes.AI]    = { ServoMap.JAW : 1000, ServoMap.LIPS_UPPER : 2199, ServoMap.LIPS_LOWER : 2199, ServoMap.LIPS_LEFT : 800, ServoMap.LIPS_RIGHT : 2200 }
        self['names'][Phonemes.ETC]   = { ServoMap.JAW : 1832, ServoMap.LIPS_UPPER : 2196, ServoMap.LIPS_LOWER : 2196, ServoMap.LIPS_LEFT : 800, ServoMap.LIPS_RIGHT : 2200 }
        self['names'][Phonemes.E]     = { ServoMap.JAW : 1832, ServoMap.LIPS_UPPER : 2196, ServoMap.LIPS_LOWER : 2196, ServoMap.LIPS_LEFT : 800, ServoMap.LIPS_RIGHT : 2200 }
        self['names'][Phonemes.O]     = { ServoMap.JAW : 1000, ServoMap.LIPS_UPPER : 2130, ServoMap.LIPS_LOWER : 2130, ServoMap.LIPS_LEFT : 1916, ServoMap.LIPS_RIGHT : 1083 }
        self['names'][Phonemes.U]     = { ServoMap.JAW : 1859, ServoMap.LIPS_UPPER : 1024, ServoMap.LIPS_LOWER : 1024, ServoMap.LIPS_LEFT : 2112, ServoMap.LIPS_RIGHT : 887 }
        self['names'][Phonemes.L]     = { ServoMap.JAW : 1190, ServoMap.LIPS_UPPER : 2105, ServoMap.LIPS_LOWER : 2105, ServoMap.LIPS_LEFT : 1014, ServoMap.LIPS_RIGHT : 1985 }
        self['names'][Phonemes.FV]    = { ServoMap.JAW : 1663, ServoMap.LIPS_UPPER : 1260, ServoMap.LIPS_LOWER : 1260, ServoMap.LIPS_LEFT : 817, ServoMap.LIPS_RIGHT : 2182 }
        self['names'][Phonemes.MBP]   = { ServoMap.JAW : 2200, ServoMap.LIPS_UPPER : 933, ServoMap.LIPS_LOWER : 933, ServoMap.LIPS_LEFT : 1039, ServoMap.LIPS_RIGHT : 1960 }
        self['names'][Phonemes.WQ]    = { ServoMap.JAW : 2200, ServoMap.LIPS_UPPER : 1151, ServoMap.LIPS_LOWER : 1151, ServoMap.LIPS_LEFT : 2199, ServoMap.LIPS_RIGHT : 800 }

        self['pins'] = type(self).mapping_to_servo_positions(self['names'])
