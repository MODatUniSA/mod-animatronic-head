""" Entry point for playing back a single audio file with servo instructions
"""

import time

from libs.logging.logger_creator import LoggerCreator

class PlaybackController:
    def __init__(self, audio_playback_controller, servo_controller):
        self._logger = LoggerCreator.logger_for('playback_controller')

        self._audio_playback_controller = audio_playback_controller
        self._servo_controller = servo_controller

        self._audio_playback_controller.set_sound_prepared_callback(self._on_sound_prepared)
        self._audio_playback_controller.set_post_playback_callback(self._on_playback_complete)

        self._audio_file = None
        self._instructions_file = None
        self._looping = False

    def play_content(self, audio_file, instructions_file, looping=False):
        """ Plays an audio file in time with the servo instructions
        """

        self._audio_file = audio_file
        self._instructions_file = instructions_file
        self._looping = looping
        self._servo_controller.prepare_instructions(instructions_file)
        self._audio_playback_controller.prepare_sound(audio_file)

    def stop(self):
        """ Stops any playback in preparation for code shutdown
        """

        self._audio_playback_controller.stop_sound()
        self._servo_controller.stop()

    # CALLBACKS
    # =========================================================================

    # REVISE: Do we also need to know here when instructions have been prepared and completed?

    def _on_sound_prepared(self):
        """ Called by the audio_playback_controller when it is ready to play
            the last sound we asked it to load
        """

        self._logger.info("Sound loaded. Playing sound and instructions.")
        self._audio_playback_controller.play_sound()
        self._servo_controller.phonemes_override_expression = False
        self._servo_controller.execute_instructions()

    def _on_playback_complete(self):
        """ Called by the audio_playback_controller when playback has completed
        """

        self._logger.info("Playback complete!")
        self._servo_controller.phonemes_override_expression = False

        if self._looping:
            time.sleep(1)
            self.play_content(self._audio_file, self._instructions_file, self._looping)
