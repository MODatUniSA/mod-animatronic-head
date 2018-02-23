""" Defines upper and lower limits of servos
"""

# IDEA: May want to pull this mapping from a config/csv file to make it easy to swap between different head configurations

from libs.patterns.singleton import Singleton
from app.servo_control.servo_map import ServoMap

# REVISE: Mid position is never used
class ServoLimit:
    def __init__(self, lower, upper):
        self.upper = upper
        self.lower = lower

    def to_limited_position(self, position):
        """ Returns a position within upper and lower bounds for this limit
        """

        return max(self.lower, min(position, self.upper))

@Singleton
class ServoLimits(dict):
    def __init__(self):
        self._build_limit_map()
        super().__init__()

    def to_limited_position(self, pin, position):
        """ Accepts a servo pin and position and returns a position value within limits for that servo
        """

        # TODO: Gracefully handle unmapped pin
        return self[ServoMap(pin)].to_limited_position(position)

    def _build_limit_map(self):
        self[ServoMap.JAW]                = ServoLimit(800,2200)
        self[ServoMap.LIPS_UPPER]         = ServoLimit(800,2200)
        self[ServoMap.LIPS_RIGHT]         = ServoLimit(800,2200)
        self[ServoMap.LIPS_LEFT]          = ServoLimit(800,2200)
        self[ServoMap.LIPS_LOWER]         = ServoLimit(800,2200)
        self[ServoMap.EYES_X]             = ServoLimit(800,2200)
        self[ServoMap.EYE_RIGHT_Y]        = ServoLimit(1500,1750)
        self[ServoMap.EYE_LEFT_Y]         = ServoLimit(1350,1550)
        self[ServoMap.EYELID_RIGHT_UPPER] = ServoLimit(800,2200)
        self[ServoMap.EYELID_RIGHT_LOWER] = ServoLimit(800,2200)
        self[ServoMap.EYELID_LEFT_UPPER]  = ServoLimit(800,2200)
        self[ServoMap.EYELID_LEFT_LOWER]  = ServoLimit(800,2200)
        self[ServoMap.EYEBROW_RIGHT]      = ServoLimit(800,2200)
        self[ServoMap.EYEBROW_LEFT]       = ServoLimit(800,2200)
