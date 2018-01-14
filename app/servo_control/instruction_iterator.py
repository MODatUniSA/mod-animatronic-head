""" Iterates over an InstructionList, passing each instruction to a callback at the appropriate time
"""

import logging
import asyncio
import time

from libs.callback_handling.callback_manager import CallbackManager

# TODO: Provide a way to put a delay/pre-delay on instructions

class InstructionIterator:
    def __init__(self):
        self._logger = logging.getLogger('instruction_iterator')
        self._iteration_routine = None
        self._iterating = False
        self._instruction_list = None
        self._cbm = CallbackManager(['instruction', 'complete'], self)

    def set_instruction_list(self, instruction_list):
        self._instruction_list = instruction_list

    def iterate_instructions(self, instruction_list=None):
        """ Accepts an instruction list and iterates over all stored instructions
        """

        if instruction_list is not None:
            self._instruction_list = instruction_list

        if self._instruction_list is None:
            # REVISE: Do we call the complete callback here? Maybe need a 3rd error callback?
            self._logger.error("No instruction list to iterate!")
            return

        if len(self._instruction_list.instructions) == 0:
            # REVISE: Do we call the complete callback here? Maybe need a 3rd error callback?
            self._logger.error("No instructions in list to iterate!")
            return

        self._iterating = True
        self._iteration_routine = asyncio.async(self._iterate_instructions())

    def stop(self):
        self._iterating = False
        # TODO: See if we can also stop self._iteration_routine without waiting on sleeps.
        #       Otherwise, could hang code shutdown with long delay between instructions

    # INTERNAL COROUTINES
    # =========================================================================

    @asyncio.coroutine
    def _iterate_instructions(self):
        """ Iterates over the current loaded set of instructions, and triggers a
            callback each time an instruction should be executed
        """

        self._logger.info("Starting iteration of instructions in %s",self._instruction_list._filename)

        start_time  = time.time()
        time_passed = 0

        for instruction in self._instruction_list.instructions:
            if not self._iterating:
                self._logger.info("Stopping instruction iteration")
                self._iteration_routine = None
                return

            self._logger.debug("Reading instruction")
            self._logger.debug("%.2f seconds have passed since start of instruction iteration", time_passed)

            if instruction.time_offset > time_passed:
                # Wait until we should execute the next instruction
                to_wait = instruction.time_offset - time_passed
                self._logger.debug("Next instruction should be executed with an offset of %.2f. Waiting %.2f seconds", instruction.time_offset, to_wait)
                yield from asyncio.sleep(to_wait)

            time_passed = time.time() - start_time

            if self._iterating:
                self._logger.debug("Executing instruction with time offset %.2f at %.2f seconds after iteration start", instruction.time_offset, time_passed)

                self._cbm.trigger_instruction_callback(instruction)

        self._logger.info("Finished iterating instructions")
        self._cbm.trigger_complete_callback(id(self))
        self._iterating = False
        self._iteration_routine = None

    # INTERNAL METHODS
    # =========================================================================

    def _stop_running_routines(self):
        """ Stops the coroutine that executes the instruction iteration
        """

        if self._iteration_routine is not None:
            self._logger.debug("Killing running instruction execution routine")
            self._iterating = False
            # TODO: Test this. May not actually be able to cancel a coroutine except from  another coroutine
            self._iteration_routine.cancel()
            self._iteration_routine = None
