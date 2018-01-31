""" Controls eye servos. Can be told to target a position based on an image, so
    we can move the eyes to look at a position on an image from a webcam.
    Current unpolished behaviour is to look at the first eye of the first face,
    falling back to an estimated point between the eyes if no faces are found
"""

import logging

from libs.helpers.math_helpers import lerp
from libs.config.device_config import DeviceConfig

from app.servo_control.servo_map import ServoMap
from app.servo_control.servo_positions import ServoPositions
from app.servo_control.image_to_servo_position_converter import ImageToServoPositionConverter

class EyeController:
    def __init__(self, camera_processor, servo_communicator):
        self._camera_processor = camera_processor
        self._servo_communicator = servo_communicator
        self._image_to_servo_position_converter = ImageToServoPositionConverter()
        self._logger = logging.getLogger('eye_controller')
        config = DeviceConfig.Instance()
        user_detection_config = config.options['USER_DETECTION']
        self._eye_track_speed = user_detection_config.getint('EYE_TRACK_SPEED')

        self._tracking = False

        self._camera_processor.add_face_detected_callback(self._on_face_detected)

    def start_tracking(self):
        self._tracking = True

    def stop_tracking(self):
        self._tracking = False

    # CALLBACKS
    # =========================================================================

    def _on_face_detected(self, faces, frame):
        """ Called by the camera processor every time it finds at least 1 face
        """

        if not self._tracking:
            return

        # Make sure the servo position converter makes calculations with the correct image dimensions
        self._image_to_servo_position_converter.set_image_dimensions(frame.shape[0:2])

        # Results are ordered by the time they were detected, so using the first should keep us
        # looking at the same face while it is detected
        position = next(iter(faces.values())).get_position()
        coordinates = [
            int(position.left()),
            int(position.top()),
            int(position.width()),
            int(position.height())
        ]

        self._target_coordinates(coordinates, 0.5, 0.4)

    # INTERNAL HELPERS
    # =========================================================================

    def _target_coordinates(self, coordinates, x_percent=0.5, y_percent=0.5):
        """ Target the eyes to x_percent, y_percent of the passed coordinates
            0.5 will target 1/2 way between the edges, while 0 and 1 will target
            the start and end respectively.
            Expects coordinates in the form x,y,width,height
        """

        x,y,w,h = coordinates
        x_val = int(lerp(x, x+w, x_percent))
        y_val = int(lerp(y, y+h, y_percent))
        target_point = (x_val, y_val)
        self._move_eyes_to_image_point(target_point)

    def _move_eyes_to_image_point(self, point):
        """ Moves eyes to the target point
            Expects the target point to be x,y of an image, which will be
            converted into a servo position
        """

        self._logger.debug('Moving eyes to point: %s', point)
        positions = self._image_to_servo_position_converter.to_servo_positions(point)
        positions.set_speeds(self._eye_track_speed)
        self._servo_communicator.move_to(positions)
