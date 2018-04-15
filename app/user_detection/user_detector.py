""" Uses the camera to determine when users are present in front of the head.
    Triggers state changes in the overall experience based on whether users are present
"""

import asyncio
import logging
import time

from libs.callback_handling.callback_manager import CallbackManager
from libs.config.device_config import DeviceConfig

class UserDetector:
    def __init__(self, camera_processor):
        self._cbm = CallbackManager(['first_user_entered', 'all_users_left'], self)
        self._camera_processor = camera_processor
        self._camera_processor.add_face_detected_callback(self._handle_face_found)
        self._loop = asyncio.get_event_loop()
        self._logger = logging.getLogger('user_detector')

        config = DeviceConfig.Instance()
        user_detection_config = config.options['USER_DETECTION']
        self._activate_at_face_detected_count = user_detection_config.getint('ACTIVATE_AT_FACE_DETECTED_COUNT')
        self._deactivate_at_face_detected_count = user_detection_config.getint('DEACTIVATE_AT_FACE_DETECTED_COUNT')
        self._max_face_detected_count = user_detection_config.getint('MAX_FACE_DETECTED_COUNT')
        self._user_absent_timeout = user_detection_config.getfloat('USER_ABSENT_TIMEOUT')

        self._delayed_all_users_left_trigger = None
        self._face_detected_count = 0
        self._should_quit = False
        self._user_present = False
        self._current_user_absent_countdown = 0
        self._logger.info("User Detector Initted")

    def run(self):
        self._logger.info("User Detector Running")
        self._camera_processor.run()

    def stop(self):
        self._logger.info("User Detector Stopping")
        self._cancel_delayed_callbacks()
        self._camera_processor.stop()
        self._should_quit = True

    # CALLBACKS
    # =========================================================================

    def _handle_face_found(self, results, frame):
        """ Handles any faces/eyes being found by the camera processor
        """

        self._face_detected_count += 1
        self._face_detected_count = min(self._face_detected_count, self._max_face_detected_count)
        self._logger.debug("Users in front of device: %d", self._face_detected_count)

        if self._face_detected_count >= self._activate_at_face_detected_count \
            and not self._user_present:
            self._logger.info("First user present. Triggering callback.")
            self._cbm.trigger_first_user_entered_callback()
            self._user_present = True

        self._reset_delayed_users_left_trigger()

    def _handle_face_absent(self):
        self._face_detected_count -= 1
        self._face_detected_count = max(self._face_detected_count, 0)
        self._logger.debug("No users detected for %s seconds: %d", self._user_absent_timeout, self._face_detected_count)

        if self._user_present:
            if self._face_detected_count <= self._deactivate_at_face_detected_count:
                self._logger.info("Flagging all users absent")
                self._user_present = False
                self._cbm.trigger_all_users_left_callback()
            else:
                self._queue_delayed_users_left_trigger()

    # INTERNAL HELPERS
    # =========================================================================

    # REVISE: How expensive is it to keep queuing and cancelling delayed callbacks?
    # Could just manage our own counter in here
    def _reset_delayed_users_left_trigger(self):
        """ Cancels any scheduled call to the all_users_left callback and creates
            a new one to be called after the default wait time
        """

        self._cancel_delayed_callbacks()
        self._queue_delayed_users_left_trigger()

    def _queue_delayed_users_left_trigger(self):
        """ Queues up a delayed call to handle user absence if we don't see one for an amount of time
        """

        self._delayed_all_users_left_trigger = self._loop.call_later(self._user_absent_timeout, self._handle_face_absent)

    def _cancel_delayed_callbacks(self):
        if self._delayed_all_users_left_trigger is not None:
            self._logger.debug("Cancelling existing delayed notification callback")
            self._delayed_all_users_left_trigger.cancel()
