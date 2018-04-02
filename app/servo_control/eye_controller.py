""" Controls eye servos. Can be told to target a position based on an image, so
    we can move the eyes to look at a position on an image from a webcam.
    Current unpolished behaviour is to look at the first eye of the first face,
    falling back to an estimated point between the eyes if no faces are found
"""

# REVISE: If attempting to track face, eyes freeze when no faces found. Looks unnatural.
# Would be good to drop back to animation movement. Should be able to do this using overrides.

import logging
import time
import random
from contextlib import suppress

from libs.helpers.math_helpers import lerp
from libs.config.device_config import DeviceConfig
from libs.callback_handling.callback_manager import CallbackManager

from app.servo_control.image_to_servo_position_converter import ImageToServoPositionConverter

class EyeController:
    def __init__(self, camera_processor, servo_communicator):
        self._camera_processor = camera_processor
        self._servo_communicator = servo_communicator
        self._image_to_servo_position_converter = ImageToServoPositionConverter()
        self._logger = logging.getLogger('eye_controller')
        self._cbm = CallbackManager(['target_updated'], self)
        config = DeviceConfig.Instance()
        user_detection_config = config.options['USER_DETECTION']
        self._eye_track_speed = user_detection_config.getint('EYE_TRACK_SPEED')
        self._min_track_time = user_detection_config.getfloat('MIN_TRACK_SINGLE_FACE_SECONDS')
        self._max_track_time = user_detection_config.getfloat('MAX_TRACK_SINGLE_FACE_SECONDS')

        self._target_face_id = None
        self._tracking_face_start = time.time()
        # How long to track the current face for
        self._current_tracking_time = self._max_track_time
        self._tracking = False

        self._camera_processor.add_face_detected_callback(self._on_face_detected)

    def start_tracking(self):
        """ Start tracking faces found from the webcam
        """

        self._tracking = True

    def stop_tracking(self):
        """ Stop tracking faces found from the webcam
        """

        self._tracking = False

    # CALLBACKS
    # =========================================================================

    def _on_face_detected(self, faces, frame):
        """ Called by the camera processor every time it finds at least 1 face
        """

        if not self._tracking:
            return

        # Ensure the servo position converter makes calculations with the correct image dimensions
        self._image_to_servo_position_converter.set_image_dimensions(frame.shape[0:2])

        position = self._position_to_track(faces)
        if not position:
            return

        coordinates = [
            int(position.left()),
            int(position.top()),
            int(position.width()),
            int(position.height())
        ]

        self._target_coordinates(coordinates, 0.5, 0.4)

    # INTERNAL HELPERS
    # =========================================================================

    def _position_to_track(self, faces):
        """ Returns the position for the eyes to track.
            Picks a face and attempts to target between its eyes
        """

        current_face = faces.get(self._target_face_id)
        tracking_for_seconds = time.time() - self._tracking_face_start

        if current_face and not self._should_track_new_face(faces, tracking_for_seconds):
            position = current_face.get_position()
        else:
            self._target_face_id, position = self._new_random_face(faces)
            self._tracking_face_start = time.time()
            self._current_tracking_time = random.uniform(self._min_track_time, self._max_track_time)
            self._logger.info("Changing tracked face: %s", self._target_face_id)
            self._logger.info("Tracking for %s seconds", self._current_tracking_time)

        return position

    def _should_track_new_face(self, faces, tracking_for_seconds):
        """ Returns whether we should track a new face
            based on whether there is a new face to track and if we have been tracking
            the current one for too long
        """

        return len(faces) > 1 and tracking_for_seconds > self._current_tracking_time

    def _new_random_face(self, faces):
        """ Returns a new face from the tracked collection that is not currently being targeted
        """

        face_id = None
        position = None

        if faces:
            face_list = [(k,v) for k,v in faces.items() if k != self._target_face_id]
            face_id, position_info = random.choice(face_list)
            position = position_info.get_position()

        return face_id, position

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
        self._cbm.trigger_target_updated_callback(target_point)
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
