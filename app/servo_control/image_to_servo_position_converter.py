""" Responsible for converting a target point on an image to a set to servo
    positions
"""

from app.servo_control.servo_map import ServoMap
from libs.helpers.math_helpers import lerp

class ImageToServoPositionConverter:
    # TODO: Pull out to config, or take dynamically from captured frame
    image_height_pixels = 720
    image_width_pixels = 1280

    # REVISE: May want an object to hold this structure, rather than dicts
    servos = {
        'width' : {
            ServoMap.EYES_X : { 'min' : 0, 'max':100 },
        },
        'height' : {
            ServoMap.EYE_LEFT_Y : { 'min' : 0, 'max':100 },
            ServoMap.EYE_RIGHT_Y : { 'min' : 100, 'max':200 }
        }
    }

    @classmethod
    def _to_servo_positions(cls, point):
        """ Coverts a point on an image to a set of eye servo positions
        """

        # REVISE: This is a lot of repeated code. Extract and generalise.

        x,y = point
        x_percent = x / cls.image_width_pixels
        y_percent = y / cls.image_height_pixels

        servo_positions_dict = {}
        for servo, limits in cls.servos['width'].items():
            servo_positions_dict[servo] = int(lerp(limits['min'], limits['max'], x_percent))
        for servo, limits in cls.servos['height'].items():
            servo_positions_dict[servo] = int(lerp(limits['min'], limits['max'], y_percent))

        return ServoPositions(servo_positions_dict)
