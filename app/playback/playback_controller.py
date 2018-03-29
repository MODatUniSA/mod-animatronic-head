""" Entry point for playing back a single audio file with servo instructions
"""

import asyncio
import time
import logging

from libs.callback_handling.callback_manager import CallbackManager

from app.interaction_control.eye_control_type import EyeControlType
from app.servo_control.servo_map import MOUTH_SERVO_PINS, EYE_SERVO_PINS

class PlaybackController:
    def __init__(self, audio_playback_controller, servo_controller, eye_controller):
        self._logger = logging.getLogger('playback_controller')
        self._cbm = CallbackManager(['interaction_complete', 'interaction_started'], self)

        self._audio_playback_controller = audio_playback_controller
        self.servo_controller = servo_controller
        self._eye_controller = eye_controller

        self._audio_playback_controller.add_sound_prepared_callback(self._on_sound_prepared)
        self._audio_playback_controller.add_post_playback_callback(self._on_playback_complete)
        self.servo_controller.add_instructions_complete_callback(self._on_servo_instructions_complete)

        self._audio_playback_running = False
        self._servo_instructions_running = False

    def play_interaction(self, interaction):
        """ Plays content for a single interaction and notifies when complete
        """

        self._logger.info("Playing Interaction: {}".format(interaction.name))
        empty = [None, '']

        # Used to stop the animation file driving certain servo pins if they're
        # to be driven by another source (e.g. procedural face tracking)
        animation_excluded_servo_pins = []
        if interaction.eye_control == EyeControlType.TRACK:
            animation_excluded_servo_pins = EYE_SERVO_PINS
            self._eye_controller.start_tracking()
        else:
            self._eye_controller.stop_tracking()

        # Prepare phoneme file instructions if present
        if interaction.phoneme_file not in empty:
            self.servo_controller.prepare_instructions(interaction.phoneme_file)
            self._logger.debug("Preparing phoneme instructions from %s.", interaction.phoneme_file)
            animation_excluded_servo_pins += MOUTH_SERVO_PINS

        # prepare animation file instructions if present
        if interaction.animation_file not in empty:
            self.servo_controller.prepare_instructions(interaction.animation_file, without_servos=animation_excluded_servo_pins)
            self._logger.debug("Preparing animation instructions from %s", interaction.animation_file)

        # prepare voice file if present (kick off instruction execution otherwise)
        if interaction.voice_file not in empty:
            self._logger.debug("Preparing audio file: %s", interaction.voice_file)
            # Instructions will be executed once the audio file has been loaded
            self._audio_playback_controller.prepare_sound(interaction.voice_file)
        else:
            self._cbm.trigger_interaction_started_callback()
            self.servo_controller.execute_instructions()
            self._servo_instructions_running = True

    def stop_interaction(self):
        """ Stop any audio and instructions of the currently playing interaction
        """

        self._logger.info("Stopping currently executing interaction")
        self.servo_controller.stop_execution()
        self._audio_playback_controller.stop_sound()

    def play_content(self, audio_file, instructions_file):
        """ Plays an audio file in time with the servo instructions
        """

        self.servo_controller.prepare_instructions(instructions_file)
        self._audio_playback_controller.prepare_sound(audio_file)

    def stop(self):
        """ Stops any playback in preparation for code shutdown
        """

        self.stop_interaction()
        self.servo_controller.stop()

    # CALLBACKS
    # =========================================================================

    def _on_sound_prepared(self):
        """ Called by the audio_playback_controller when it is ready to play
            the last sound we asked it to load.
        """

        self._logger.info("Sound loaded. Playing sound and instructions.")
        self._audio_playback_running = True
        self._servo_instructions_running = True
        self._audio_playback_controller.play_sound()
        self._cbm.trigger_interaction_started_callback()
        self.servo_controller.execute_instructions()

    def _on_playback_complete(self):
        """ Called by the audio_playback_controller when playback has completed
        """

        self._logger.info("Audio playback complete!")
        self._audio_playback_running = False
        self._check_trigger_interaction_complete()

    def _on_servo_instructions_complete(self):
        """ Called when the servo controller has finished executing all instructions
        """

        self._logger.info("Instruction execution complete!")
        self._servo_instructions_running = False
        self._check_trigger_interaction_complete()

    def _check_trigger_interaction_complete(self):
        if self._audio_playback_running is False and self._servo_instructions_running is False:
            self._cbm.trigger_interaction_complete_callback()
