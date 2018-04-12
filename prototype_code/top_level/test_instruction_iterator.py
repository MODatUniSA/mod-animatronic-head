""" Entry point. Creates all objects for Almost Human and kicks off the experience.
"""

import asyncio
import signal
import functools
import argparse
import os
import random

from libs.logging.logger_creator import LoggerCreator
from libs.asyncio.test_functions import AsyncioTestFunctions

from app.servo_control.instruction_list_builder import InstructionListBuilder

class IITester:
    def __init__(self, args):
        self._should_quit              = False
        self._shutdown_on_complete     = False
        self.args                      = args
        LoggerCreator().create_logger()
        self._logger                   = LoggerCreator.logger_for('driver')

        self.loop                      = asyncio.get_event_loop()
        instruction_list = InstructionListBuilder().build('pseq_load_test/ps_1_1.csv')
        instruction_iterator_info = InstructionListBuilder.create_iterator(instruction_list)
        self.instruction_iterator = instruction_iterator_info['iterator']
        import pdb; pdb.set_trace()

    def run(self):
        self._logger.info("Starting.")

        self._assign_interrupt_handler()
        tasks = [
        ]

        try:
            # self.loop.run_until_complete(asyncio.wait(tasks))
            self.instruction_iterator.iterate_instructions()
            self.loop.run_forever()
        finally:
            self._logger.debug("Closing Event Loop")
            self.loop.close()

            if self._shutdown_on_complete:
                self._logger.info("Initiating System Shutdown!")
                os.system('shutdown now')

    @asyncio.coroutine
    def stop(self):
        # FIXME: Should make stop corouines and yield from to ensure they all clean up properly
        # self.playback_controller.stop()
        self._logger.info("Stopping everything")
        self.instruction_iterator.stop()
        # TEST: Give the coroutine time to stop
        yield from asyncio.sleep(2)
        self._should_quit = True
        self.loop.stop()

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
        asyncio.ensure_future(self.stop())


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument("--no-hw", dest='hardware_present', action='store_false', help="Don't attempt to communicate with hardware. Used to test behaviour when no serial device connected")
    parser.set_defaults(hardware_present=True)

    parser.add_argument("-v", dest='verbose_output', action='store_true', help="Output all logged info to the console")
    parser.set_defaults(verbose_output=False)

    IITester(parser.parse_args()).run()
