""" Interaction Class. Holds info required for single interaction in loop
"""

# REVISE: Should this class validate/load the referenced files?

from app.interaction_control.interaction_type import InteractionType
from app.interaction_control.eye_control_type import EyeControlType

class Interaction:
    def __init__(self, name, voice_file=None, phoneme_file=None, animation_file=None, interaction_type=InteractionType.NONE, eye_control_type=EyeControlType.NONE):
        self.name = name
        self.voice_file = voice_file
        self.phoneme_file = phoneme_file
        self.animation_file = animation_file
        self.interaction_type = InteractionType.NONE
        self.eye_control = EyeControlType.NONE

    @classmethod
    def from_dict(cls, attrs):
        return cls(
            attrs['name'],
            attrs.get('voice_file'),
            attrs.get('phoneme_file'),
            attrs.get('animation_file'),
            InteractionType[str(attrs.get('interaction_type')).upper()],
            EyeControlType[str(attrs.get('eye_control_type')).upper()]
        )
