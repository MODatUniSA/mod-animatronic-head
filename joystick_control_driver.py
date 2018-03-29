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
from app.playback.audio.audio_playback_controller import AudioPlaybackController
from app.playback.playback_controller import PlaybackController
from app.interaction_control.interaction import Interaction
from app.null_objects.null_eye_controller import NullEyeController

class JoystickControlDriver:
    def __init__(self, args):
        self.args                      = args
        LoggerCreator().create_logger()
        self._logger                   = LoggerCreator.logger_for('driver')

        if self.args.hardware_present:
            self._logger.info("Running Almost Human with real hardware")
            from app.servo_control.servo_communicator import ServoCommunicator
        else:
            self._logger.info("Running Almost Human with mocked hardware")
            from app.null_objects.null_servo_communicator import NullServoCommunicator as ServoCommunicator

        # TODO: Set in config
        pygame.mixer.pre_init(frequency=48000, size=-16, channels=2)
        pygame.init()

        self.loop                   = asyncio.get_event_loop()
        servo_communicator          = ServoCommunicator()
        audio_playback_controller   = AudioPlaybackController()
        servo_controller            = ServoController(servo_communicator)
        playback_controller         = PlaybackController(audio_playback_controller, servo_controller, NullEyeController())

        self.joystick_controller = JoystickServoController(
            playback_controller,
            self._build_input_interaction(),
            args.autostop_recording,
            args.overdub,
            args.looping
        )

        if args.output_file is not None:
            self.joystick_controller.record_to_file(args.output_file)

    def run(self):
        self._logger.info("Almost Human Joystick Control driver starting.")

        self._assign_interrupt_handler()

        tasks = [
            self.joystick_controller.run(),
        ]

        try:
            self.loop.run_until_complete(asyncio.wait(tasks))
        finally:
            self._logger.debug("Closing Event Loop")
            self.loop.close()

    def stop(self):
        self.joystick_controller.stop()

    def _build_input_interaction(self):
        if self.args.input_file is None and self.args.playback_audio_file is None:
            return None

        return Interaction(
            name='joystick_input_interaction',
            voice_file=self.args.playback_audio_file,
            animation_file=self.args.input_file
        )

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

    parser.add_argument("-no-hw", dest='hardware_present', action='store_false', help="Don't attempt to communicate with hardware. Used to test behaviour when no serial device connected")
    parser.set_defaults(hardware_present=True)

    parser.add_argument("-v", dest='verbose_output', action='store_true', help="Output errors, warnings, and info to the console")
    parser.add_argument("-vv", dest='very_verbose_output', action='store_true', help="Output all logged output to the console")
    parser.set_defaults(verbose_output=False)

    parser.add_argument("-autostop", dest='autostop_recording', action='store_true', help="Autostop the overdub recording once the input file completes playback. Has no effect if looping.")
    parser.set_defaults(autostop_recording=False)

    parser.add_argument("-overdub", dest='overdub', action='store_true', help="Record both the playback and joystick control into the new file")
    parser.set_defaults(overdub=False)

    parser.add_argument("-loop", dest='looping', action='store_true', help="Loop playback/recording")
    parser.set_defaults(looping=False)

    parser.add_argument("--playback", dest='input_file', help="Instruction file to execute")
    parser.set_defaults(input_file=None)

    parser.add_argument("--playback-audio", dest='playback_audio_file', help="Audio file to play")
    parser.set_defaults(playback_audio_file=None)

    # IDEA: Consider adding arg to record to default file
    parser.add_argument("--record", dest='output_file', help="File to write joystick control + playback instructions to.")
    parser.set_defaults(output_file=None)


    JoystickControlDriver(parser.parse_args()).run()
