""" For parsing/storing/executing instructions for the servos to execute
"""

import csv
import logging
import json
from enum import Enum
from contextlib import suppress

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

class InstructionList:
    def __init__(self, filename):
        self._logger = logging.getLogger('instruction_list')
        self._config = DeviceConfig.Instance()
        self._default_move_time_ms = self._config.options['SERVO_CONTROL'].getint('DEFAULT_MOVE_TIME_MS')
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
            instruction_reader = csv.reader(csvfile, delimiter=',', quotechar="'")
            headers = next(instruction_reader)

            for row in instruction_reader:
                dict_row = {key: value for key, value in zip(headers, row)}
                instruction = ServoInstruction(dict_row, self._default_move_time_ms)
                self.instructions.append(instruction)
