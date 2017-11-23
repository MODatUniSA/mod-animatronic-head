""" Maps phonemes to mouth shape positions. Phonemes/Positions taken from http://www.garycmartin.com/phoneme_examples.html and output of Papagayo.
"""

from enum import Enum, auto

from app.servo_control.servo_map import ServoMap

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

class PhonemeMap(dict):
    def __init__(self):
        self._build_phoneme_map()

    @staticmethod
    def to_pin_numbers(position_map):
        return { k.value: v for k, v in position_map.items() }

    def _build_phoneme_map(self):
        self ['names'] = {}
        self['pins'] = {}

        # REVISE: May want to store in ServoPositions object (extends dict), rather than dict
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

        for phoneme, positions in self['names'].items():
            self['pins'][phoneme] = type(self).to_pin_numbers(positions)
