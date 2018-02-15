""" InteractionLoop contains an entire interaction loop, as defined by a CSV file
    CSV - state,interaction_name
        idle, breathing_1
        activating, hello_1
        activating, transition_1
        active, own_thing_1
        active, transition_2
        ...
    IDLE state defines the idle to be used AFTER the rest of the loop is executed
"""

import csv

from app.interaction_control.interaction_type import InteractionType
from app.interaction_control.interaction_map import InteractionMap
from app.playback.audio.audio_cache import AudioCache

# REVISE: Either need a .random() factory method in here to fetch and load a random loop file,
#         or need to create an InteractionLoopList class with a random() method
class InteractionLoop:
    def __init__(self, loop_file):
        self.audio_files = []
        self._current_interaction_type = None
        self._iterator = None
        self._interactions = {
            InteractionType.IDLE : [],
            InteractionType.ACTIVATING : [],
            InteractionType.ACTIVE : [],
            InteractionType.DEACTIVATING : [],
        }
        self._interaction_map = InteractionMap.Instance()
        self._build_interactions(loop_file)

    def reset(self):
        """ Resets the state of this loop. Allows us to iterate over a single interaction type multiple times
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
