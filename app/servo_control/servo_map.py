""" Provides mapping from servo names to harware pins
"""

from enum import Enum

class ServoMap(Enum):
    JAW = 0
    LIPS_UPPER = 1
    LIPS_LOWER = 4
    LIPS_RIGHT = 2
    LIPS_LEFT = 3
    EYEBROW_LEFT = 5
    EYEBROW_RIGHT = 6

MOUTH_SERVOS = [ServoMap.JAW, ServoMap.LIPS_UPPER, ServoMap.LIPS_LOWER,
ServoMap.LIPS_LEFT, ServoMap.LIPS_RIGHT]
MOUTH_SERVO_PINS = [servo.value for servo in MOUTH_SERVOS]
