""" Responsible for converting a target point on an image to a set to servo
    positions. Assumes image origin is top left.
"""

import logging

from app.servo_control.servo_map import ServoMap
from app.servo_control.servo_positions import ServoPositions
from libs.helpers.math_helpers import lerp

class DimensionsNotSpecifiedError(ArithmeticError):
    default_message = "Image dimensions must be set before finding servo positions"
    def __init__(self, message=default_message):
        self.message = message

    def __str__(self):
        return repr(self.message)

class ImageToServoPositionConverter:
    def __init__(self):
        self._logger = logging.getLogger('image_to_servo_position_converter')
        self._image_height_pixels = None
        self._image_width_pixels = None

        # REVISE: May want an object to hold this structure, rather than dicts
        # EYES X min is where on the x axis the eyes should be when point is at the very top of the image
        # EYES X max is where on the x axis the eyes should be when point is at the very bottom of the image
        # Similarly, EYES y covers where the eyes should be based on horizontal position on image
        # Note that our head is mounted on its side, which is why Y axis deals with image width, and X height
        # self._servos = {
        #     'width' : {
        #         ServoMap.EYE_LEFT_Y.value : { 'min' : 1440, 'max': 1600 },
        #         ServoMap.EYE_RIGHT_Y.value : { 'min' : 1630, 'max': 1510 }
        #     },
        #     'height' : {
        #         ServoMap.EYES_X.value : { 'min' : 1550, 'max': 1380 },
        #     }
        # }

        # Going outside actual bounds to exaggerate movement
        # Servo position clamping will ensure we don't go out of bounds
        self._servos = {
            'width' : {
                ServoMap.EYE_LEFT_Y.value : { 'min' : 440, 'max': 2600 },
                ServoMap.EYE_RIGHT_Y.value : { 'min' : 2510, 'max': 630 }
            },
            'height' : {
                ServoMap.EYES_X.value : { 'min' : 2550, 'max': 380 },
            }
        }


    def set_image_dimensions(self, dimensions):
        self._logger.debug("Setting image dimensions: %s", dimensions)
        self._image_height_pixels, self._image_width_pixels = dimensions

    def to_servo_positions(self, point):
        """ Coverts a point on an image to a set of eye servo positions
        """

        if self._image_height_pixels is None or self._image_width_pixels is None:
            raise DimensionsNotSpecifiedError

        x,y = point
        servo_positions_dict = {}
        servo_positions_dict.update(self._axis_positions(x, self._image_width_pixels, self._servos['width']))
        servo_positions_dict.update(self._axis_positions(y, self._image_height_pixels, self._servos['height']))

        return ServoPositions(servo_positions_dict)

    def _axis_positions(self, value, max_possible_value, servo_infos):
        ret = {}
        percent = value / max_possible_value
        for servo, limits in servo_infos.items():
            ret[servo] = int(lerp(limits['min'], limits['max'], percent))

        return ret
