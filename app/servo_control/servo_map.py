""" Provides mapping from servo names to harware pins
"""

# IDEA: May want to pull this mapping from a config/csv file to make it easy to swap between different head configurations

from enum import Enum

class ServoMap(Enum):
    JAW = 0
    LIPS_UPPER = 1
    LIPS_RIGHT = 2
    LIPS_LEFT = 3
    LIPS_LOWER = 4
    EYES_X = 5
    EYE_RIGHT_Y = 6
    EYE_LEFT_Y = 7
    EYELID_RIGHT_UPPER = 8
    EYELID_RIGHT_LOWER = 9
    EYELID_LEFT_UPPER = 10
    EYELID_LEFT_LOWER = 11
    EYEBROW_RIGHT = 12
    EYEBROW_LEFT = 13

MOUTH_SERVOS = [ServoMap.JAW, ServoMap.LIPS_UPPER, ServoMap.LIPS_LOWER,
ServoMap.LIPS_LEFT, ServoMap.LIPS_RIGHT]
MOUTH_SERVO_PINS = [servo.value for servo in MOUTH_SERVOS]
EYE_SERVOS = [ServoMap.EYES_X, ServoMap.EYE_LEFT_Y, ServoMap.EYE_RIGHT_Y]
EYE_SERVO_PINS = [servo.value for servo in EYE_SERVOS]
