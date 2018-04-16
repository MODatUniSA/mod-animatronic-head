""" Entry point. Creates all objects for Almost Human and kicks off the experience.
"""

import asyncio
import signal
import functools
import argparse
import os
import random
import time
import threading
from concurrent.futures import CancelledError, ThreadPoolExecutor

from libs.logging.logger_creator import LoggerCreator
from libs.asyncio.test_functions import AsyncioTestFunctions
from libs.config.device_config import DeviceConfig
from libs.heartbeat.heartbeater import Heartbeater

class HBTest:
    def __init__(self, args):
        self._shutdown_on_complete     = False
        self.args                      = args
        LoggerCreator().create_logger()
        self._logger                   = LoggerCreator.logger_for('driver')

        self.loop                  = asyncio.get_event_loop()
        self.executor              = ThreadPoolExecutor(5)
        self.loop.set_default_executor(self.executor)

        config                     = DeviceConfig.Instance()
        heartbeat_config           = config.options['HEARTBEAT']
        heartbeat_url              = heartbeat_config['HEARTBEAT_PUSH_URL']
        heartbeat_period           = heartbeat_config.getfloat('HEARTBEAT_PUSH_PERIOD_SECONDS')
        self._heartbeater          = Heartbeater(heartbeat_url, heartbeat_period)
        self._tf                   = AsyncioTestFunctions()
        self._tasks = [self._heartbeater.run(), self._tf.output_loop_count(60)]

    def run(self):
        self._logger.info("HBTest starting.")
        self._assign_interrupt_handler()

        try:
            self.loop.run_until_complete(asyncio.wait(self._tasks))
        except CancelledError:
            self._logger.debug("Event loop tasks have been cancelled!")
        finally:
            # REVISE: May need to call self.executor.shutdown(wait=True)
            self._logger.debug("Closing Event Loop")
            self.loop.close()

            if self._shutdown_on_complete:
                self._logger.info("Initiating System Shutdown!")
                os.system('shutdown now')

    def stop(self):
        self._heartbeater.stop()
        list(map(lambda task: task.cancel(), asyncio.Task.all_tasks()))

    # EVENT LOOP SIGNAL HANDLING
    # ==========================================================================
    def _assign_interrupt_handler(self):
        for signame in ('SIGINT', 'SIGTERM'):
            self.loop.add_signal_handler(getattr(signal, signame),
                                    functools.partial(self.ask_exit, signame))

        self._logger.info("Event loop running forever, press Ctrl+C to interrupt.")
        self._logger.info("PID %i: send SIGINT or SIGTERM to exit.", os.getpid())

    def ask_exit(self, signame):
        self._logger.info("Got signal %s: Stopping Execution", signame)
        self.stop()

    def trigger_shutdown(self):
        self._shutdown_on_complete = True
        self.stop()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument("-v", dest='verbose_output', action='store_true', help="Output all logged info to the console")
    parser.set_defaults(verbose_output=False)

    HBTest(parser.parse_args()).run()
