""" Overall servo controller. Executes servo control instructions by passing them to the communicator
"""

import logging

from libs.config.path_helper import PathHelper

from app.servo_control.instruction_iterator import InstructionIterator
from app.servo_control.instruction_list import InstructionList, InstructionTypes
from app.servo_control.phoneme_map import PhonemeMap
from app.servo_control.expression_map import ExpressionMap
from app.servo_control.servo_positions import ServoPositions

class ServoController:
    def __init__(self, servo_communicator):
        self._logger = logging.getLogger('servo_controller')
        self._servo_communicator = servo_communicator
        self._instruction_list = None
        self._phoneme_map = PhonemeMap()
        self._expression_map = ExpressionMap()
        self.phonemes_override_expression = False

        # REVISE: Do we need to distinguish between main and nested iterators?
        self._main_instruction_iterator = self._create_instruction_iterator()
        # Iterators for any nested instruction sequences
        self._nested_instruction_iterators = {}

    def prepare_instructions(self, instructions_filename):
        """ Prepares a list of instructions for executing from the argument file
        """

        self._instruction_list = InstructionList(instructions_filename)

    def execute_instructions(self):
        if self._instruction_list is None:
            self._logger.error("No instructions loaded. Cannot execute")

        self._logger.info("Executing Servo Instructions")
        self._main_instruction_iterator.iterate_instructions(self._instruction_list)

    def stop(self):
        """ Stop the servo controller and any dependent object
        """

        # TODO: Stop any instruction iterators, including nested ones
        self._servo_communicator.stop()

    # CALLBACKS
    # =========================================================================

    def _execute_instruction(self, instruction):
        """ Called by the instruction iterator each time an instruction should be executed
        """

        self._logger.info("Executing %s Instruction", instruction.instruction_type.name)
        if instruction.instruction_type == InstructionTypes.PHONEME:
            self._execute_phoneme_instruction(instruction)
        elif instruction.instruction_type == InstructionTypes.EXPRESSION:
            self._execute_expression_instruction(instruction)
        elif instruction.instruction_type == InstructionTypes.PARALLEL_SEQUENCE:
            self._execute_parallel_sequence_instruction(instruction)
        elif instruction.instruction_type == InstructionTypes.POSITION:
            self._execute_position_instruction(instruction)
        else:
            self._logger.error("Unhandled instruction type: %s. Cannot execute!", instruction.instruction_type)

    def _instructions_complete(self, iterator_id):
        """ Called by the instruction iterator when iteration complete
        """

        self._logger.info("Instruction execution complete for iterator: %s", iterator_id)
        if iterator_id in self._nested_instruction_iterators:
            self._logger.info("Clearing nested instruction iterator")
            del(self._nested_instruction_iterators[iterator_id])

    # INTERNAL METHODS
    # =========================================================================

    def _create_instruction_iterator(self):
        instruction_iterator = InstructionIterator()
        instruction_iterator.set_intruction_callback(self._execute_instruction)
        instruction_iterator.set_complete_callback(self._instructions_complete)
        return instruction_iterator

    # INSTRUCTION EXECUTION
    # =========================================================================

    def _execute_phoneme_instruction(self, instruction):
        """ Executes a single phoneme instruction, which sends a message to the mouth servos to move
        """

        # TODO: Gracefully handle phoneme not mapped
        servo_positions = self._phoneme_map['pins'][instruction.phoneme].positions_str
        self._logger.debug("Sending Phoneme: %s", instruction.phoneme)
        self._logger.debug("Sending servo positions: %s",servo_positions)

        # TODO: Support different movement speeds?
        self._servo_communicator.move_to(servo_positions, 200)

    def _execute_expression_instruction(self, instruction):
        """ Executes a single expression instruction, which sends a message to the face servos to move
        """

        servo_positions = self._expression_map['pins'][instruction.expression]
        if self.phonemes_override_expression:
            self._logger.debug("Sending expression w/o mouth")
            position_to_send = servo_positions.positions_without_mouth_str
        else:
            self._logger.debug("Sending expression w/ mouth")
            position_to_send = servo_positions.positions_str

        self._logger.debug("Sending Expression: %s", instruction.expression)
        self._logger.debug("Sending servo positions: %s", position_to_send)

        self._servo_communicator.move_to(position_to_send, 200)

    # TODO: Loading and executing nested instructions is rather dangerous, as files could contain loops/self references that cause infinite loops. Should guard against this.
    def _execute_parallel_sequence_instruction(self, instruction):
        """ Loads a named instruction sequence into an instruction list and starts iteration.
            This allows mulitple lists of instructions to be triggered in parallel
        """

        if not PathHelper.is_valid_instruction_file(instruction.filename):
            self._logger.error = "Nested sequence is not a valid filename. Can't load."
            return

        self._logger.info("Loading nested instruction sequence: %s", instruction.filename)
        instruction_list = InstructionList(instruction.filename)
        nested_iterator = self._create_instruction_iterator()
        nested_iterator.iterate_instructions(instruction_list)
        self._nested_instruction_iterators[id(nested_iterator)] = nested_iterator

    def _execute_position_instruction(self, instruction):
        """ Send a position directly from the CSV to the servos. Still applies limiting, and allows phonemes to override mouth servos
        """

        if instruction.position is None:
            self._logger.error("Unable to process POSITION instruction. Ignoring")
            return

        positions = ServoPositions(instruction.position)

        if self.phonemes_override_expression:
            self._logger.debug("Sending raw positions w/o mouth")
            positions_to_send = positions.positions_without_mouth_str
        else:
            self._logger.debug("Sending raw positions w/ mouth")
            positions_to_send = positions.positions_str

        # TODO: Support different movement speeds per position?
        self._servo_communicator.move_to(positions_to_send, 200)
