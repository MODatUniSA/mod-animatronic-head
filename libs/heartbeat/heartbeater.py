""" Periodically Sends out a heartbeat ping to the configured URL.
    Used to tell monitoring services that the code is running as expected.
"""

import asyncio
import aiohttp
import logging
from concurrent.futures import CancelledError

class Heartbeater:
    def __init__(self, url, period):
        self._url = url
        self._period      = period
        self._logger      = logging.getLogger("heartbeater")
        self._session     = None
        self._should_quit = False

    @asyncio.coroutine
    def run(self):
        """ Start the heartbeater pinging the target url
        """

        self._session = aiohttp.ClientSession()
        self._logger.debug('Heartbeat session started')

        while not self._should_quit:
            try:
                yield from self._send_heartbeat()
                yield from asyncio.sleep(self._period)
            except CancelledError:
                self._logger.debug("Task has been cancelled!")
                break
            except RuntimeError:
                self._logger.error("Heatbeat ping failed!", exc_info=True)

    def stop(self):
        self._logger.debug("Stopping Heartbeater")
        self._should_quit = True

        if self._session and not self._session.closed:
            self._logger.debug("Closing session")
            self._session.close()
        else:
            self._logger.debug("No open session to close")

    @asyncio.coroutine
    def _send_heartbeat(self):
        """ Sends the actual PUSH to the monitoring URL
        """

        self._logger.debug("Sending Heartbeat: %s", self._url)
        yield from self._session.get(self._url)
