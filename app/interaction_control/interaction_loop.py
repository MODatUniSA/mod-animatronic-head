import csv
import os
import random
import logging

from app.interaction_control.interaction_type import InteractionType
from app.interaction_control.interaction_map import InteractionMap
from app.playback.audio.audio_cache import AudioCache

from libs.config.device_config import DeviceConfig
from libs.config.path_helper import PathHelper
from libs.patterns.singleton import Singleton

class InteractionLoop:
    """ Contains an entire interaction loop, as defined by a CSV file
        CSV -
            state,interaction_name
            IDLE, breathing_1
            ACTIVATING, hello_1
            ACTIVATING, transition_1
            ACTIVE, own_thing_1
            ACTIVE, transition_2
            ...
        IDLE state defines the idle to be used AFTER the rest of the loop is executed
    """

    def __init__(self, loop_file):
        self.audio_files = []
        self._current_interaction_type = None
        self._iterator = None
        self._interactions = {
            InteractionType.IDLE : [],
            InteractionType.ACTIVATING : [],
            InteractionType.INTERRUPTED_ACTIVATING : [],
            InteractionType.ACTIVE : [],
            InteractionType.DEACTIVATING : [],
            InteractionType.INTERRUPTED_DEACTIVATING : [],
        }
        self._interaction_map = InteractionMap.Instance()
        self._build_interactions(loop_file)

    @classmethod
    def next_loop(cls):
        """ Returns a random interaction loop
        """
        return cls(InteractionLoopList.Instance().next())

    def reset(self):
        """ Resets the state of this loop. Allows us to iterate over a single interaction type
            multiple times without reloading
        """

        self._current_interaction_type = None
        self._iterator = None

    def next(self, interaction_type):
        """ Returns the next interaction of the argument interaction type, or
            None if no next element present
        """

        self._ensure_iterator_current(interaction_type)
        return next(self._iterator, None)

    def cache_all_audio(self):
        """ Caches all audio files referenced by interactions in this loop
        """

        audio_cache = AudioCache.Instance()
        for audio_file in self.audio_files:
            audio_cache.load_sound(audio_file)

    # INTERAL HELPERS
    # =========================================================================

    def _build_interactions(self, loop_file):
        with open(loop_file, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                self._build_interaction(row)

    def _build_interaction(self, interaction_info):
        # TODO: Handle unknown interaction type
        interaction_type = InteractionType[interaction_info['state'].upper()]

        # TODO: Notify if we are skipping an interaction because we can't find it in the map
        interaction = self._interaction_map.get(interaction_info['interaction_name'])
        if interaction is not None:
            self._interactions[interaction_type].append(interaction)
            if interaction.voice_file not in ['', None]:
                self.audio_files.append(interaction.voice_file)

    def _ensure_iterator_current(self, interaction_type):
        if self._current_interaction_type != interaction_type:
            self._current_interaction_type = interaction_type
            self._iterator = iter(self._interactions[interaction_type])

@Singleton
class InteractionLoopList:
    """ List of all defined interaction loops in directory defined in config
    """

    def __init__(self):
        self._logger = logging.getLogger('interaction_loop_list')
        config = DeviceConfig.Instance()
        self._random_order = config.options['INTERACTION_LOOPS'].getboolean('RANDOM_ORDER')
        self.loops = []
        self._base_path = PathHelper.base_interaction_loop_path
        self._valid_extension = '.csv'
        self._last_selected = None
        self._last_selected_index = -1
        self._build_list()

    def next(self):
        """ Fetch the next interaction loop to execute.
        """

        return self.random() if self._random_order else self.next_sequential()

    def next_sequential(self):
        """ Fetch the next interaction loop in the order they were loaded
        """

        if not self._check_loops_loaded():
            return None

        self._last_selected_index = (self._last_selected_index + 1) % len(self.loops)
        self._last_selected = self.loops[self._last_selected_index]
        return self._last_selected

    def random(self):
        """ Fetch a random loop from all loaded loops. If more than one loop defined, does not
            return the same loop twice in a row
        """
        if not self._check_loops_loaded():
            return None


        if len(self.loops) == 1:
            return self.loops[0]

        except_last = [loop for loop in self.loops if loop != self._last_selected]
        self._last_selected = random.choice(except_last)
        self._last_selected_index = self.loops.index(self._last_selected)
        return self._last_selected

    def _check_loops_loaded(self):
        if not self.loops:
            self._logger.error("No Loops Loaded. Make sure interaction loop csvs are present in %s", self._base_path)
            return False
        return True

    def _build_list(self):
        """ Builds a list of interaction loops based on files in the specified interaction
            loop directory
        """

        self.loops = [
            os.path.join(self._base_path, filename) for filename
            in os.listdir(self._base_path)
            if os.path.isfile(os.path.join(self._base_path, filename)) and
            os.path.splitext(filename)[1] == self._valid_extension
        ]
        self.loops.sort()
