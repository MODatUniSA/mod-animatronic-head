""" Interaction loop executor executes interaction loops
"""
import logging

from libs.callback_handling.callback_manager import CallbackManager
from app.interaction_control.interaction_type import InteractionType

# TODO: Need a way to interrupt this execution, so we can transition between states early based on user behaviour

class InteractionLoopExecutor:
    callbacks = ['idle_complete', 'activation_complete', 'active_complete', 'deactivation_complete']

    def __init__(self, playback_controller):
        self._logger = logging.getLogger('interaction_loop_executor')
        self._playback_controller = playback_controller
        # Execute the next step each time an interaction is completed
        self._playback_controller.add_interaction_complete_callback(self.continue_execution)

        self._interaction_loop = None
        self._current_interaction_type = None
        self._cbm = CallbackManager(type(self).callbacks, self)
        # What to call on completion of any interaction type
        self._completion_triggers = {
            InteractionType.IDLE : self._cbm.trigger_idle_complete_callback,
            InteractionType.ACTIVATING : self._cbm.trigger_activation_complete_callback,
            InteractionType.ACTIVE : self._cbm.trigger_active_complete_callback,
            InteractionType.DEACTIVATING : self._cbm.trigger_deactivation_complete_callback
        }

    def set_interaction_loop(self, interaction_loop):
        self._interaction_loop = interaction_loop

    def start_execution(self, interaction_type):
        """ Starts execution of all interactions of the argument type, triggering a callback when all are complete
        """

        self._logger.info("Starting Execution of {} interactions".format(interaction_type.name))
        self._interaction_loop.reset()
        self._current_interaction_type = interaction_type
        self._execute_step_or_finish()

    def continue_execution(self):
        """ Executes the next step in the current interaction
        """

        self._execute_step_or_finish()

    def _execute_step_or_finish(self):
        """ Executes the next step in the current interaction type if present, or flags it as complete otherwise
        """

        interaction = self._interaction_loop.next(self._current_interaction_type)
        if interaction is not None:
            self._playback_controller.play_interaction(interaction)
        else:
            # Notify of completion of current interaction type
            self._completion_triggers[self._current_interaction_type]()
