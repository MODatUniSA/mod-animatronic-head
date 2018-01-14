""" Overall servo controller. Executes servo control instructions by passing them to the communicator
"""

import logging

from libs.config.path_helper import PathHelper
from libs.callback_handling.callback_manager import CallbackManager

from app.servo_control.instruction_iterator import InstructionIterator
from app.servo_control.instruction_list import InstructionList, InstructionTypes
from app.servo_control.phoneme_map import PhonemeMap
from app.servo_control.expression_map import ExpressionMap
from app.servo_control.servo_positions import ServoPositions

# TODO: Send complete callback on completion of all iterators (including nested)

class ServoController:
    def __init__(self, servo_communicator):
        self._logger = logging.getLogger('servo_controller')
        self._servo_communicator = servo_communicator
        self._instruction_list = None
        self._phoneme_map = PhonemeMap()
        self._expression_map = ExpressionMap()
        self.phonemes_override_expression = False
        self._overridden_servo_positions = None
        self._cbm = CallbackManager(['move_instruction', 'stop_instruction'], self)

        # REVISE: Do we need to distinguish between main and nested iterators?
        #           Can all iterators be treated equally?
        self._main_instruction_iterator = self._create_instruction_iterator()
        # Iterators for any nested instruction sequences
        self._nested_instruction_iterators = {}

    # TODO: Need to be able to prepare mulitple sets of instructions for concurrent execution
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

    def override_control(self, servo_positions):
        """ Provides a way to override the playback instructions from file based playback
        """

        self._logger.debug("Overriding control with %s", servo_positions.positions)

        # REVISE: I believe we need to merge control overrides here, as we send
        #           the overrides separately per axis/control
        # Needs more testing.
        if self._overridden_servo_positions is None:
            self._overridden_servo_positions = servo_positions
        else:
            self._overridden_servo_positions = self._overridden_servo_positions.merge(servo_positions)

        self._logger.debug("Final Override: %s", self._overridden_servo_positions.positions)

        # Immediately send override positions through to communicator and notify
        self._servo_communicator.move_to(self._overridden_servo_positions)
        self._cbm.trigger_move_instruction_callback(self._overridden_servo_positions.positions)

    def clear_control_override(self, servos):
        """ Clears the argument servos out of any set servo control override
        """

        self._logger.debug("Clearing position override for: %s", servos)
        if self._overridden_servo_positions is None:
                return

        self._overridden_servo_positions.clear_servos(servos)

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
        elif instruction.instruction_type == InstructionTypes.STOP:
            self._execute_stop_instruction(instruction)
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
        instruction_iterator.add_instruction_callback(self._execute_instruction)
        instruction_iterator.add_complete_callback(self._instructions_complete)
        return instruction_iterator

    # INSTRUCTION EXECUTION
    # =========================================================================

    def _execute_phoneme_instruction(self, instruction):
        """ Executes a single phoneme instruction, which sends a message to the mouth servos to move
        """

        # TODO: Gracefully handle phoneme not mapped
        servo_positions = self._phoneme_map['pins'][instruction.phoneme]

        if self._overridden_servo_positions is not None:
            servo_positions = servo_positions.merge(self._overridden_servo_positions)

        self._logger.debug("Sending Phoneme: %s", instruction.phoneme)

        self._cbm.trigger_move_instruction_callback(servo_positions.positions)
        self._servo_communicator.move_to(servo_positions, instruction.move_time)

    def _execute_expression_instruction(self, instruction):
        """ Executes a single expression instruction, which sends a message to the face servos to move
        """

        servo_positions = self._expression_map['pins'][instruction.expression]
        if self._overridden_servo_positions is not None:
            servo_positions = servo_positions.merge(self._overridden_servo_positions)

        if self.phonemes_override_expression:
            self._logger.debug("Sending expression w/o mouth")
            position_to_send = servo_positions.positions_without_mouth_str
            self._cbm.trigger_move_instruction_callback(servo_positions.positions_without_mouth)
        else:
            self._logger.debug("Sending expression w/ mouth")
            position_to_send = servo_positions.positions_str
            self._cbm.trigger_move_instruction_callback(servo_positions.positions)

        self._logger.debug("Sending Expression: %s", instruction.expression)
        self._logger.debug("Sending servo positions: %s", position_to_send)

        self._servo_communicator.move_to(position_to_send, instruction.move_time)

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
        """ Send a position directly from the CSV to the servos. Applies limiting, and allows phonemes to override mouth servos
        """

        if instruction.position is None:
            self._logger.error("Unable to process POSITION instruction. Ignoring")
            return

        positions = ServoPositions(instruction.position)

        if self._overridden_servo_positions is not None:
            positions = positions.merge(self._overridden_servo_positions)

        if self.phonemes_override_expression:
            self._logger.debug("Sending raw positions w/o mouth")
            positions_to_send = positions.positions_without_mouth_str
            self._cbm.trigger_move_instruction_callback(positions.positions_without_mouth)
        else:
            self._logger.debug("Sending raw positions w/ mouth")
            positions_to_send = positions.positions_str
            self._cbm.trigger_move_instruction_callback(positions.positions)

        # Only send move time if individual servo speeds aren't specified
        move_time = None if positions.speed_specified else instruction.move_time
        self._servo_communicator.move_to(positions_to_send, move_time)

    def _execute_stop_instruction(self, instruction):
        """ Stops the servos specified by the instruction
        """

        # Don't stop servos whose control we're currently overriding
        to_stop = instruction.servos
        if self._overridden_servo_positions is not None:
            to_stop -= self._overridden_servo_positions.positions.keys()

        self._servo_communicator.stop_servos(instruction.servos)
        self._cbm.trigger_stop_instruction_callback(to_stop)
