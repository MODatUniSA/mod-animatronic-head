""" Maps joystick axes to servos.
"""

from enum import Enum, auto

from app.servo_control.servo_map import ServoMap
from app.servo_control.servo_limits import ServoLimits
from app.servo_control.servo_positions import ServoPositions

class JoystickAxes(Enum):
    LEFT_STICK_X = auto()
    LEFT_STICK_Y = auto()
    RIGHT_STICK_X = auto()
    RIGHT_STICK_Y = auto()
    TRIGGERS = auto()

class JoystickServoPosition:
    """ Stores a single set of servo positions to be used by a joystick control.
        Allows simple setting of speed to move towards target positions.
    """

    def __init__(self, positions):
        """ Accepts a dictionary of { pin : { 'position' : ... }, ... }
        """
        self.positions = None
        if positions is None:
            return

        self.positions = { pin : { 'position' : position_info['position'], 'speed' : 0 }
            for pin, position_info in positions.items()
        }

    def set_speed(self, speed):
        if self.positions is None:
            return

        for pin, position_info in self.positions.items():
            position_info['speed'] = speed

class JoystickServoPositions:
    """ Stores joystick control target positions in the positive and negative directions
    """
    def __init__(self, positive_positions, negative_positions = None):
        self.positive = JoystickServoPosition(positive_positions)
        self.negative = JoystickServoPosition(negative_positions)

        all_servos = list(positive_positions.keys())
        if negative_positions is not None:
            all_servos += list(negative_positions.keys())

        self.controlled_servos = set(all_servos)

# TODO: Will need to be able to easily alter position config for animation recording
# Probably just create separate classes (e.g. JoystickServoMouthMap, JoystickServoEyesMap, etc.)
# Could use config or command line args to specify which map to use
class JoystickServoMap(dict):
    def __init__(self):
        self._build_map()

    def _build_map(self):
            # LEFT STICK Y Controls Upper + Lower Lips
        self[JoystickAxes.LEFT_STICK_Y] = JoystickServoPositions(
            {
                ServoMap.LIPS_LOWER.value : { 'position' : 1200 },
                ServoMap.LIPS_UPPER.value : { 'position' : 1800 }
            },
            {
                ServoMap.LIPS_LOWER.value : { 'position' : 1800 },
                ServoMap.LIPS_UPPER.value : { 'position' : 1700 }
            }
        )

        # LEFT STICK X Controls Lips Left and Right servos
        self[JoystickAxes.LEFT_STICK_X] = JoystickServoPositions(
            {
                ServoMap.LIPS_LEFT.value : { 'position' : 1200 },
                ServoMap.LIPS_RIGHT.value : { 'position' : 1200 }
            },
            {
                ServoMap.LIPS_LEFT.value : { 'position' : 1800 },
                ServoMap.LIPS_RIGHT.value : { 'position' : 1800 }
            }
        )

        # RIGHT STICK X Also controls Left and Right Servos, but in a different shape
        self[JoystickAxes.RIGHT_STICK_X] = JoystickServoPositions(
            {
                ServoMap.LIPS_LEFT.value : { 'position' : 1200 },
                ServoMap.LIPS_RIGHT.value : { 'position' : 1800 }
            },
            {
                ServoMap.LIPS_LEFT.value : { 'position' : 1800 },
                ServoMap.LIPS_RIGHT.value : { 'position' : 1200 }
            }
        )

        self[JoystickAxes.TRIGGERS] = JoystickServoPositions(
            {
                ServoMap.JAW.value : { 'position' : 2200 },
            },
            {
                ServoMap.JAW.value : { 'position' : 1200 },
            }
        )
