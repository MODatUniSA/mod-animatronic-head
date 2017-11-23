""" Overall servo controller. Executes servo control instructions by passing them to the communicator
"""

import logging

from app.servo_control.instruction_iterator import InstructionIterator
from app.servo_control.instruction_list import InstructionList, InstructionTypes
from app.servo_control.phoneme_map import PhonemeMap

# TODO: Provide a way to interrupt/stop this (and triggered children) at any time
class ServoController:
    def __init__(self, servo_communicator):
        self._logger = logging.getLogger('servo_controller')
        self._servo_communicator = servo_communicator
        self._instruction_iterator = InstructionIterator()
        self._instruction_list = None
        self._phoneme_map = PhonemeMap()

        self._instruction_iterator.set_intruction_callback(self._execute_instruction)
        self._instruction_iterator.set_complete_callback(self._instructions_complete)

    def prepare_instructions(self, instructions_filename):
        """ Prepares a list of instructions for executing from the argument file
        """

        self._instruction_list = InstructionList(instructions_filename)

    def execute_instructions(self):
        if self._instruction_list is None:
            self._logger.error("No instructions loaded. Cannot execute")

        self._logger.info("Executing Servo Instructions")
        self._instruction_iterator.iterate_instructions(self._instruction_list)

    def stop(self):
        """ Stop the servo controller and any dependent object
        """

        self._servo_communicator.stop()


    # CALLBACKS
    # =========================================================================

    def _execute_instruction(self, instruction):
        """ Called by the instruction iterator each time an instruction should be executed
        """

        self._logger.info("Executing %s Instruction", instruction.instruction_type.name)
        if instruction.instruction_type == InstructionTypes.PHONEME:
            self._execute_phoneme_instruction(instruction)

    def _instructions_complete(self):
        """ Called by the instruction iterator when iteration complete
        """

        self._logger.info("Instruction execution complete")
        self._instruction_list = None

    # INTERNAL METHODS
    # =========================================================================

    def _execute_phoneme_instruction(self, instruction):
        """ Executes a single phoneme instruction, which sends a message to the mouth servos to move
        """

        servo_positions = self._phoneme_map['pins'][instruction.phoneme]
        self._logger.debug("Sending Phoneme: %s", instruction.phoneme)
        self._logger.debug("Sending servo positions: %s",servo_positions)

        # Move to servo positions in shortest time possible
        self._servo_communicator.move_to(servo_positions, 200)
