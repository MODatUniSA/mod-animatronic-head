""" Defines upper and lower limits of servos
"""

# IDEA: May want to pull this mapping from a config/csv file to make it easy to swap between different head configurations

from libs.patterns.singleton import Singleton
from app.servo_control.servo_map import ServoMap

# REVISE: Mid position is never used
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
        self[ServoMap.JAW]                = ServoLimit(1440,1520,1600)
        self[ServoMap.LIPS_UPPER]         = ServoLimit(1430,1480,1530)
        self[ServoMap.LIPS_RIGHT]         = ServoLimit(1220,1385,1550)
        self[ServoMap.LIPS_LEFT]          = ServoLimit(1530,1690,1850)
        self[ServoMap.LIPS_LOWER]         = ServoLimit(1550,1650,1750)
        self[ServoMap.EYES_X]             = ServoLimit(1380,1465,1550)
        self[ServoMap.EYE_RIGHT_Y]        = ServoLimit(1510,1570,1630)
        self[ServoMap.EYE_LEFT_Y]         = ServoLimit(1440,1520,1600)
        self[ServoMap.EYELID_RIGHT_UPPER] = ServoLimit(1650,1720,1790)
        self[ServoMap.EYELID_RIGHT_LOWER] = ServoLimit(1250,1340,1430)
        self[ServoMap.EYELID_LEFT_UPPER]  = ServoLimit(1260,1330,1400)
        self[ServoMap.EYELID_LEFT_LOWER]  = ServoLimit(1500,1610,1720)
        self[ServoMap.EYEBROW_RIGHT]      = ServoLimit(1570,1585,1600)
        self[ServoMap.EYEBROW_LEFT]       = ServoLimit(1520,1545,1570)
