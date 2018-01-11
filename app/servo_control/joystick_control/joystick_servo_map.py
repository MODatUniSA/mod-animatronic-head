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

    @classmethod
    def interpolate_positions(cls, servo_positions_1, servo_positions_2, percentage):
        """ Interpolates between the argument positions by the argument percentage and returns
            the resulting JoystickServoPosition object.
            Percentage should be 0 <= p <= 1
        """

        interpolated_positions = {}
        for pin, position_info in servo_positions_1.positions.items():
            pos_1 = position_info['position']
            pos_2 = servo_positions_2.positions[pin]['position']

            interpolated = int((percentage * pos_2) + ((1-percentage) * pos_1))
            interpolated_positions[pin] = { 'position' : interpolated }

        return cls(interpolated_positions)

class JoystickServoPositions:
    """ Stores joystick control target positions in the positive and negative directions
    """
    def __init__(self, positive_positions, negative_positions):
        self._validate_servos(positive_positions, negative_positions)

        self.positive = JoystickServoPosition(positive_positions)
        self.negative = JoystickServoPosition(negative_positions)
        self.neutral = JoystickServoPosition.interpolate_positions(self.negative, self.positive, 0.5)
        self.controlled_servos = list(positive_positions.keys())

    def interpolated_position_for_percentage(self, percentage):
        """ Returns a new JoystickServoPosition object with target positions between the +ve and -ve mapped positions
            -1 <= percentage <= 1
        """

        end_point = self.positive if percentage >=0 else self.negative
        percentage = max(min(abs(percentage), 1), 0)
        return JoystickServoPosition.interpolate_positions(self.neutral, end_point, percentage)

    def _validate_servos(self, positive, negative):
        """ Ensures both +ve and -ve position maps have identical keys
        """

        if list(positive.keys()) != list(negative.keys()):
            raise KeyError('Joystick Servo Positions must drive the same servos in both positive and negative directions')

class JoystickServoMap(dict):
    def __init__(self):
        self._build_map()

    def _build_map(self):
        # LEFT STICK Y Controls Upper + Lower Lips
        # NOTE: For position based control, we need the same servos to be referenced in both the +ve and -ve directions,
        #       otherwise we can't interpolate the target position
        self[JoystickAxes.LEFT_STICK_Y] = JoystickServoPositions(
            {
                ServoMap.LIPS_LOWER.value : { 'position' : 1800 },
                ServoMap.LIPS_UPPER.value : { 'position' : 1700 }
            },
            {
                ServoMap.LIPS_LOWER.value : { 'position' : 1200 },
                ServoMap.LIPS_UPPER.value : { 'position' : 1800 }
            }
        )

        # RIGHT STICK X controls Left and Right Servos to pinch/spread
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

        # RIGHT STICK Y Controls Upper/Lower Lips + Jaw
        self[JoystickAxes.RIGHT_STICK_Y] = JoystickServoPositions(
            {
                ServoMap.LIPS_LOWER.value : { 'position' : 1800 },
                ServoMap.LIPS_UPPER.value : { 'position' : 1700 },
                ServoMap.JAW.value : { 'position' : 2200 }
            },
            {
                ServoMap.LIPS_LOWER.value : { 'position' : 1200 },
                ServoMap.LIPS_UPPER.value : { 'position' : 1800 },
                ServoMap.JAW.value : { 'position' : 1200 }
            }
        )
