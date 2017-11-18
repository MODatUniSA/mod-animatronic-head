""" For parsing/storing/executing instructions for the servos to execute
"""

import csv

from libs.config.path_helper import PathHelper

class ServoInstruction:
    """ Storage class. Stores a single instruction to send to the servos.
    """

    def __init__(self, info_row):
        self.time_offset = float(info_row['time'])
        self.instruction = info_row['instruction'].upper()
        self.arg = info_row['arg']
        self.phoneme = None

        self._set_instruction_arg()

    def _set_instruction_arg(self):
        """ Assigns this instruction's argument to an instance variable depending on instruction type
            Just used for readable access to args
        """

        if self.instruction == 'PHONEME':
            self.phoneme = self.arg

class InstructionList:
    def __init__(self, filename):
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
