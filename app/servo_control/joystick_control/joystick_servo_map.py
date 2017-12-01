""" Maps joystick axes to servos.
"""

from enum import Enum, auto

from app.servo_control.servo_map import ServoMap
from app.servo_control.servo_limits import ServoLimits

class JoystickAxes(Enum):
    LEFT_STICK_X = auto()
    LEFT_STICK_Y = auto()
    RIGHT_STICK_X = auto()
    RIGHT_STICK_Y = auto()

class JoystickServoMap(dict):
    def __init__(self):
        self._build_map()

    def _build_map(self):
        self[JoystickAxes.LEFT_STICK_X] = ServoMap.LIPS_LOWER
        self[JoystickAxes.LEFT_STICK_Y] = ServoMap.LIPS_UPPER
        self[JoystickAxes.RIGHT_STICK_X] = ServoMap.LIPS_LEFT
        self[JoystickAxes.RIGHT_STICK_Y] = ServoMap.LIPS_RIGHT

        # REVISE: Could acutally map to a ServoPosition object, which would allow a single stick to move mulitple servos towards a fixed position. Will need to confirm how this should work with Marshal
        # self[JoystickAxes.LEFT_STICK_X] = { 'positive' : ServoPositions({ServoMap.LIPS_LOWER.value : 1200, ServoMap.LIPS_UPPER.value : 1700}), 'negative' : ... }
