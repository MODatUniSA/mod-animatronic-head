""" Maps joystick axes to servos.
"""

from enum import Enum, auto

from libs.config.device_config import DeviceConfig
from libs.helpers.list_helpers import flatten

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

class NullJoystickServoPositions:
    """ Joystick servo position returned if axis unmapped
    """
    def __init__(self):
        self.controlled_servos = []

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

    def controlled_servos(self, axes):
        """ Returns the set of servos that are controlled by the argument axes
        """

        controlled = []
        for axis in axes:
            controlled.append(self.get(axis, NullJoystickServoPositions()).controlled_servos)
        controlled = list(flatten(controlled))
        return set(controlled)

    def _build_map(self):
        config = DeviceConfig.Instance()
        joystick_control_config = config.options['JOYSTICK_CONTROL']

        for axis in JoystickAxes:
            servo_set_name = joystick_control_config.get(axis.name)
            if servo_set_name is not None:
                print("Axis: {}. Servo Set Name: {}".format(axis.name, servo_set_name))
                try:
                    self[axis] = getattr(ServoControlSets, servo_set_name)
                except AttributeError as err:
                    print("ERROR - Unknown Servo Set: {}. Skipping mapping for {}.".format(servo_set_name, axis.name))

class ServoControlSets:
    """ Holds common sets of servos for mapping to joystick axes
    """

    # NOTE: For position based control, we need the same servos to be referenced in both the +ve and -ve directions,
    #       otherwise we can't interpolate the target position

    EYES_Y = JoystickServoPositions(
        {
            ServoMap.EYE_LEFT_Y.value : { 'position' : 1440 },
            ServoMap.EYE_RIGHT_Y.value : { 'position' : 1630 }
        },
        {
            ServoMap.EYE_LEFT_Y.value : { 'position' : 1600 },
            ServoMap.EYE_RIGHT_Y.value : { 'position' : 1510 }
        }
    )

    EYES_X = JoystickServoPositions(
        {
            ServoMap.EYES_X.value : { 'position' : 1550 },
        },
        {
            ServoMap.EYES_X.value : { 'position' : 1380 },
        }
    )

    EYELIDS = JoystickServoPositions(
        {
            ServoMap.EYELID_RIGHT_UPPER.value : { 'position' : 1650 },
            ServoMap.EYELID_RIGHT_LOWER.value : { 'position' : 1430 },
            ServoMap.EYELID_LEFT_UPPER.value : { 'position' : 1400 },
            ServoMap.EYELID_LEFT_LOWER.value : { 'position' : 1500 }
        },
        {
            ServoMap.EYELID_RIGHT_UPPER.value : { 'position' : 1790 },
            ServoMap.EYELID_RIGHT_LOWER.value : { 'position' : 1250 },
            ServoMap.EYELID_LEFT_UPPER.value : { 'position' : 1260 },
            ServoMap.EYELID_LEFT_LOWER.value : { 'position' : 1720 }
        }
    )

    EYEBROWS = JoystickServoPositions(
        {
            ServoMap.EYEBROW_RIGHT.value : { 'position' : 1570 },
            ServoMap.EYEBROW_LEFT.value : { 'position' : 1570 },
        },
        {
            ServoMap.EYEBROW_RIGHT.value : { 'position' : 1600 },
            ServoMap.EYEBROW_LEFT.value : { 'position' : 1520 },
        }
    )

    JAW = JoystickServoPositions(
        {
            ServoMap.JAW.value : { 'position' : 1440 },
        },
        {
            ServoMap.JAW.value : { 'position' : 1600 },
        }
    )

    LIPS_VERTICAL = JoystickServoPositions(
        {
            ServoMap.LIPS_LOWER.value : { 'position' : 1750 },
            ServoMap.LIPS_UPPER.value : { 'position' : 1530 },
        },
        {
            ServoMap.LIPS_LOWER.value : { 'position' : 1550 },
            ServoMap.LIPS_UPPER.value : { 'position' : 1430 },
        }
    )

    LIPS_HORIZONTAL = JoystickServoPositions(
        {
            ServoMap.LIPS_RIGHT.value : { 'position' : 1220 },
            ServoMap.LIPS_LEFT.value : { 'position' : 1850 },
        },
        {
            ServoMap.LIPS_RIGHT.value : { 'position' : 1550 },
            ServoMap.LIPS_LEFT.value : { 'position' : 1530 },
        }
    )
