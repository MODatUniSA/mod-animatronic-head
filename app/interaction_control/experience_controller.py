""" ExperienceController maintains Josh's state, and tells interaction executor what to execute
    based on this state
"""

# REVISE: Does this class do anything useful? This functionality could exist on
#         the InteractionLoopExecutor as initially planned. At present, this
#         class will mostly just delegate and handle callbacks from the
#         InteractionLoopExecutor.

# TODO: Figure out when to fetch a new interaction loop and pass it to the executor.
#       After we return to idle? After we're told to activate while idle?
#       May also need to account for activating/deactivating loops that skip idle
#       At this stage, only a single loop will be fetched and executed, regardless of
#       completion or state changes

import logging
import asyncio

from transitions import Machine

from app.interaction_control.interaction_type import InteractionType
from app.interaction_control.interaction_loop import InteractionLoop

class ExperienceController:
    states = ['idle', 'activating', 'active', 'deactivating']

    def __init__(self, interaction_loop_executor, user_detector):
        self._logger = logging.getLogger('experience_controller')
        self._machine = None
        self._executor = interaction_loop_executor
        self._user_detector = user_detector
        self._build_state_machine()
        self._add_executor_callbacks()
        self._add_user_detector_callbacks()

    @asyncio.coroutine
    def run(self):
        """ Starts the experience. Kicks everything off in idle.
        """

        self._executor.set_interaction_loop(self._random_interaction_loop())
        self._execute_idle()

    # INTERACTION EXECUTION
    # =========================================================================

    def _execute_idle(self):
        """ Executes the idle part of the current interaction loop
        """

        self._logger.info("Executing Idle State")
        self._executor.queue_execution(InteractionType.IDLE)

    def _execute_activating(self):
        """ Executes the default activating interaction
        """

        # REVISE: Do we need to tell the loop executor to interrupt its current behvaiour?

        self._logger.info("Executing Activating State")
        self._executor.queue_execution(InteractionType.ACTIVATING)

    def _execute_activating_from_deactivating(self):
        """ Execute the activating interaction from the deactivating state
        """

        #TODO: Handle this differently if needed
        self._execute_activating()

    def _execute_active(self):
        self._logger.info("Executing Active State")
        self._executor.queue_execution(InteractionType.ACTIVE)

    def _execute_deactivating(self):
        self._logger.info("Executing Deactivating State")
        self._executor.queue_execution(InteractionType.DEACTIVATING)

    def _execute_deactivating_from_activating(self):
        #TODO: Handle this differently if needed
        self._execute_deactivating()

    # INTERNAL HELPERS
    # =========================================================================

    def _random_interaction_loop(self):
        # TODO: Return actual random loop. Probably by calling InteractionLoop.random().
        return InteractionLoop('resources/interaction_loops/own_thing_loop.csv')

    def _build_state_machine(self):
        """ Builds the state machine and adds all state transitions
        """
        # REVISE: ignoring invalid triggers. May want to check in caller if transition valid.
        self._machine = Machine(model=self, states=type(self).states, initial='idle', ignore_invalid_triggers=True)
        self._machine.add_transition('complete_idle', 'idle', 'idle', after='_execute_idle')
        self._machine.add_transition('activate', 'idle', 'activating', after='_execute_activating')
        self._machine.add_transition('activate', 'deactivating', 'activating', after='_execute_activating_from_deactivating')
        self._machine.add_transition('complete_activation', 'activating', 'active', after='_execute_active')
        self._machine.add_transition('deactivate', 'active', 'deactivating', after='_execute_deactivating')
        self._machine.add_transition('deactivate', 'activating', 'deactivating', after='_execute_deactivating_from_activating')
        self._machine.add_transition('complete_deactivation', 'deactivating', 'idle', after='_execute_idle')

    def _add_executor_callbacks(self):
        """ Sets callbacks on executor so it can tell us when execution has completed
        """

        self._executor.add_idle_complete_callback(self.complete_idle)
        self._executor.add_activation_complete_callback(self.complete_activation)
        self._executor.add_active_complete_callback(self.deactivate)
        self._executor.add_deactivation_complete_callback(self.complete_deactivation)

    def _add_user_detector_callbacks(self):
        """ Sets callbacks on user detector, so it can tell us when users enter/leave
        """

        self._user_detector.add_first_user_entered_callback(self.activate)
        self._user_detector.add_all_users_left_callback(self.deactivate)
