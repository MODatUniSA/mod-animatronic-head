""" Uses the camera to determine when users are present in front of the head.
    Currently completely mocked behaviour.
"""

import asyncio
import logging
import time

from libs.callback_handling.callback_manager import CallbackManager

class UserDetector:
    def __init__(self, camera_processor):
        self._cbm = CallbackManager(['first_user_entered', 'all_users_left'], self)
        self._camera_processor = camera_processor
        self._camera_processor.add_face_detected_callback(self._handle_face_found)
        self._loop = asyncio.get_event_loop()

        self._logger = logging.getLogger('user_detector')
        # How long should we wait without seeing a user's face before deciding there are no users present?
        # TODO: Extract to config
        self._user_absent_timeout = 5
        self._delayed_all_users_left_trigger = None
        self._should_quit = False
        self._user_present = False
        self._logger.debug("User Detector Initted")

    def run(self):
        self._logger.debug("User Detector Running")
        self._camera_processor.run()

    def stop(self):
        self._logger.debug("User Detector Stopping")
        self._cancel_delayed_callbacks()
        self._camera_processor.stop()
        self._should_quit = True

    # CALLBACKS
    # =========================================================================

    def _handle_face_found(self, faces, eyes):
        """ Handles any faces/eyes being found by the camera processor
        """

        self._logger.info("User in front of device.")

        # REVISE: Probably also want to debounce this, as we may erroneously detect a face for a single frame
        # Consider a state machine that requires 2 triggers within x seconds to consider a user present
        if not self._user_present:
            self._logger.info("First user present. Triggering callback.")
            self._cbm.trigger_first_user_entered_callback()
            self._user_present = True

        self._reset_delayed_users_left_trigger()

    def _reset_delayed_users_left_trigger(self):
        """ Cancels any scheduled call to the all_users_left callback and creates
            a new one to be called after the default wait time
        """

        self._cancel_delayed_callbacks()
        self._delayed_all_users_left_trigger = self._loop.call_later(self._user_absent_timeout, self._notify_all_users_left)

    def _cancel_delayed_callbacks(self):
        if self._delayed_all_users_left_trigger is not None:
            self._logger.debug("Cancelling existing delayed notification callback")
            self._delayed_all_users_left_trigger.cancel()

    def _notify_all_users_left(self):
        self._logger.info("No users detected for %s seconds. Assuming all users left.", self._user_absent_timeout)
        self._user_present = False
        self._cbm.trigger_all_users_left_callback()
        self._delayed_all_users_left_trigger = None
