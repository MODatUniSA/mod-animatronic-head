""" Slices a collection of instruction csvs into new files
"""

import os
import argparse
import csv
import json

from app.servo_control.instruction_writer import InstructionWriter
from libs.config.path_helper import PathHelper

class CsvSlicer:
    def __init__(self, input_filenames):
        self._input_paths = self._file_paths(input_filenames)
        print("Inputs: {}".format(self._input_paths))
        print("-----\n")

        # self._instruction_writer = InstructionWriter(self._output_filename)

    def slice(self, start_time=0, end_time=0):
        """ Iterate over input file and convert to output file
        """

        if end_time <= start_time:
            print("End time must be after start time!")
            return


        for input_file in self._input_paths:
            base_dir = os.path.dirname(input_file)
            slice_dir = self._create_slice_directory(base_dir, start_time, end_time)

            writer = InstructionWriter(self._output_filename(slice_dir, input_file), False)

            with open(input_file, newline='') as csvfile:
                instruction_reader = csv.reader(csvfile, delimiter=',', quotechar="'")
                headers = next(instruction_reader)
                write_started = False

                previous_row = {}
                for row in instruction_reader:
                    dict_row = {key: value for key, value in zip(headers, row)}
                    if previous_row == {}:
                        previous_row = dict_row

                    row_time = float(dict_row['time'])
                    if row_time > end_time:
                        break

                    if  row_time == start_time:
                        dict_row['time'] = 0
                        self._write_row(writer, dict_row)
                        write_started = True
                    elif row_time > start_time:
                        if not write_started:
                            previous_row['time'] = 0
                            self._write_row(writer, previous_row)
                            write_started = True

                        dict_row['time'] = self._shift_time(dict_row['time'], -start_time)
                        self._write_row(writer, dict_row)

                    previous_row = dict_row

            writer.stop()

    def _write_row(self, writer, row):
        try:
            arg_1 = json.loads(row['arg_1'])
        except json.decoder.JSONDecodeError:
            arg_1 = row['arg_1']
        writer.write_instruction(
            row['time'],
            row['instruction'],
            arg_1,
            row.get('arg_2')
        )

    def _shift_time(self, input_time, shift_amount):
        return round(max(0, float(input_time) + shift_amount), 2)

    def _file_paths(self, filenames):
        return [PathHelper.instruction_path(filename) for filename in filenames.split(',')]

    def _output_filename(self, base_dir, input_filename):
        """ Infer output file name from input file. Used if no output file name passed
        """

        filename, file_extension = os.path.splitext(input_filename)
        out_filename = "{}/{}{}".format(base_dir, os.path.basename(filename), file_extension)
        return out_filename

    def _create_slice_directory(self, base_dir, start_time, end_time):
        dirname = '{}/{}_to_{}'.format(base_dir, start_time, end_time)

        if not os.path.exists(dirname):
            os.makedirs(dirname)
        return dirname

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument("--input", dest='input_filenames', help="Input files")
    parser.set_defaults(input_filenames=None)

    parser.add_argument("--start", dest='arg_start_time', help="Where to start the slice")
    parser.set_defaults(arg_start_time=0)

    parser.add_argument("--end", dest='arg_end_time', help="Where to end the slice")
    parser.set_defaults(arg_end_time=0)

    args = parser.parse_args()

    slicer = CsvSlicer(args.input_filenames)

    arg_start_time = float(args.arg_start_time)
    arg_end_time = float(args.arg_end_time)
    if arg_start_time > 0 or arg_end_time > 0:
        slicer.slice(arg_start_time, arg_end_time)
