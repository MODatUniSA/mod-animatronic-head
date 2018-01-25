""" Maps phonemes to mouth shape positions. Phonemes/Positions taken from http://www.garycmartin.com/phoneme_examples.html and output of Papagayo.
"""

# TODO: All phonemes currently match the prototype mouth. Update for new head.
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

        self['names'][Phonemes.CLOSED]  = { ServoMap.JAW : 1200, ServoMap.LIPS_UPPER : 1800, ServoMap.LIPS_LOWER : 1400, ServoMap.LIPS_LEFT : 1500, ServoMap.LIPS_RIGHT : 1500 }
        self['names'][Phonemes.REST]  = { ServoMap.JAW : 1500, ServoMap.LIPS_UPPER : 1500, ServoMap.LIPS_LOWER : 1500, ServoMap.LIPS_LEFT : 1500, ServoMap.LIPS_RIGHT : 1500 }
        self['names'][Phonemes.AI]    = { ServoMap.JAW : 2000, ServoMap.LIPS_UPPER : 1500, ServoMap.LIPS_LOWER : 1800, ServoMap.LIPS_LEFT : 1500, ServoMap.LIPS_RIGHT : 1500 }
        self['names'][Phonemes.ETC]   = { ServoMap.JAW : 1500, ServoMap.LIPS_UPPER : 1500, ServoMap.LIPS_LOWER : 1700, ServoMap.LIPS_LEFT : 1700, ServoMap.LIPS_RIGHT : 1300 }
        self['names'][Phonemes.E]     = { ServoMap.JAW : 1800, ServoMap.LIPS_UPPER : 1500, ServoMap.LIPS_LOWER : 1800, ServoMap.LIPS_LEFT : 1700, ServoMap.LIPS_RIGHT : 1300 }
        self['names'][Phonemes.O]     = { ServoMap.JAW : 2000, ServoMap.LIPS_UPPER : 1300, ServoMap.LIPS_LOWER : 1700, ServoMap.LIPS_LEFT : 1300, ServoMap.LIPS_RIGHT : 1700 }
        self['names'][Phonemes.U]     = { ServoMap.JAW : 1700, ServoMap.LIPS_UPPER : 1300, ServoMap.LIPS_LOWER : 1900, ServoMap.LIPS_LEFT : 1300, ServoMap.LIPS_RIGHT : 1700 }
        self['names'][Phonemes.L]     = { ServoMap.JAW : 1500, ServoMap.LIPS_UPPER : 1200, ServoMap.LIPS_LOWER : 1700, ServoMap.LIPS_LEFT : 1300, ServoMap.LIPS_RIGHT : 1700 }
        self['names'][Phonemes.FV]    = { ServoMap.JAW : 1200, ServoMap.LIPS_UPPER : 1500, ServoMap.LIPS_LOWER : 1500, ServoMap.LIPS_LEFT : 1500, ServoMap.LIPS_RIGHT : 1500 }
        self['names'][Phonemes.MBP]   = { ServoMap.JAW : 1200, ServoMap.LIPS_UPPER : 1800, ServoMap.LIPS_LOWER : 1400, ServoMap.LIPS_LEFT : 1500, ServoMap.LIPS_RIGHT : 1500 }
        self['names'][Phonemes.WQ]    = { ServoMap.JAW : 1200, ServoMap.LIPS_UPPER : 1800, ServoMap.LIPS_LOWER : 1400, ServoMap.LIPS_LEFT : 1300, ServoMap.LIPS_RIGHT : 1700 }

        self['pins'] = type(self).mapping_to_servo_positions(self['names'])
