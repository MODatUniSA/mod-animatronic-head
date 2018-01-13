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

# REVISE: Either need a .random() factory method in here to fetch and load a random loop file,
#         or need to create an InteractionLoopList class with a random() method
class InteractionLoop:
    def __init__(self, loop_file):
        self._interactions = {
            InteractionType.IDLE : [],
            InteractionType.ACTIVATING : [],
            InteractionType.ACTIVE : [],
            InteractionType.DEACTIVATING : [],
        }
        self._interaction_map = InteractionMap.Instance()
        self._build_interactions(loop_file)

    # REVISE: Do we need to define this for every interaction type?
    #         Can we just define them in a dict, then define these methods with metaprogramming?
    # OR can we just use next(InteractionType.IDLE)
    def next_idle(self):
        """ Returns the next idle interaction
        """
        pass

    def next_idle_available(self):
        """ Returns whether there is another idle interaction available
        """
        pass

    def _build_interactions(self, loop_file):
        with open(loop_file, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                print("Interaction: {}".format(row))
                self._build_interaction(row)

    def _build_interaction(self, interaction_info):
        # TODO: Handle unknown interaction type
        interaction_type = InteractionType[interaction_info['state'].upper()]

        # TODO: Notify if we are skipping an interaction because we can't find it in the map
        interaction = self._interaction_map.get(interaction_info['interaction_name'])
        if interaction is not None:
            self._interactions[interaction_type].append(interaction)
