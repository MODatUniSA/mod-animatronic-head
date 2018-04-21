""" Writes servo instructions to a CSV file
"""

import csv
import json
import logging
import re
from datetime import datetime

from libs.config.path_helper import PathHelper

class InstructionWriter:
    def __init__(self, filename=None,prepend_instruction_path=True):
        self._logger = logging.getLogger("instruction_writer")
        self._filename = filename
        if self._filename == None:
            self._filename = type(self)._default_filename()

        if prepend_instruction_path:
            self._file_path = PathHelper.instruction_path(self._filename)
        else:
            self._file_path = self._filename

        self._file = open(self._file_path, 'w')
        fieldnames = ['time','instruction','arg_1','arg_2']
        self._writer = csv.writer(self._file, delimiter=',', quotechar="'", quoting=csv.QUOTE_MINIMAL)
        self._writer.writerow(fieldnames)
        self._logger.debug("Initted")

    def stop(self):
        self._logger.debug("Stopping")

        self._file.close()

    def write_instruction(self, time, instruction_type, arg_1, arg_2=None):
        self._logger.debug("Writing instruction row")

        row = [
            time,
            instruction_type if isinstance(instruction_type, str) else instruction_type.name,
            type(self).json_arg_clean(arg_1),
            type(self).json_arg_clean(arg_2)
        ]

        self._writer.writerow(row)

    @classmethod
    def json_arg_clean(cls, arg):
        """ Returns a clean version of a JSON arg. Used to avoid duplicating quotes when writing.
        """

        if arg is None:
            return arg

        if isinstance(arg, str):
            arg = re.sub(r'"', '', arg)
            if arg == '':
                arg = None
        else:
            arg = json.dumps(arg)

        return arg

    @staticmethod
    def _default_filename():
        dt = datetime.now()
        return "recorded_{}.csv".format(dt.strftime('%Y-%m-%d_%H:%M:%S'))
