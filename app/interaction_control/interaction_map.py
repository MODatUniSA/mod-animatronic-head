""" Holds collections of interactions so they can be referenced by name
"""

import csv

from libs.patterns.singleton import Singleton

from app.interaction_control.interaction import Interaction

@Singleton
class InteractionMap(dict):
    def __init__(self):
        self._build_map()
        super().__init__()

    def _build_map(self):
        # TODO: Define this file in config
        with open('resources/interactions/interactions.csv', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                self[row['name']] = Interaction.from_dict(row)
