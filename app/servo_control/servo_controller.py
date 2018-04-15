""" Overall servo controller. Executes servo control instructions by passing them
    to the communicator
"""

import logging

from libs.config.path_helper import PathHelper
from libs.callback_handling.callback_manager import CallbackManager

from app.servo_control.instruction_iterator import InstructionIterator
from app.servo_control.instruction_list import InstructionList, InstructionTypes
from app.servo_control.phoneme_map import PhonemeMap
from app.servo_control.servo_positions import ServoPositions
from app.servo_control.instruction_list_builder import InstructionListBuilder

# TODO: Lot of code duplication present in this class. Should be able to reduce
#           with better handling of instruction merging and deduplication
# IDEA: Record position instructions as a % of the possible movment, not as fixed positions.
#           Would account for changing servo limits without needing to adjust/re-record all animations

class ServoController:
    def __init__(self, servo_communicator):
        self._logger = logging.getLogger('servo_controller')
        self._servo_communicator = servo_communicator
        self._phoneme_map = PhonemeMap()
        self._list_builder = InstructionListBuilder()
        self._overridden_servo_positions = None
        self._cbm = CallbackManager(['move_instruction', 'stop_instruction', 'instructions_complete'], self)
        self._instruction_iterators = {}
        self._last_sent = ServoPositions({})

    def prepare_instructions(self, instructions_filename, without_servos=None, as_override=False):
        """ Prepares a list of instructions for executing from the argument file
            without_servos defines which servos in this instruction list should be ignored
            as_override defines whether to override servo positions from other instruction sets
        """

        options = {
            'without_servos'    : without_servos,
            'override'          : as_override,
            'execute_callback'  : self._execute_instruction,
            'complete_callback' : self._instructions_complete
        }
        instruction_list = self._list_builder.build(instructions_filename)
        iterator_info = InstructionListBuilder.create_iterator(instruction_list, **options)
        self._instruction_iterators[iterator_info['id']] = iterator_info
        return iterator_info['iterator']

    def execute_instructions(self):
        """ Executes all currently prepared instructions
        """

        self._logger.info("Executing all loaded servo instructions")
        if not self._instruction_iterators:
            self._cbm.trigger_instructions_complete_callback()
            return

        # Run all primary iterators. Nested iterators will be run when triggered by parent
        for iterator_info in self._instruction_iterators.values():
            iterator_info['iterator'].iterate_instructions()

    def any_instructions_loaded(self):
        """ Returns whether we have any instructions loaded and ready to execute
        """

        return len(self._instruction_iterators) > 0

    def stop_execution(self):
        """ Stops any instruction execution
        """

        for iterator_info in self._instruction_iterators.values():
            iterator_info['iterator'].stop()

    def stop(self):
        """ Stop the servo controller and any dependent object
        """

        self.stop_execution()
        self._servo_communicator.stop()

    def override_control(self, servo_positions):
        """ Provides a way to override the playback instructions from file based playback
            We use this to override any instruction based control with the current
            joystick control
        """

        self._logger.debug("Overriding control with %s", servo_positions.positions)

        if self._overridden_servo_positions is None:
            self._overridden_servo_positions = servo_positions
        else:
            self._overridden_servo_positions = self._overridden_servo_positions.merge(servo_positions)

        self._logger.debug("Final Override: %s", self._overridden_servo_positions.positions)

        # Get a set of servo positions without duplicates of what was last sent
        to_send = self._overridden_servo_positions.without_duplicates(self._last_sent)
        self._last_sent = self._last_sent.merge(to_send)

        # Immediately send override positions through to communicator and notify
        self._servo_communicator.move_to(to_send)
        self._cbm.trigger_move_instruction_callback(to_send.positions)

    def clear_control_override(self, servos):
        """ Clears the argument servos out of any set servo control override. Expects list/set
            of servo pins
        """

        self._logger.debug("Clearing position override for: %s", servos)
        if self._overridden_servo_positions is None:
            return

        self._overridden_servo_positions.clear_servos(servos)

    # CALLBACKS
    # =========================================================================

    def _execute_instruction(self, instruction, iterator_id):
        """ Called by the instruction iterator each time an instruction should be executed
        """

        # self._logger.debug("Executing %s Instruction from iterator %s", instruction.instruction_type.name, iterator_id)
        iterator_info = self._instruction_iterators[iterator_id]

        if instruction.instruction_type == InstructionTypes.PHONEME:
            self._execute_phoneme_instruction(instruction)
        elif instruction.instruction_type == InstructionTypes.POSITION:
            self._execute_position_instruction(instruction, iterator_info)
        elif instruction.instruction_type == InstructionTypes.STOP:
            self._execute_stop_instruction(instruction)
        else:
            self._logger.error("Unhandled instruction type: %s. Cannot execute!", instruction.instruction_type)

    def _instructions_complete(self, iterator_id):
        """ Called by the instruction iterator when iteration complete
        """

        self._logger.info("Instruction execution complete for iterator: %s", iterator_id)
        if iterator_id in self._instruction_iterators:
            iterator_info = self._instruction_iterators[iterator_id]
            if iterator_info['override']:
                self._logger.debug("Clearing overrides from instruction iterator")
                self.clear_control_override(iterator_info['overridden'])

            self._logger.debug("Clearing instruction iterator")
            del self._instruction_iterators[iterator_id]

        if not self._instruction_iterators:
            self._logger.info("Notifying all instructions executed")
            self._cbm.trigger_instructions_complete_callback()
        else:
            self._logger.debug("%d iterators remaining",len(self._instruction_iterators))

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

        to_send = servo_positions.without_duplicates(self._last_sent)
        self._last_sent = self._last_sent.merge(to_send)

        self._cbm.trigger_move_instruction_callback(to_send.positions)
        self._servo_communicator.move_to(to_send, instruction.move_time)

    # FIXME: If overriding control, excluded servos settings are ignored
    def _execute_position_instruction(self, instruction, iterator_info):
        """ Send a position directly from the CSV to the servos.
            Allows servos to be excluded if specified in iterator_info
            Allows this instruction to override other instructions if specified in iterator_info
        """

        without_servos = iterator_info['without_servos']
        override = iterator_info['override']

        if instruction.position is None:
            self._logger.error("Unable to process POSITION instruction. Ignoring")
            return

        positions = ServoPositions(instruction.position)

        if override:
            iterator_info['overridden'].update(positions.controlled_servos())
            self.override_control(positions)
            return

        if self._overridden_servo_positions is not None:
            positions = positions.merge(self._overridden_servo_positions)

        to_send = positions.without_duplicates(self._last_sent)
        self._last_sent = self._last_sent.merge(to_send)

        self._cbm.trigger_move_instruction_callback(to_send.positions)

        positions_to_send = to_send.to_str(without=without_servos)
        # Only send move time if individual servo speeds aren't specified
        move_time = None if to_send.speed_specified else instruction.move_time
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
