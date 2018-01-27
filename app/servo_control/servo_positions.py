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
        self._servo_limits = ServoLimits.Instance()
        self.positions = type(self)._uniform_position_structure(positions_dict)
        self.positions = self._to_limited_positions(self.positions)
        self.positions_str = self._to_positions_string(self.positions)

    @classmethod
    def _uniform_position_structure(cls, positions_dict):
        """ Takes formats { pin : position_int, ... } and { pin : { position : int, speed : int } }
            And converts the former to the latter
        """

        positions = {}
        for pin, position_info in positions_dict.items():
            if isinstance(position_info, dict):
                positions[pin] = position_info
            else:
                positions[pin] = { 'position' : position_info }

        return positions

    def positions_without(self, without):
        """ Returns the positions, except for those servos specified in the args
        """

        return { pin : value for pin, value in self.positions.items() if pin not in without }

    def to_str(self, without=None):
        """ Returns a string of positions, except those specified in the args if provided
        """

        if without is None or len(without) == 0:
            return self._to_positions_string(self.positions)

        return self._to_positions_string(self.positions_without(without))

    def merge(self, servo_positions):
        """ Merge this servo positions object with another servo_positions object.
            Positions in the other object take priority over this one.
            Returns a new object with the merged positions
        """

        merged_positions = self.positions.copy()
        merged_positions.update(servo_positions.positions)
        return type(self)(merged_positions)


    def set_speeds(self, speed):
        for pin, position_info in self.positions.items():
            position_info['speed'] = speed

    def clear_servos(self, servos):
        """ Clears the argument servos out of our positions
        """

        if len(self.positions) == 0:
            return

        for servo in servos:
            if servo in self.positions.keys():
                del(self.positions[servo])

    # REVISE: May also want to compare speed values
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

    # INTERNAL HELPERS
    # =========================================================================

    def _to_positions_string(self, positions):
        return ''.join("#{!s}P{!s}".format(pin,self._to_position_string(pos)) for (pin,pos) in positions.items())

    def _to_position_string(self, position):
        if isinstance(position, dict) and 'position' in position:
            pos_str = str(position['position'])
            if 'speed' in position:
                self.speed_specified = True
                pos_str = '{}S{}'.format(pos_str, position['speed'])
            return pos_str

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
        else:
            self._logger.error("Unable to construct limited servo position from: %s", position)
            return None
