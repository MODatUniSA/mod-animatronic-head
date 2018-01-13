""" Entry point. Creates all objects for Almost Human and kicks off the experience.
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
from app.servo_control.servo_controller import ServoController

class AHDriver:
    def __init__(self, args):
        self._should_quit              = False
        self._shutdown_on_complete     = False
        self.args                      = args
        LoggerCreator().create_logger()
        self._logger                   = LoggerCreator.logger_for('driver')

        if self.args.hardware_present:
            self._logger.info("Running Almost Human with real hardware")
            from app.servo_control.servo_communicator import ServoCommunicator
        else:
            self._logger.info("Running Almost Human with mocked hardware")
            from app.null_objects.null_servo_communicator import NullServoCommunicator as ServoCommunicator

        self.loop                      = asyncio.get_event_loop()
        self.audio_playback_controller = AudioPlaybackController()
        self.servo_communicator        = ServoCommunicator()
        self.servo_controller          = ServoController(self.servo_communicator)
        self.playback_controller       = PlaybackController(self.audio_playback_controller, self.servo_controller)

    def run(self):
        self._logger.info("Almost Human driver starting.")

        self._assign_interrupt_handler()

        try:
            # TODO: Create ExperienceController and dependencies and trigger. No longer need to call playback controller directly from here

            # TEST: Triggers a single sound + set of instructions to play for testing
            # self.playback_controller.play_content('Mod1.ogg', 'position_speed_test_min.csv')
            # self.playback_controller.play_content('Mod1.ogg', 'recorded_2017-12-08_20:57:41.csv')
            # self.playback_controller.play_content('Mod1.ogg', 'Mod1_tweaked.csv', True)

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

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument("--no-hw", dest='hardware_present', action='store_false', help="Don't attempt to communicate with hardware. Used to test behaviour when no serial device connected")
    parser.set_defaults(hardware_present=True)

    parser.add_argument("-v", dest='verbose_output', action='store_true', help="Output all logged info to the console")
    parser.set_defaults(verbose_output=False)

    AHDriver(parser.parse_args()).run()
