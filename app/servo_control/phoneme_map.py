""" Maps phonemes to mouth shape positions. Phonemes/Positions taken from http://www.garycmartin.com/phoneme_examples.html and output of Papagayo.
"""

from enum import Enum

from app.servo_control.servo_map import ServoMap

class Phonemes(Enum):
    REST = 0
    AI = 1
    ETC = 2
    E = 3
    O = 4
    U = 5
    FV = 6
    MBP = 7
    # Very similar to 0, but jaw further open. Should we try to encompass jaw extension in phoneme map?
    WQ = 8

class PhonemeMap(dict):
    def __init__(self):
        self._build_phoneme_map()

    @staticmethod
    def to_pin_numbers(position_map):
        return { k.value: v for k, v in position_map.items() }

    # TODO: Set servo values to correct positions
    def _build_phoneme_map(self):
        self ['names'] = {}
        self['pins'] = {}

        self['names'][Phonemes.REST]    = { ServoMap.LIPS_UPPER : 0, ServoMap.LIPS_LOWER : 0, ServoMap.LIPS_LEFT : 0, ServoMap.LIPS_RIGHT : 0 }
        self['names'][Phonemes.AI]      = { ServoMap.LIPS_UPPER : 0, ServoMap.LIPS_LOWER : 0, ServoMap.LIPS_LEFT : 0, ServoMap.LIPS_RIGHT : 0 }
        self['names'][Phonemes.ETC]     = { ServoMap.LIPS_UPPER : 0, ServoMap.LIPS_LOWER : 0, ServoMap.LIPS_LEFT : 0, ServoMap.LIPS_RIGHT : 0 }
        self['names'][Phonemes.E]       = { ServoMap.LIPS_UPPER : 0, ServoMap.LIPS_LOWER : 0, ServoMap.LIPS_LEFT : 0, ServoMap.LIPS_RIGHT : 0 }
        self['names'][Phonemes.O]       = { ServoMap.LIPS_UPPER : 0, ServoMap.LIPS_LOWER : 0, ServoMap.LIPS_LEFT : 0, ServoMap.LIPS_RIGHT : 0 }
        self['names'][Phonemes.U]       = { ServoMap.LIPS_UPPER : 0, ServoMap.LIPS_LOWER : 0, ServoMap.LIPS_LEFT : 0, ServoMap.LIPS_RIGHT : 0 }
        self['names'][Phonemes.FV]      = { ServoMap.LIPS_UPPER : 0, ServoMap.LIPS_LOWER : 0, ServoMap.LIPS_LEFT : 0, ServoMap.LIPS_RIGHT : 0 }
        self['names'][Phonemes.MBP]     = { ServoMap.LIPS_UPPER : 0, ServoMap.LIPS_LOWER : 0, ServoMap.LIPS_LEFT : 0, ServoMap.LIPS_RIGHT : 0 }
        self['names'][Phonemes.WQ]      = { ServoMap.LIPS_UPPER : 0, ServoMap.LIPS_LOWER : 0, ServoMap.LIPS_LEFT : 0, ServoMap.LIPS_RIGHT : 0 }

        for phoneme, positions in self['names'].items():
            self['pins'][phoneme] = type(self).to_pin_numbers(positions)
