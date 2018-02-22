""" Responsible for rendering frames that the camera processor puts in its frame queue
"""

import asyncio
import logging

import cv2

from libs.config.device_config import DeviceConfig
from libs.helpers.math_helpers import center_point_ints

class FrameRenderer:
    def __init__(self, eye_controller, camera_processor):
        self._logger = logging.getLogger('frame_renderer')
        self._camera_processor = camera_processor
        eye_controller.add_target_updated_callback(self._set_eye_target)
        self._camera_processor.add_frame_processed_callback(self._display_frame)

        config = DeviceConfig.Instance()
        user_detection_config = config.options['USER_DETECTION']
        self._frame_period_seconds = user_detection_config.getfloat('FRAME_PERIOD_SECONDS')

        self._eye_target = None
        self._font = cv2.FONT_HERSHEY_SIMPLEX

    def _display_frame(self, frame):
        """ Shows the captured frame with rectangles around any faces and eyes found
        """

        self._logger.info("Displaying frame")

        # TODO: Extract drawing on frame to separate function
        # REVISE: Nosy for this class to know about the face trackers directly. May be able to decouple.
        for face_index, tracker in self._camera_processor.face_trackers.items():
            tracked_position = tracker.get_position()

            x = int(tracked_position.left())
            y = int(tracked_position.top())
            w = int(tracked_position.width())
            h = int(tracked_position.height())

            cv2.rectangle(frame,(x,y),(x+w,y+h),(255,0,0),2)

            tracked_center = center_point_ints(x-w/2,y-h/2,w,h)
            track_string = "Face: {}".format(face_index)
            # cv2.putText(frame,track_string,tracked_center.tuple, self._font, 1, (200,255,155), 2, cv2.LINE_AA)

        # Show point eyes are targeting
        cv2.circle(frame, self._eye_target, 10, (0,255,0), 8)

        frame=cv2.flip(frame,1)

        cv2.imshow('Frame', frame)

    def _set_eye_target(self, target_point):
        self._eye_target = target_point
