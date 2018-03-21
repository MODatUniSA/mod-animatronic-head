""" Writes servo instructions to a CSV file
"""

import csv
import json
import logging
from datetime import datetime

from libs.config.path_helper import PathHelper

class InstructionWriter:
    def __init__(self, filename=None):
        self._logger = logging.getLogger("instruction_writer")
        self._filename = filename
        if self._filename == None:
            self._filename = type(self)._default_filename()

        self._file_path = PathHelper.instruction_path(self._filename)
        self._file = open(self._file_path, 'w')
        fieldnames = ['time','instruction','arg_1','arg_2']
        self._writer = csv.writer(self._file, delimiter=',', quotechar="'", quoting=csv.QUOTE_MINIMAL)
        self._writer.writerow(fieldnames)
        self._logger.debug("Initted")

    def stop(self):
        self._logger.debug("Stopping")

        self._file.close()

    def write_instruction(self, time, instruction_type, arg_1, arg_2=''):
        self._logger.debug("Writing instruction row")

        row = [
            time,
            instruction_type if isinstance(instruction_type, str) else instruction_type.name,
            json.dumps(arg_1),
            json.dumps(arg_2)
        ]

        self._writer.writerow(row)

    @staticmethod
    def _default_filename():
        dt = datetime.now()
        return "recorded_{}.csv".format(dt.strftime('%Y-%m-%d_%H:%M:%S'))
