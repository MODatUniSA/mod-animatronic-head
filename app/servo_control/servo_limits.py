""" Defines upper and lower limits of servos
"""

from libs.patterns.singleton import Singleton
from app.servo_control.servo_map import ServoMap

class ServoLimit:
    def __init__(self, lower, mid, upper):
        self.upper = upper
        self.lower = lower
        self.mid   = mid

    def to_limited_position(self, position):
        """ Returns a position within upper and lower bounds for this limit
        """

        return max(self.lower, min(position, self.upper))

@Singleton
class ServoLimits(dict):
    def __init__(self):
        self._build_limit_map()

    def to_limited_position(self, pin, position):
        """ Accepts a servo pin and position and returns a position value within limits for that servo
        """

        # TODO: Gracefully handle unmapped pin
        return self[ServoMap(pin)].to_limited_position(position)

    def _build_limit_map(self):
        self[ServoMap.JAW] = ServoLimit(1200, 1500, 2200)
        self[ServoMap.LIPS_UPPER] = ServoLimit(1200, 1500, 1800)
        self[ServoMap.LIPS_LOWER] = ServoLimit(1200, 1500, 1800)
        self[ServoMap.LIPS_LEFT] = ServoLimit(1300, 1500, 1700)
        self[ServoMap.LIPS_RIGHT] = ServoLimit(1300, 1500, 1700)
        # PLACEHOLDER LIMITS - To be replaced with actual values from hardware
        self[ServoMap.EYEBROW_LEFT] = ServoLimit(0, 1000, 2000)
        self[ServoMap.EYEBROW_RIGHT] = ServoLimit(0, 1000, 2000)
        self[ServoMap.EYE_LEFT_X] = ServoLimit(0, 1000, 2000)
        self[ServoMap.EYE_LEFT_Y] = ServoLimit(0, 1000, 2000)
        self[ServoMap.EYE_RIGHT_X] = ServoLimit(0, 1000, 2000)
        self[ServoMap.EYE_RIGHT_Y] = ServoLimit(0, 1000, 2000)
