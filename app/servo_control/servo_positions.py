""" Stores single set of servo positions
"""

from app.servo_control.servo_map import MOUTH_SERVO_PINS
from app.servo_control.servo_limits import ServoLimits

class ServoPositions:
    def __init__(self, positions_dict):
        """ Accepts a dict of servo positions in the format { pin : position, ... }
        """
        self._servo_limits = ServoLimits()
        self.positions_raw = positions_dict
        self.positions = self._to_limited_positions(self.positions_raw)
        self.positions_str = type(self)._to_position_string(self.positions)
        self.positions_without_mouth = type(self)._to_positions_without_mouth(self.positions)
        self.positions_without_mouth_str = type(self)._to_position_string(self.positions_without_mouth)

    @staticmethod
    def _to_position_string(positions):
        return ''.join("#{!s}P{!s}".format(pin,post) for (pin,post) in positions.items())

    def _to_positions_without_mouth(positions):
        return {servo: position for servo, position in positions.items() if servo not in MOUTH_SERVO_PINS}

    def _to_limited_positions(self, positions):
        """ Accepts a dict of positions and ensures each servo is within the acceptable position limits
        """

        return {
            pin : self._servo_limits.to_limited_position(pin, value)
                for pin, value in positions.items()
        }
