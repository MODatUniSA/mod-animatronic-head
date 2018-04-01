""" For parsing/storing/executing instructions for the servos to execute
"""

import csv
import logging
import json
from enum import Enum
from contextlib import suppress
from collections import OrderedDict

from libs.config.path_helper import PathHelper
from libs.config.device_config import DeviceConfig
from app.servo_control.phoneme_map import Phonemes
from app.servo_control.position_instruction_decoder import PositionInstructionDecoder

class InstructionTypes(Enum):
    # Set the mouth/jaw servos to a named phoneme
    PHONEME = 0
    # Load an execute an additional sequence of instructions in parallel with the current
    PARALLEL_SEQUENCE = 1
    # Set the servos to a fixed, specified position. Will still apply clamping.
    POSITION = 2
    # Stop the servos in their current position
    STOP = 3

class ServoInstruction:
    """ Storage class. Stores a single instruction to send to the servos.
    """

    def __init__(self, info_row, default_move_time_ms):
        self.time_offset = float(info_row['time'])
        # TODO: Gracefully handle unrecognised instruction. Just ignore.
        self.instruction_type = InstructionTypes[info_row['instruction'].upper()]
        self.arg_1 = info_row['arg_1']
        self.arg_2 = info_row.get('arg_2', default_move_time_ms) or default_move_time_ms

        # Semantic sugar for accessing instruction arguments
        self.phoneme = None
        self.filename = None
        self.position = None
        self.move_time = None
        self.servos = None
        self._set_instruction_args()

    def is_parallel_sequence(self):
        return self.instruction_type == InstructionTypes.PARALLEL_SEQUENCE

    def _set_instruction_args(self):
        """ Assigns this instruction's argument to an instance variable depending on instruction type
            Just used for readable access to args
        """

        # TODO: Gracefully handle unrecognised phoneme. Default?

        if self.instruction_type == InstructionTypes.PHONEME:
            self.phoneme = Phonemes[self.arg_1.upper()]
        elif self.instruction_type == InstructionTypes.PARALLEL_SEQUENCE:
            self.filename = self.arg_1
        elif self.instruction_type == InstructionTypes.POSITION:
            with suppress(json.decoder.JSONDecodeError):
                self.position = json.loads(self.arg_1, cls=PositionInstructionDecoder)
        elif self.instruction_type == InstructionTypes.STOP:
            with suppress(json.decoder.JSONDecodeError):
                self.servos = set(json.loads(self.arg_1))

        if self.instruction_type != InstructionTypes.PARALLEL_SEQUENCE:
            self.move_time = self.arg_2

    def merge(self, other):
        """ Merge this instruction with another instruction.
            Only valid for POSITION instructions
        """

        if not self.instruction_type == InstructionTypes.POSITION and\
            other.instruction_type == InstructionTypes.POSITION:
            return

        self.position.update(other.position)


class InstructionList:
    def __init__(self):
        self._logger = logging.getLogger('instruction_list')
        self._config = DeviceConfig.Instance()
        self._default_move_time_ms = self._config.options['SERVO_CONTROL'].getint('DEFAULT_MOVE_TIME_MS')
        self.files = []
        self._unsorted_instructions = {}
        self.instructions = OrderedDict()

    # INTERNAL METHODS
    # =========================================================================

    def load_instructions(self, filename):
        """ Loads the argument instructions
            Returns whether the load was successful, and the list of parallel sequences found in the instructions
        """

        if not PathHelper.is_valid_instruction_file(filename):
            self._logger.error("Instruction file %s not found. Please make sure this exists, and we have read permissions.", filename)
            return False, None

        self.files.append(filename)
        return True, self._parse_instructions_csv(PathHelper.instruction_path(filename))

    def sort_instructions(self):
        self.instructions = OrderedDict(sorted(self._unsorted_instructions.items()))

    def merge(self, other):
        """ Merges instruction lists
        """

        self._logger.debug("Merging instruction list for %s into %s", other.files, self.files)
        self.files.append(other.files[0])

        for instructions in other.instructions.values():
            for instruction in instructions.values():
                self._add_to_instructions(instruction)

    def _parse_instructions_csv(self, file_path):
        parallel_sequences = []

        with open(file_path, newline='') as csvfile:
            instruction_reader = csv.reader(csvfile, delimiter=',', quotechar="'")
            headers = next(instruction_reader)

            for row in instruction_reader:
                dict_row = {key: value for key, value in zip(headers, row)}
                instruction = ServoInstruction(dict_row, self._default_move_time_ms)
                if instruction.is_parallel_sequence():
                    parallel_sequences.append(instruction)
                else:
                    self._add_to_instructions(instruction)

        return parallel_sequences


    def _add_to_instructions(self, instruction):
        """ Adds the instruction to the list, merging with existing instructions if present
        """

        instructions_for_time = self._unsorted_instructions.get(instruction.time_offset)
        if instructions_for_time is None:
            self._unsorted_instructions[instruction.time_offset] = { instruction.instruction_type : instruction }
        else:
            matching_instruction = instructions_for_time.get(instruction.instruction_type)
            if matching_instruction is None\
                or instruction.instruction_type == InstructionTypes.PHONEME:
                self._unsorted_instructions[instruction.time_offset][instruction.instruction_type] = instruction
            else:
                matching_instruction.merge(instruction)
