""" Entry point for playing back a single audio file with servo instructions
"""

from libs.logging.logger_creator import LoggerCreator

class PlaybackController:
    def __init__(self, audio_playback_controller, servo_controller):
        self._logger = LoggerCreator.logger_for('playback_controller')

        self._audio_playback_controller = audio_playback_controller
        self._servo_controller = servo_controller

        self._audio_playback_controller.set_sound_prepared_callback(self._on_sound_prepared)
        self._audio_playback_controller.set_post_playback_callback(self._on_playback_complete)
        # self._sound_prea

    def play_content(self, audio_file, instructions_file):
        """ Plays an audio file in time with the servo instructions
        """

        self._audio_playback_controller.prepare_sound(audio_file)
        # TODO: Pass instructions to the servo controller to load/execute


    def stop(self):
        """ Stops any playback in preparation for code shutdown
        """

        self._audio_playback_controller.stop_sound()

    # CALLBACKS
    # =========================================================================

    def _on_sound_prepared(self):
        """ Called by the audio_playback_controller when it is ready to play
            the last sound we asked it to load
        """

        self._logger.info("Sound prepared. Playing.")
        self._audio_playback_controller.play_sound()

    def _on_playback_complete(self):
        """ Called by the audio_playback_controller when playback has completed
        """

        self._logger.info("Playback complete!")
