""" Maps named expressions to servo positions. Currently static, will later be sequences/animations.
"""

# REIVSE: May not use static expressions anymore, as we'll be using moving animations for expression control

from enum import Enum

from app.servo_control.servo_map import ServoMap
from app.servo_control.servo_position_map import ServoPositionMap

class Expressions(Enum):
    SURPRISED = 0
    STERN     = 1

class ExpressionMap(ServoPositionMap):
    def _build_map(self):
        self['names'] = {}
        self['pins'] = {}

        self['names'][Expressions.SURPRISED] = { ServoMap.JAW : 2000, ServoMap.LIPS_UPPER : 1300, ServoMap.LIPS_LOWER : 1700, ServoMap.LIPS_LEFT : 1300, ServoMap.LIPS_RIGHT : 1700, ServoMap.EYEBROW_LEFT : 123, ServoMap.EYEBROW_RIGHT : 456 }
        self['names'][Expressions.STERN] = { ServoMap.JAW : 1200, ServoMap.LIPS_UPPER : 1800, ServoMap.LIPS_LOWER : 1400, ServoMap.LIPS_LEFT : 1500, ServoMap.LIPS_RIGHT : 1500, ServoMap.EYEBROW_LEFT : 999, ServoMap.EYEBROW_RIGHT : 888 }

        self['pins'] = type(self).mapping_to_servo_positions(self['names'])
