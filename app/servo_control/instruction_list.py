""" For parsing/storing/executing instructions for the servos to execute
"""

import csv
import logging
from enum import Enum, auto

from libs.config.path_helper import PathHelper
from app.servo_control.phoneme_map import Phonemes
from app.servo_control.expression_map import Expressions

class InstructionTypes(Enum):
    # Set the mouth/jaw servos to a named phoneme
    PHONEME = auto()
    # Set the face servos to a mapped fixed expression
    EXPRESSION = auto()
    # Load an execute an additional sequence of instructions in parallel with the current
    NESTED_SEQUENCE = auto()
    # Set the servos to a fixed, specified position
    POSITION = auto()

class ServoInstruction:
    """ Storage class. Stores a single instruction to send to the servos.
    """

    def __init__(self, info_row):
        self.time_offset = float(info_row['time'])
        # TODO: Gracefully handle unrecognised instruction. Just ignore.
        self.instruction_type = InstructionTypes[info_row['instruction'].upper()]
        self.arg = info_row['arg']

        # Semantic sugar for accessing instruction arguments
        self.phoneme = None
        self.expression = None
        self.nested_filename = None
        self.positions = None
        self._set_instruction_arg()

    def _set_instruction_arg(self):
        """ Assigns this instruction's argument to an instance variable depending on instruction type
            Just used for readable access to args
        """

        # TODO: Gracefully handle unrecognised phoneme/expression. Default to rest?
        # TODO: Handle POSITION instruction

        if self.instruction_type == InstructionTypes.PHONEME:
            self.phoneme = Phonemes[self.arg.upper()]
        elif self.instruction_type == InstructionTypes.EXPRESSION:
            self.expression = Expressions[self.arg.upper()]
        elif self.instruction_type == InstructionTypes.NESTED_SEQUENCE:
            self.nested_filename = self.arg

class InstructionList:
    def __init__(self, filename):
        self._logger = logging.getLogger('instruction_list')
        self._filename = filename
        self._file_path = None
        self.instructions = []
        self._load_instructions()

    # INTERNAL METHODS
    # =========================================================================

    def _load_instructions(self):
        """ Loads the instructions in the csv passed to this class on init
        """

        if not PathHelper.is_valid_instruction_file(self._filename):
            self._logger.error("Instruction file %s not found. Please make sure this exists, and we have read permissions.", self._filename)
            return

        self._file_path = PathHelper.instruction_path(self._filename)
        self._parse_instructions_csv()

    def _parse_instructions_csv(self):
        with open(self._file_path, newline='') as csvfile:
            instruction_reader = csv.reader(csvfile, delimiter=',', quotechar='"')
            headers = next(instruction_reader)

            for row in instruction_reader:
                dict_row = {key: value for key, value in zip(headers, row)}
                instruction = ServoInstruction(dict_row)
                self.instructions.append(instruction)
