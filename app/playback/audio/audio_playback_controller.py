""" Handles audio playback
    Accepts a file to play, then passes playback onto pygame's mixer.
"""

import os
import asyncio

import pygame.mixer

from libs.config.path_helper import PathHelper
from libs.logging.logger_creator import LoggerCreator
from app.playback.audio.audio_cache import AudioCache
from libs.callback_handling.callback_manager import CallbackManager

class AudioPlaybackController:
    def __init__(self):
        self._logger = LoggerCreator.logger_for('audio_playback_controller')
        self._init_pygame_mixer()
        self._audio_cache                    = AudioCache()
        self._audio_filename                 = None
        self._delayed_post_playback_callback = None
        self._cbm = CallbackManager(['post_playback', 'sound_prepared'], self)
        self._loop                           = asyncio.get_event_loop()

    def prepare_sound(self, audio_file, callback=None):
        """ Prepares a sound for playback
        """

        if not PathHelper.is_valid_audio_file(audio_file):
            self._logger.error("Audio file with name %s not found. Please make sure this exists, and we have read permissions.", audio_file)
            return

        self.stop_sound()

        self._audio_filename = audio_file
        self._logger.info("Loading sound: %s", audio_file)

        # calling _sound() after setting the filename causes us to load it
        if self._sound():
            self._logger.info("Sound prepared. Triggering callback")
            self._cbm.trigger_sound_prepared_callback()
        else:
            self._logger.info("Failed to load sound. Not triggering callback")
            self._audio_filename = None

    def play_sound(self):
        """ Plays the most recent sound we have loaded
        """

        if not self._sound():
            self._logger.error("Attempting to play sound, but no sound loaded.")
            return

        self._sound().play(loops=0)
        self._trigger_callback_on_playback_complete()

    def stop_sound(self):
        if self._sound() is not None:
            self._sound().stop()

        self._cancel_delayed_callbacks()

    # INTERNAL METHODS
    # =========================================================================``

    def _init_pygame_mixer(self):
        # Init just the pygame mixer, as we don't need the entire library
        pygame.mixer.init(frequency=48000, size=-16, channels=2)
        # Only need to play 1 sound at a time
        pygame.mixer.set_num_channels(1)

    def _cancel_delayed_callbacks(self):
        self._logger.debug("Cancelling delayed callbacks")

        if self._delayed_post_playback_callback is not None:
            self._logger.debug("Cancelling scheduled post playback callback")
            self._delayed_post_playback_callback.cancel()
            self._delayed_post_playback_callback = None

            # Still actually trigger the callback from here so listeners know we're no longer playing audio
            self._cbm.trigger_post_playback_callback()


    def _trigger_callback_on_playback_complete(self):
        sound_length = self._sound().get_length()
        self._logger.debug("Waiting %.2f seconds for sound to finish playback", sound_length)
        self._delayed_post_playback_callback = self._loop.call_later(sound_length, self._trigger_post_playback_callback)

    def _trigger_post_playback_callback(self):
        self._cbm.trigger_post_playback_callback()
        self._delayed_post_playback_callback = None

    def _sound(self):
        """ Sound that has most recently been requested for playback. Causes the sound to be loaded into the audio cache if it isn't already cached.
        """

        if self._audio_filename is None:
            return None

        return self._audio_cache.get_sound(self._audio_filename)
