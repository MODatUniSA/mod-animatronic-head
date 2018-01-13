""" Interaction loop executor executes interaction loops
"""

from libs.callback_handling.callback_manager import CallbackManager
from app.interaction_control.interaction_type import InteractionType

class InteractionLoopExecutor:
    callbacks = ['idle_complete', 'activation_complete', 'active_complete', 'deactivation_complete']

    def __init__(self, playback_controller):
        self._playback_controller = playback_controller
        self._interaction_loop = None
        self._current_interaction_type = None
        self._cbm = CallbackManager(type(self).callbacks, self)
        # Defines what to call on completion of any interaction type
        self._trigger_map = {
            InteractionType.IDLE : self._cbm.trigger_idle_complete_callback,
            InteractionType.ACTIVATING : self._cbm.trigger_activation_complete_callback,
            InteractionType.ACTIVE : self._cbm.trigger_active_complete_callback,
            InteractionType.DEACTIVATING : self._cbm.trigger_deactivation_complete_callback
        }

    def set_interaction_loop(self, interaction_loop):
        self._interaction_loop = interaction_loop

    def execute(self, interaction_type):
        """ Executes all interactions of the argument type, triggering a callback when all are complete
        """

        self._current_interaction_type = interaction_type
        if self._interaction_loop.next_available(interaction_type):
            interaction = self._interaction_loop.next(interaction_type)
            self._playback_controller.play_interaction(interaction)
        else:
            self._trigger_map[self._current_interaction_type]()
