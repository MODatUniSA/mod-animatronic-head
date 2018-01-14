""" Uses the camera to determine when users are present in front of the head.
    Currently completely mocked behaviour.
"""

import asyncio
import logging

from libs.callback_handling.callback_manager import CallbackManager

# TODO: Accept camera object and use to determine user state

class UserDetector:
    def __init__(self):
        self._cbm = CallbackManager(['first_user_entered', 'all_users_left'], self)
        self._logger = logging.getLogger('user_detector')
        self._should_quit = False
        self._logger.debug("User Detector Initted")

    @asyncio.coroutine
    def run(self):
        """ DEBUG: Triggers user entered on a cycle
        """

        self._logger.debug("User Detector Running")

        while not self._should_quit:
            yield from asyncio.sleep(1)
            self._logger.info("Triggering user entered")
            self._cbm.trigger_first_user_entered_callback()
            yield from asyncio.sleep(100)

        self._logger.debug("User Detector Finished")

    def stop(self):
        self._logger.debug("User Detector Stopping")
        self._should_quit = True
