""" Stores loaded sound objects in a dictionary. Used to allow us to preload/unload sounds from memory around playback. Leads to more predictable playback times as we don't have to account for time taken to load sounds into memory.
"""

import pygame.mixer
import logging
import asyncio
import time

from libs.config.path_helper import PathHelper
from libs.patterns.singleton import Singleton

# IDEA: We currently never unload audio, meaning we could run out of memory if we have enough audio.
#       Should either automatically uncache audio that hasn't been referenced in a period of time,
#       or have all audio for an interaction loop uncached on its completion.

@Singleton
class AudioCache:
    LOADING_STRING = 'loading'

    def __init__(self):
        self._cache = {}
        self._logger = logging.getLogger('audio_cache')
        self._loop = asyncio.get_event_loop()

    def load_sound(self, filename):
        """ Loads a sound object into memory
        """

        if self.is_sound_cached(filename):
            self._logger.info("Ignoring attempt to preload sound that is already cached: %s", filename)
            return

        if not PathHelper.is_valid_audio_file(filename):
            self._logger.error("Cannot find or open file we are attempting to preload: %s", filename)
            return

        try:
            self._set_as_loading(filename)
            # Perform the acutal loading of the audio file in a background thread
            self._loop.run_in_executor(None, self._perform_load_sound, filename)
            return True
        except pygame.error as err:
            self._logger.error("Error loading sound!", exc_info=True)
            return False

    def unload_sound(self, filename):
        if not self.is_sound_cached(filename):
            self._logger.warning("Attempting to unload sound that has not been cached: %s", filename)
            return

        self._logger.info("Audio Cache unloading sound: %s", filename)
        del self._cache[filename]

    def get_sound(self, filename):
        if not self.is_sound_cached(filename):
            self._logger.info("Attempting to fetch uncached sound. Loading into cache.")
            self.load_sound(filename)

        # Block if we're trying to fetch a sound that is currently being loaded in the background
        while self.is_sound_loading(filename):
            self._logger.debug("Waiting for sound to load")
            time.sleep(0.1)

        return self._cache.get(filename)

    def is_sound_cached(self, filename):
        return filename in self._cache.keys()

    def is_sound_loading(self, filename):
        return self.is_sound_cached(filename) and self._cache[filename] == type(self).LOADING_STRING

    def _set_as_loading(self, filename):
        self._cache[filename] = type(self).LOADING_STRING

    def _perform_load_sound(self, filename):
        """ Performs the actual loading of the argument sound into memory
        """

        self._logger.info("Audio Cache preloading sound: %s", filename)
        sound = pygame.mixer.Sound(PathHelper.audio_path(filename))
        self._cache[filename] = sound
