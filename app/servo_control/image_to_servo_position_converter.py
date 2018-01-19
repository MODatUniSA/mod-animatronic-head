""" Responsible for converting a target point on an image to a set to servo
    positions
"""

from app.servo_control.servo_map import ServoMap
from libs.maths.math_helper import lerp

class ImageToServoPositionConverter:
    def __init__(self):
        # TODO: Pull out to config, or take dynamically from captured frame
        self._image_height_pixels = 720
        self._image_width_pixels = 1280

        # REVISE: May want an object to hold this structure, rather than dicts
        # Could hold functionality for converting image point to servo position
        self._servos = {
            'width' : {
                ServoMap.EYE_LEFT_X : { 'min' : 0, 'max':100 },
                ServoMap.EYE_RIGHT_X : { 'min' : 100, 'max':200 }
            },
            'height' : {
                ServoMap.EYE_LEFT_Y : { 'min' : 0, 'max':100 },
                ServoMap.EYE_RIGHT_Y : { 'min' : 100, 'max':200 }
            }
        }

    def _to_servo_position(self, point):
        """ Coverts a point on an image to a set of eye servo positions
        """

        # REVISE: This is a lot of repeated code. Try to extract and generalise

        x,y = point
        x_percent = x / self._image_width_pixels
        y_percent = y / self._image_height_pixels

        servo_positions_dict = {}
        for servo, limits in self._servos['width'].items():
            servo_positions_dict[servo] = int(MathHelper.lerped(limits['min'], limits['max'], x_percent))
        for servo, limits in self._servos['height'].items():
            servo_positions_dict[servo] = int(MathHelper.lerped(limits['min'], limits['max'], y_percent))

        return ServoPositions(servo_positions_dict)
