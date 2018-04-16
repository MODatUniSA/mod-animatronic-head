""" Helper functions for testing asyncio behaviour
"""

import time
import asyncio
import logging

class AsyncioTestFunctions:
    def __init__(self):
        self._logger = logging.getLogger('asyncio_test_functions')
        self._should_quit = False
        self._logger.debug('Test functions object initted')

    def stop(self):
        self._should_quit = True

    @asyncio.coroutine
    def output_loop_count(self, loop_seconds=1):
        """ Coroutine to run while testing async behaviour to ensure we don't accidentally block the event loop. If count output is interrupted we have blocked async ops.
        """
        count = 1
        last_time = time.time()

        self._logger.debug('Outputting Asyncio Loop')

        while not self._should_quit:
            time_diff = time.time() - last_time
            last_time = time.time()
            self._logger.debug("Loop: {}. Time Diff: {:.2f}".format(count, time_diff))
            yield from asyncio.sleep(loop_seconds)
            count += 1
