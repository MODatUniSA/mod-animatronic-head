""" Entry point. Creates all objects and kicks off experience.
"""

import asyncio
import signal
import functools
import argparse
import os
import random

from libs.logging.logger_creator import LoggerCreator

from app.playback.audio.audio_playback_controller import AudioPlaybackController
from app.playback.playback_controller import PlaybackController

class AHDriver:
    def __init__(self, args):
        self._should_quit              = False
        self._shutdown_on_complete     = False
        self.args                      = args
        LoggerCreator().create_logger()
        self._logger                   = LoggerCreator.logger_for('driver')

        if self.args.hardware_present:
            self._logger.info("Running Almost Human with real hardware")
        else:
            self._logger.info("Running Almost Human with mocked hardware")

        self.loop                      = asyncio.get_event_loop()
        self.audio_playback_controller = AudioPlaybackController()
        self.playback_controller       = PlaybackController(self.audio_playback_controller, None)

    def run(self):
        self._logger.info("Almost Human driver starting.")

        self._assign_interrupt_handler()

        try:
            # TEST: Triggers a single sound to play for testing
            self.playback_controller.play_content('Mod1.ogg', None)
            self.loop.run_forever()
        finally:
            self._logger.debug("Closing Event Loop")
            self.loop.close()

            if self._shutdown_on_complete:
                self._logger.info("Initiating System Shutdown!")
                os.system('shutdown now')

    def stop(self):
        self.playback_controller.stop()
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
        self.stop()

    def trigger_shutdown(self):
        self._shutdown_on_complete = True
        self.stop()

    # INTERNAL METHODS
    # =========================================================================

    @asyncio.coroutine
    def output_loop_count(self):
        """ Coroutine to run while testing async behaviour to ensure we don't accidentally block the event loop. If count output is interrupted we have blocked async ops.
        """
        count = 1
        last_time = time.time()

        while not self._should_quit:
            time_diff = time.time() - last_time
            last_time = time.time()
            self._logger.debug("Loop: {}. Time Diff: {:.2f}".format(count, time_diff))
            yield from asyncio.sleep(1)
            count += 1

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument("--no-hw", dest='hardware_present', action='store_false', help="Don't attempt to communicate with hardware. Used to test behaviour when no serial device connected")
    parser.set_defaults(hardware_present=True)

    parser.add_argument("-v", dest='verbose_output', action='store_true', help="Output all logged info to the console")
    parser.set_defaults(verbose_output=False)

    AHDriver(parser.parse_args()).run()
