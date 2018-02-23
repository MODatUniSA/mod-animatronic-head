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
from concurrent.futures import CancelledError

from libs.logging.logger_creator import LoggerCreator
from libs.asyncio.test_functions import AsyncioTestFunctions
from libs.config.device_config import DeviceConfig
from libs.heartbeat.heartbeater import Heartbeater

from app.playback.audio.audio_playback_controller import AudioPlaybackController
from app.playback.playback_controller import PlaybackController
from app.servo_control.servo_controller import ServoController
from app.interaction_control.experience_controller import ExperienceController
from app.interaction_control.interaction_loop_executor import InteractionLoopExecutor
from app.user_detection.user_detector import UserDetector
from app.user_detection.camera_processor import CameraProcessor
from app.user_detection.frame_renderer import FrameRenderer
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

        if self.args.slack_enabled:
            self._logger.info("Slack integration enabled")
            from libs.slack_integration.slack_bot import SlackBot
        else:
            self._logger.info("Slack integration disabled")
            from app.null_objects.null_slack_bot import NullSlackBot as SlackBot

        self.loop                  = asyncio.get_event_loop()
        config                     = DeviceConfig.Instance()
        heartbeat_config           = config.options['HEARTBEAT']
        heartbeat_url              = heartbeat_config['HEARTBEAT_PUSH_URL']
        heartbeat_period           = heartbeat_config.getfloat('HEARTBEAT_PUSH_PERIOD_SECONDS')
        self._heartbeater          = Heartbeater(heartbeat_url, heartbeat_period)
        audio_playback_controller  = AudioPlaybackController()
        servo_communicator         = ServoCommunicator()
        servo_controller           = ServoController(servo_communicator)
        camera_processor           = CameraProcessor()
        eye_controller             = EyeController(camera_processor, servo_communicator)
        if config.options['USER_DETECTION'].getboolean('DISPLAY_FRAMES'):
            frame_renderer             = FrameRenderer(eye_controller, camera_processor)
        playback_controller        = PlaybackController(audio_playback_controller, servo_controller, eye_controller)
        interaction_loop_executor  = InteractionLoopExecutor(playback_controller)
        self._user_detector        = UserDetector(camera_processor)
        self._experience_controller = ExperienceController(interaction_loop_executor, self._user_detector)
        self._tf                   = AsyncioTestFunctions()
        token = config.options['SLACK']['TOKEN']
        self._slack_bot = SlackBot(token)
        self._tasks = [self._heartbeater.run(), self._tf.output_loop_count()]

    def run(self):
        self._logger.info("Almost Human driver starting.")
        self._logger.info("AH Driver Thread: %s", threading.current_thread().name)

        self._assign_interrupt_handler()

        try:
            self._slack_bot.run()
            self._user_detector.run()
            self._experience_controller.run()
            self.loop.run_until_complete(asyncio.wait(self._tasks))
        except CancelledError:
            self._logger.debug("Event loop tasks have been cancelled!")
        finally:
            self._logger.debug("Closing Event Loop")
            self.loop.close()

            if self._shutdown_on_complete:
                self._logger.info("Initiating System Shutdown!")
                os.system('shutdown now')

    def stop(self):
        self._heartbeater.stop()
        self._slack_bot.stop()
        self._experience_controller.stop()
        self._user_detector.stop()
        # REVISE: We may want to cancel any tasks using call_soon_threadsafe
        list(map(lambda task: task.cancel(), asyncio.Task.all_tasks()))

        # HACK: Give things time to exit gracefully. Should make the stop() functions coroutines and wait on them to complete
        time.sleep(2)

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

    parser.add_argument("-no-hw", dest='hardware_present', action='store_false', help="Don't attempt to communicate with hardware. Used to test behaviour when no serial device connected")
    parser.set_defaults(hardware_present=True)

    parser.add_argument("-no-slack", dest='slack_enabled', action='store_false', help="Disable direct communication with slack")
    parser.set_defaults(slack_enabled=True)

    parser.add_argument("-v", dest='verbose_output', action='store_true', help="Output all logged info to the console")
    parser.set_defaults(verbose_output=False)

    AHDriver(parser.parse_args()).run()
