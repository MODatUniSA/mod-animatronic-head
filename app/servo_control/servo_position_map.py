""" Base class for position maps
"""

from app.servo_control.servo_positions import ServoPositions

class ServoPositionMap(dict):
    def __init__(self):
        self._build_map()
        super().__init__()

    @staticmethod
    def positions_to_pin_numbers(single_position_map):
        return { k.value: v for k, v in single_position_map.items() }

    @staticmethod
    def mapping_to_servo_positions(total_map):
        """ Converts a mapping of Servo Enum : Positions Dictionary -> Pin : ServoPosition
        """
        ret = {}
        for key, positions in total_map.items():
            ret[key] = ServoPositions(ServoPositionMap.positions_to_pin_numbers(positions))

        return ret

    def _build_map(self):
        raise "Implement in subclass!"
