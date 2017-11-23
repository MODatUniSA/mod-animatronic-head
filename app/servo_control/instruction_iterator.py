""" Iterates over an InstructionList, passing each instruction to a callback at the appropriate time
"""

import logging
import asyncio
import time

# TODO: Provide a way to put a delay/pre-delay on instructions

class InstructionIterator:
    def __init__(self):
        self._logger = logging.getLogger('instruction_iterator')
        self._iteration_routine = None
        self._iterating = False
        self._instruction_list = None
        self._instruction_callback = None
        self._complete_callback = None

    # TODO: Generalise callback setting/triggering/handling
    def set_intruction_callback(self, to_call):
        """ Accepts a callable, which will be passed each instruction when it is time to be executed.
            Should be called before iterate_instructions.
        """

        if not self._check_callable(to_call):
            return

        self._instruction_callback = to_call

    def set_complete_callback(self, to_call):
        """ Accepts a callable, which will be passed each instruction when it is time to be executed.
            Should be called before iterate_instructions.
        """

        if not self._check_callable(to_call):
            return

        self._complete_callback = to_call

    def iterate_instructions(self, instruction_list):
        """ Accepts an instruction list and iterates over all stored instructions
        """

        self._instruction_list = instruction_list

        if len(instruction_list.instructions) == 0:
            self._logger.error("No instructions available to iterate!")
            return

        self._iterating = True
        self._iteration_routine = asyncio.async(self._iterate_instructions())

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

                self._trigger_instruction_callback(instruction)

        self._logger.info("Finished iterating instructions")
        self._trigger_complete_callback()
        self._iterating = False
        self._iteration_routine = None

    # INTERNAL METHODS
    # =========================================================================

    def _trigger_instruction_callback(self, instruction):
        if self._instruction_callback is not None:
            self._logger.info("Triggering instruction callback")
            self._instruction_callback(instruction)

    def _trigger_complete_callback(self):
        if self._complete_callback is not None:
            self._logger.info("Triggering complete callback")
            self._complete_callback()

    def _stop_running_routines(self):
        """ Stops the coroutine that executes the instruction iteration
        """

        if self._iteration_routine is not None:
            self._logger.debug("Killing running instruction execution routine")
            self._iterating = False
            # TODO: Test this. May not actually be able to cancel a coroutine except from  another coroutine
            self._iteration_routine.cancel()
            self._iteration_routine = None

    # TODO: Duplicate code. Generalise callback handling
    def _check_callable(self, to_call):
        """ Checks whether to_call is a valid callable
        """

        if not callable(to_call):
            self._logger.error("Error! Variable passed is not callable! Ignoring.")
            return False

        return True
