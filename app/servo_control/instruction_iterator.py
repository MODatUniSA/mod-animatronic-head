""" Iterates over an InstructionList, passing each instruction to a callback at the appropriate time
"""

import logging
import asyncio
import time

from libs.callback_handling.callback_manager import CallbackManager
from libs.config.device_config import DeviceConfig

class InstructionIterator:
    def __init__(self):
        self._logger = logging.getLogger('instruction_iterator_{}'.format(id(self)))
        config                  = DeviceConfig.Instance()
        logging_config          = config.options['LOGGING']
        self._warning_threshold = logging_config.getfloat('INSTRUCTION_TIME_WARNING_THRESHOLD')
        self._log_timing        = logging_config.getboolean('LOG_INSTRUCTION_TIMING')
        self._threshold_str     = "Time offset diff of %.2f greater than allowed threshold"
        self._timing_str        = "Executing instructions with time offset %.2f at %.2f seconds after iteration start (Diff: %.2f)"
        self._iteration_routine = None
        self._iterating         = False
        self._instruction_list  = None
        # Using 2 separate callback managers so we don't need to use call soon on the frequently
        # triggering instruction callback
        self._cbm_complete = CallbackManager(['complete'], self)
        self._cbm_instruction = CallbackManager(['instruction'], self, False)

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
            self._cbm_complete.trigger_complete_callback(id(self))
            return

        if not self._instruction_list.instructions:
            self._logger.error("No instructions in list to iterate!")
            self._cbm_complete.trigger_complete_callback(id(self))
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

        self._logger.info("Starting iteration of instructions in %s",self._instruction_list.files)

        start_time  = time.time()
        time_passed = 0

        for time_offset, instructions in self._instruction_list.instructions.items():
            if not self._iterating:
                self._logger.info("Interrupting instruction iteration")
                break

            if time_offset > time_passed:
                # Wait until we should execute the next instruction
                to_wait = time_offset - time_passed - 0.005
                yield from asyncio.sleep(to_wait)

            time_passed = time.time() - start_time

            if self._iterating:
                time_diff = time_passed - time_offset
                if self._log_timing or time_diff >= self._warning_threshold:
                    self._logger.debug(self._timing_str, time_offset, time_passed, time_diff)
                if time_diff >= self._warning_threshold:
                    # IDEA: May want to skip instructions if we fall behind to make up lost time. Similar to dropping frames.
                    self._logger.warning(self._threshold_str, time_diff)
                for instruction in instructions.values():
                    self._cbm_instruction.trigger_instruction_callback(instruction, id(self))

        self._logger.info("Finished iterating instructions")
        self._cbm_complete.trigger_complete_callback(id(self))
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
            self._cbm_complete.trigger_complete_callback(id(self))
