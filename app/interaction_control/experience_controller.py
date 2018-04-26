""" ExperienceController maintains Josh's state, and tells interaction executor what to execute
    based on this state
"""

import logging

from transitions import Machine

from app.interaction_control.interaction_type import InteractionType
from app.interaction_control.interaction_loop import InteractionLoop

class ExperienceController:
    states = [
        'idle',
        'activating',
        'interrupted_activating',
        'active',
        'deactivating',
        'interrupted_deactivating',
    ]

    def __init__(self, interaction_loop_executor, user_detector, autorun=False):
        self._logger = logging.getLogger('experience_controller')
        self._machine = None
        self._executor = interaction_loop_executor
        self._user_detector = user_detector
        self._autorun = autorun
        self._build_state_machine()
        self._add_executor_callbacks()
        self._add_user_detector_callbacks()
        self._should_quit = False

        self._logger.info("Experience Autorun enabled: {}".format(autorun))

    def run(self):
        """ Starts the experience. Kicks everything off in idle.
        """

        self._execute_idle()

    def stop(self):
        self._should_quit = True
        self._executor.stop()

    # INTERACTION EXECUTION
    # =========================================================================

    # REVISE: Intearaction execution methods all almost identical. Could probably have a single
    #           method and a map to determine which interactions to execute

    def _execute_idle(self):
        """ Executes the idle part of the current interaction loop. Selects a new random interaction
            loop each time we go into idle
        """

        if self._should_quit:
            return

        self._executor.set_interaction_loop(InteractionLoop.random())
        self._logger.info("Executing Idle State")
        self._executor.queue_execution(InteractionType.IDLE)

    def _execute_activating(self,interrupt=True):
        """ Executes the default activating interaction
        """

        if self._should_quit:
            return

        self._logger.info("Executing Activating State")
        self._executor.queue_execution(InteractionType.ACTIVATING, interrupt)

    def _execute_interrupted_activating(self):
        """ Execute the activating interaction from the deactivating state
        """

        if self._should_quit:
            return

        self._logger.info("Executing Interrupted Activating State")
        self._executor.queue_execution(InteractionType.INTERRUPTED_ACTIVATING, True)

    def _execute_active(self):
        if self._should_quit:
            return

        self._logger.info("Executing Active State")
        self._executor.queue_execution(InteractionType.ACTIVE)

    def _execute_deactivating(self):
        if self._should_quit:
            return

        self._logger.info("Executing Deactivating State")
        self._executor.queue_execution(InteractionType.DEACTIVATING)

    def _execute_interrupted_deactivating(self):
        if self._should_quit:
            return

        self._logger.info("Executing Interrupted Deactivating State")
        self._executor.queue_execution(InteractionType.INTERRUPTED_DEACTIVATING, True)

    # INTERNAL HELPERS
    # =========================================================================

    def _build_state_machine(self):
        """ Builds the state machine and adds all state transitions
        """

        # REVISE: Each state now has its own handling, could probably just call builtin machine
        #           callbacks (on_enter_idle, etc.) to handle transitions, rather than using after
        #           transition callbacks

        self._machine = Machine(model=self, states=type(self).states, initial='idle', ignore_invalid_triggers=True)
        self._machine.add_transition(
            trigger ='complete_idle',
            source  ='idle',
            dest    ='idle',
            after   ='_execute_idle'
        )
        self._machine.add_transition(
            trigger ='activate',
            source  ='idle',
            dest    ='activating',
            after   ='_execute_activating'
        )
        self._machine.add_transition(
            trigger ='activate',
            source  =['deactivating', 'interrupted_deactivating'],
            dest    ='interrupted_activating',
            after   ='_execute_interrupted_activating'
        )
        self._machine.add_transition(
            trigger ='complete_activation',
            source  =['activating', 'interrupted_activating'],
            dest    ='active',
            after   ='_execute_active'
        )
        self._machine.add_transition(
            trigger ='deactivate',
            source  ='active',
            dest    ='deactivating',
            after   ='_execute_deactivating'
        )
        self._machine.add_transition(
            trigger ='deactivate_interrupt',
            source  =['activating', 'active'],
            dest    ='interrupted_deactivating',
            after   ='_execute_interrupted_deactivating'
        )
        self._machine.add_transition(
            trigger ='complete_deactivation',
            source  =['deactivating', 'interrupted_deactivating'],
            dest    ='idle',
            after   ='_execute_idle'
        )

    # CALLBACKS
    # =========================================================================

    def _add_executor_callbacks(self):
        """ Sets callbacks on executor so it can tell us when execution has completed
        """

        if self._autorun:
            self._executor.add_idle_complete_callback(self.activate)
        else:
            self._executor.add_idle_complete_callback(self.complete_idle)

        self._executor.add_activation_complete_callback(self.complete_activation)
        self._executor.add_active_complete_callback(self.deactivate)
        self._executor.add_deactivation_complete_callback(self.complete_deactivation)

    def _add_user_detector_callbacks(self):
        """ Sets callbacks on user detector, so it can tell us when users enter/leave
        """

        self._user_detector.add_first_user_entered_callback(self.activate)
        self._user_detector.add_all_users_left_callback(self.deactivate_interrupt)
