""" Stores loaded sound objects in a dictionary. Used to allow us to preload/unload sounds from memory around playback. Leads to more predictable playback times as we don't have to account for time taken to load sounds into memory.
"""

import pygame.mixer

from libs.config.path_helper import PathHelper
from libs.logging.logger_creator import LoggerCreator

class AudioCache:
    def __init__(self):
        self._cache = {}
        self._logger = LoggerCreator.logger_for('audio_cache')

    def load_sound(self, filename):
        """ Loads a sound object into memory
        """

        if self.is_sound_cached(filename):
            self._logger.warning("Attempting to preload sound that is already cached: %s", filename)
            return

        if not PathHelper.is_valid_audio_file(filename):
            self._logger.error("Cannot find or open file we are attempting to preload: %s", filename)
            return


        self._logger.info("Audio Cache preloading sound: %s", filename)

        try:
            self._cache[filename] = pygame.mixer.Sound(PathHelper.audio_path(filename))
            return True
        except pygame.error as err:
            self._logger.exception(err)
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

        return self._cache.get(filename)

    def is_sound_cached(self, filename):
        return filename in self._cache.keys()
