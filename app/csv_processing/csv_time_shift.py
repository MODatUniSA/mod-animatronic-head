""" Time shifts an instruction CSV by a fixed amount
"""

import os
import argparse
import csv
import json

from app.servo_control.instruction_writer import InstructionWriter
from libs.config.path_helper import PathHelper

class CsvTimeShift:
    def __init__(self, input_filename, output_filename=None, shift_amount=0):
        self._input_filename = input_filename
        self._input_file_path = self._file_path = PathHelper.instruction_path(input_filename)
        self._output_filename = output_filename
        self._shift_amount = shift_amount

        if self._output_filename is None:
            self._output_filename = self._infer_output_file_name()

        print("Input: {}".format(self._input_filename))
        print("Output: {}".format(self._output_filename))
        print("-----\n")

        self._instruction_writer = InstructionWriter(self._output_filename)

    def shift(self):
        """ Iterate over input file and convert to output file
        """

        with open(self._input_file_path, newline='') as csvfile:
            instruction_reader = csv.reader(csvfile, delimiter=',', quotechar="'")
            headers = next(instruction_reader)

            for row in instruction_reader:
                dict_row = {key: value for key, value in zip(headers, row)}
                shifted_time = self._shift_time(dict_row['time'])
                self._instruction_writer.write_instruction(
                    shifted_time,
                    dict_row['instruction'],
                    json.loads(dict_row['arg_1']),
                    dict_row.get('arg_2')
                )

        self._instruction_writer.stop()

    def _shift_time(self, input_time):
        return round(max(0, float(input_time) + self._shift_amount), 2)

    def _infer_output_file_name(self):
        """ Infer output file name from input file. Used if no output file name passed
        """

        filename, file_extension = os.path.splitext(self._input_filename)
        out_filename = "{}_shifted.csv".format(filename)
        return out_filename

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument("--input", dest='input_filename', help="Input file")
    parser.set_defaults(input_filename=None)

    parser.add_argument("--output", dest='output_filename', help="Output file (optional) - Inferred from input filename if absent.")
    parser.set_defaults(output_filename=None)

    parser.add_argument("--shift_amount", dest='shift_amount', help="How much to shift the input csv time")
    parser.set_defaults(shift_amount=0)

    args = parser.parse_args()

    processor = CsvTimeShift(args.input_filename, args.output_filename, float(args.shift_amount))
    processor.shift()
