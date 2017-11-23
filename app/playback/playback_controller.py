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

    def play_content(self, audio_file, instructions_file):
        """ Plays an audio file in time with the servo instructions
        """

        self._servo_controller.prepare_instructions(instructions_file)
        self._audio_playback_controller.prepare_sound(audio_file)

    def stop(self):
        """ Stops any playback in preparation for code shutdown
        """

        # TODO: Also stop servo controller instruction execution
        self._audio_playback_controller.stop_sound()

    # CALLBACKS
    # =========================================================================

    # REVISE: Do we also need to know here when instructions have been prepared and completed?

    def _on_sound_prepared(self):
        """ Called by the audio_playback_controller when it is ready to play
            the last sound we asked it to load
        """

        self._logger.info("Sound loaded. Playing sound and instructions.")
        self._audio_playback_controller.play_sound()
        self._servo_controller.execute_instructions()

    def _on_playback_complete(self):
        """ Called by the audio_playback_controller when playback has completed
        """

        self._logger.info("Playback complete!")

        # TEST: Trigger self again after playback complete for testing
        # time.sleep(1)
        # self.play_content('Mod1.ogg', 'Mod1.csv')
