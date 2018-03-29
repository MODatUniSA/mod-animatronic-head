""" Iterates over an InstructionList, passing each instruction to a callback at the appropriate time
"""

import logging
import asyncio
import time

from libs.callback_handling.callback_manager import CallbackManager

class InstructionIterator:
    def __init__(self):
        self._logger = logging.getLogger('instruction_iterator_{}'.format(id(self)))
        self._iteration_routine = None
        self._iterating = False
        self._instruction_list = None
        self._cbm = CallbackManager(['instruction', 'complete'], self)

    def set_instruction_list(self, instruction_list):
        """ Sets the list of instructions this iterator should iterate
        """

        self._instruction_list = instruction_list

    def iterate_instructions(self, instruction_list=None):
        """ Accepts an instruction list and iterates over all stored instructions
            Instruction list is optional, as we can set one with set_instruction_list
            to set it up without immediately starting iteration
        """

        if instruction_list is not None:
            self._instruction_list = instruction_list

        if self._instruction_list is None:
            self._logger.error("No instruction list to iterate!")
            self._cbm.trigger_complete_callback(id(self))
            return

        if not self._instruction_list.instructions:
            self._logger.error("No instructions in list to iterate!")
            self._cbm.trigger_complete_callback(id(self))
            return

        self._iterating = True
        self._iteration_routine = asyncio.ensure_future(self._iterate_instructions())

    def stop(self):
        """ Stop instruction iteration
        """

        self._stop_running_routines()

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
                self._logger.info("Interrupting instruction iteration")
                break

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
                self._cbm.trigger_instruction_callback(instruction, id(self))

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
            self._iteration_routine.cancel()
            self._iterating = False
            self._iteration_routine = None
            self._cbm.trigger_complete_callback(id(self))
