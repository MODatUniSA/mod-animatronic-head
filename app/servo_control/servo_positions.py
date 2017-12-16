""" Stores single set of servo positions
"""

import logging

from app.servo_control.servo_map import MOUTH_SERVO_PINS
from app.servo_control.servo_limits import ServoLimits

class ServoPositions:
    def __init__(self, positions_dict):
        """ Accepts a dict of servo positions in the format { pin : position_int, ... }
            Also accepts { pin : { position : int, speed : int } }
        """
        self._logger = logging.getLogger('servo_positions')
        self.speed_specified = False
        self._servo_limits = ServoLimits()
        self.positions = self._to_limited_positions(positions_dict)
        self.positions_str = self._to_positions_string(self.positions)
        self.positions_without_mouth = type(self)._to_positions_without_mouth(self.positions)
        self.positions_without_mouth_str = self._to_positions_string(self.positions_without_mouth)

    def merge(self, servo_positions):
        """ Merge this servo positions object with another servo_positions object.
            Positions in the other object take priority over this one.
            Returns a new object with the merged positions
        """

        merged_positions = self.positions.copy()
        merged_positions.update(servo_positions.positions)
        return type(self)(merged_positions)


    def clear_servos(self, servos):
        """ Clears the argument servos out of our positions
        """

        if len(self.positions) == 0:
            return

        for servo in servos:
            if servo in self.positions.keys():
                del(self.positions[servo])

    def _to_positions_string(self, positions):
        return ''.join("#{!s}P{!s}".format(pin,self._to_position_string(pos)) for (pin,pos) in positions.items())

    def _to_position_string(self, position):
        if isinstance(position, dict) and 'position' in position:
            # REVISE: Apply default speed if no speed present?
            self.speed_specified = True
            return '{}S{}'.format(position['position'], position['speed'])
        else:
            return str(position)


    def _to_positions_without_mouth(positions):
        return {servo: position for servo, position in positions.items() if servo not in MOUTH_SERVO_PINS}

    def _to_limited_positions(self, positions):
        """ Accepts a dict of positions and ensures each servo is within the acceptable position limits
        """

        # TODO: Need to handle possibility on None value returned if we can't apply limit. May filter here, or handle when attempting to process/send position

        return {
            pin : self._to_limited_position(pin, value)
                for pin, value in positions.items()
        }

    def _to_limited_position(self, pin, position):
        """ Accepts either an int or dict and returns the same structure with servo position limits applied
        """

        if isinstance(position, dict) and 'position' in position:
            position['position'] = self._servo_limits.to_limited_position(pin, position['position'])
            return position
        elif isinstance(position, int):
            return self._servo_limits.to_limited_position(pin, position)
        else:
            self._logger.error("Unable to construct limited servo position from: %s", position)
            return None

    def within_threshold(self, other, threshold):
        """ Returns whether the other positions are all within the threshold of this one
        """

        if other is None:
            return False

        for pin, position_info in self.positions.items():
            other_position_info = other.positions.get(pin)
            if other_position_info is None:
                return False
            if abs(position_info['position'] - other_position_info['position']) > threshold:
                return False

        return True
