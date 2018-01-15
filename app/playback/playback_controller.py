""" Entry point for playing back a single audio file with servo instructions
"""

import asyncio
import time

from libs.logging.logger_creator import LoggerCreator
from libs.callback_handling.callback_manager import CallbackManager
from app.servo_control.servo_map import MOUTH_SERVO_PINS

# TODO: Need to be able to interrupt interactions

class PlaybackController:
    def __init__(self, audio_playback_controller, servo_controller):
        self._logger = LoggerCreator.logger_for('playback_controller')
        self._cbm = CallbackManager(['interaction_complete'], self)

        self._audio_playback_controller = audio_playback_controller
        self._servo_controller = servo_controller

        self._audio_playback_controller.add_sound_prepared_callback(self._on_sound_prepared)
        self._audio_playback_controller.add_post_playback_callback(self._on_playback_complete)
        self._servo_controller.add_instructions_complete_callback(self._on_servo_instructions_complete)

        self._audio_playback_running = False
        self._servo_instructions_running = False

    def play_interaction(self, interaction):
        """ Plays content for a single interaction and notifies when complete
        """

        self._logger.info("Playing Interaction: {}".format(interaction.name))

        if interaction.phoneme_file is not None:
            self._servo_controller.prepare_instructions(interaction.phoneme_file)
            if interaction.animation_file is not None:
                self._servo_controller.prepare_instructions(interaction.animation_file, without=MOUTH_SERVO_PINS)

        # TODO: Handle Eye Control Type
        if interaction.animation_file is not None:
            self._servo_controller.prepare_instructions(interaction.animation_file)

        if interaction.voice_file is not None:
            # Instructions will be executed once the audio file has been loaded
            self._audio_playback_controller.prepare_sound(interaction.voice_file)
        else:
            self._servo_controller.execute_instructions()
            self._servo_instructions_running = True

    def play_content(self, audio_file, instructions_file):
        """ Plays an audio file in time with the servo instructions
        """

        self._servo_controller.prepare_instructions(instructions_file)
        self._audio_playback_controller.prepare_sound(audio_file)

    def stop(self):
        """ Stops any playback in preparation for code shutdown
        """

        self._audio_playback_controller.stop_sound()
        self._servo_controller.stop()

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
        self._servo_controller.execute_instructions()

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
