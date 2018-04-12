""" Testing multiprocessing behaviour
"""

import asyncio
from concurrent.futures import ProcessPoolExecutor
import time
import os
import logging

from libs.config.device_config import DeviceConfig

class MpTest:
    def __init__(self):
        self._q      = None
        self._logger = None
        self._frame_period_seconds = None

    @asyncio.coroutine
    def run(self, loop, q):
        yield from loop.run_in_executor(ProcessPoolExecutor(), self._perform_run, q)

    def _perform_run(self, q):
        self._q = q
        self._logger = logging.getLogger('mp_test')
        self._logger.debug("Child PID: %i", os.getpid())
        self._load_config()
        self._logger.debug("Frame Period Seconds: %s",self._frame_period_seconds)

        while True:
            try:
                self._count()
            except RuntimeError:
                print("Error caught in Test executor")

    def _count(self):
        count = 0
        while True:
            self._q.put_nowait("Count: {}".format(count))
            print("MPTest: {}".format(count))
            count += 1
            time.sleep(2)
        print("Mp Test Finished")


    def _load_config(self):
        config = DeviceConfig.Instance()
        user_detection_config = config.options['USER_DETECTION']
        self._frame_period_seconds = user_detection_config.getfloat('FRAME_PERIOD_SECONDS')
