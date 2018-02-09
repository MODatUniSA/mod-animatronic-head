""" Entry point. Creates all objects for Almost Human and kicks off the experience.
"""

import asyncio
import signal
import functools
import argparse
import os
import random
import time

from libs.logging.logger_creator import LoggerCreator
from libs.asyncio.test_functions import AsyncioTestFunctions
from libs.slack_integration.slack_bot import SlackBot
from libs.config.device_config import DeviceConfig

from app.playback.audio.audio_playback_controller import AudioPlaybackController
from app.playback.playback_controller import PlaybackController
from app.servo_control.servo_controller import ServoController
from app.interaction_control.experience_controller import ExperienceController
from app.interaction_control.interaction_loop_executor import InteractionLoopExecutor
from app.user_detection.user_detector import UserDetector
from app.user_detection.camera_processor import CameraProcessor
from app.servo_control.eye_controller import EyeController

class AHDriver:
    def __init__(self, args):
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

        self.loop                  = asyncio.get_event_loop()
        config                     = DeviceConfig.Instance()
        audio_playback_controller  = AudioPlaybackController()
        servo_communicator         = ServoCommunicator()
        servo_controller           = ServoController(servo_communicator)
        camera_processor           = CameraProcessor()
        eye_controller             = EyeController(camera_processor, servo_communicator)
        playback_controller        = PlaybackController(audio_playback_controller, servo_controller, eye_controller)
        interaction_loop_executor  = InteractionLoopExecutor(playback_controller)
        self._user_detector        = UserDetector(camera_processor)
        self.experience_controller = ExperienceController(interaction_loop_executor, self._user_detector)
        self._tf = AsyncioTestFunctions()
        token = config.options['SLACK']['TOKEN']
        self._slack_bot = SlackBot(token)

    def run(self):
        self._logger.info("Almost Human driver starting.")

        self._assign_interrupt_handler()

        try:
            self._slack_bot.run()
            self._user_detector.run()
            self.experience_controller.run()
            self.loop.run_forever()
        finally:
            self._logger.debug("Closing Event Loop")
            self.loop.close()

            if self._shutdown_on_complete:
                self._logger.info("Initiating System Shutdown!")
                os.system('shutdown now')

    def stop(self):
        self._slack_bot.stop()
        self.experience_controller.stop()
        self._user_detector.stop()
        # HACK: Give things time to exit gracefully. Should make the stop() functions coroutines and wait on them to complete
        time.sleep(1)
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
