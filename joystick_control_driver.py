""" Entry point. Creates all objects for Almost Human and kicks off the experience.
"""

import asyncio
import signal
import functools
import argparse
import os
import random

import pygame

from libs.logging.logger_creator import LoggerCreator
from app.servo_control.joystick_control.joystick_servo_controller import JoystickServoController
from app.servo_control.servo_controller import ServoController

class JoystickControlDriver:
    def __init__(self, args):
        self.args                      = args
        LoggerCreator().create_logger()
        self._logger                   = LoggerCreator.logger_for('driver')

        # TODO: Extract to config/command line args
        self.playback = False
        self.playback_filename = 'position_speed_test_min.csv'

        if self.args.hardware_present:
            self._logger.info("Running Almost Human with real hardware")
            from app.servo_control.servo_communicator import ServoCommunicator
        else:
            self._logger.info("Running Almost Human with mocked hardware")
            from app.null_objects.null_servo_communicator import NullServoCommunicator as ServoCommunicator

        pygame.init()

        self.loop                = asyncio.get_event_loop()
        self.servo_communicator  = ServoCommunicator()
        self.playback_controller = None
        if self.playback:
            self.playback_controller = ServoController(self.servo_communicator)
            self.playback_controller.prepare_instructions(self.playback_filename)

        self.servo_controller    = JoystickServoController(self.servo_communicator, self.playback_controller)

    def run(self):
        self._logger.info("Almost Human Joystick Control driver starting.")

        self._assign_interrupt_handler()

        tasks = [
            self.servo_controller.run(),
        ]

        try:
            self.loop.run_until_complete(asyncio.wait(tasks))
        finally:
            self._logger.debug("Closing Event Loop")
            self.loop.close()

    def stop(self):
        self.servo_controller.stop()

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

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument("--no-hw", dest='hardware_present', action='store_false', help="Don't attempt to communicate with hardware. Used to test behaviour when no serial device connected")
    parser.set_defaults(hardware_present=True)

    parser.add_argument("-v", dest='verbose_output', action='store_true', help="Output all logged info to the console")
    parser.set_defaults(verbose_output=False)

    JoystickControlDriver(parser.parse_args()).run()
