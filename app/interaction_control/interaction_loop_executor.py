""" Interaction loop executor executes interaction loops
"""
import logging

from libs.callback_handling.callback_manager import CallbackManager
from app.interaction_control.interaction_type import InteractionType

class InteractionLoopExecutor:
    callbacks = ['idle_complete', 'activation_complete', 'active_complete', 'deactivation_complete']

    def __init__(self, playback_controller):
        self._logger = logging.getLogger('interaction_loop_executor')
        self._playback_controller = playback_controller
        # Execute the next step each time an interaction is completed
        self._playback_controller.add_interaction_complete_callback(self.handle_execution_complete)

        self._should_quit = False
        self._executing = False
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

    def stop(self):
        self._should_quit = True
        self._playback_controller.stop()

    def set_interaction_loop(self, interaction_loop):
        self._interaction_loop = interaction_loop
        # REVISE: This will cache all audio as soon as we're passed an interaction loop,
        # and will only hold up running the loop until the first audio file is loaded.
        # This might not be the best place to cache the audio, but I'm not sure where would be better at present.
        self._interaction_loop.cache_all_audio()

    def queue_execution(self, interaction_type, interrupt=False):
        """ Queues execution of all interactions of the argument type, triggering a callback when all are complete
            If nothing is currently executing, execution is started immediately, otherwise we wait for the
            completion of the current interaction
            If interrupt is True, we stop the currently executing interaction executing immediately
        """

        self._logger.info("Queuing Execution of %s interactions", interaction_type.name)
        self._interaction_loop.reset()
        self._current_interaction_type = interaction_type

        if interrupt:
            self._playback_controller.stop_interaction()

        # Start executing first step of interaction if we're not already running
        if not self._executing:
            self._execute_step_or_finish()
            self._executing = True

    def handle_execution_complete(self):
        """ Called when execution of an interaction is complete
        """

        if self._should_quit:
            return

        self._execute_step_or_finish()

    def _execute_step_or_finish(self):
        """ Executes the next step in the current interaction type if present, or flags it as complete otherwise
        """

        self._logger.debug("Executing {} Step".format(self._current_interaction_type.name))

        interaction = self._interaction_loop.next(self._current_interaction_type)
        if interaction is not None:
            self._playback_controller.play_interaction(interaction)
        else:
            # Notify of completion of current interaction type
            self._executing = False
            self._completion_triggers[self._current_interaction_type]()
