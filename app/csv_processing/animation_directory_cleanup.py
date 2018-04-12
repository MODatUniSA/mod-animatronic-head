""" Time shifts an instruction CSV by a fixed amount
"""

import argparse
import csv
import os
import re
import json

from libs.config.path_helper import PathHelper
from app.servo_control.instruction_list import InstructionTypes
from app.servo_control.instruction_writer import InstructionWriter

class AnimationDirectoryCleanup:
    def __init__(self, input_filename):
        self._input_filename = input_filename
        self._input_file_path = self._file_path = PathHelper.instruction_path(input_filename)
        self._input_base_path = os.path.dirname(self._input_file_path)
        self._output_filename = self._infer_output_file_name()
        self._output_file_path = self._file_path = PathHelper.instruction_path(self._output_filename)

        print("Input: {}".format(self._input_filename))
        print("-----\n")

        self._instruction_writer = InstructionWriter(self._output_filename)

    def cleanup(self):
        """ Iterate over input file to build a list of referenced files
        """

        referenced_files = self._referenced_file_list()
        self._delete_unreferenced_files(referenced_files)
        self._instruction_writer.stop()
        self._rename_loop_files()
        self._rename_io_files()

    def _referenced_file_list(self):
        """ Constructs the referenced file list, and also writes the new file with clean names
        """

        referenced_files = [os.path.basename(self._input_filename), os.path.basename(self._output_filename)]

        with open(self._input_file_path, newline='') as csvfile:
            instruction_reader = csv.reader(csvfile, delimiter=',', quotechar="'")
            headers = next(instruction_reader)

            for row in instruction_reader:
                dict_row = {key: value for key, value in zip(headers, row)}
                if InstructionTypes[dict_row['instruction']] == InstructionTypes.PARALLEL_SEQUENCE:
                    referenced_files.append(os.path.basename(dict_row['arg_1']))
                    arg_1 = re.sub(r'_loop_\d', '', dict_row['arg_1'])
                else:
                    try:
                        arg_1 = json.loads(dict_row['arg_1'])
                    except json.decoder.JSONDecodeError:
                        arg_1 = dict_row['arg_1']

                self._instruction_writer.write_instruction(
                    dict_row['time'],
                    dict_row['instruction'],
                    arg_1,
                    dict_row['arg_2']
                )

        return referenced_files

    def _delete_unreferenced_files(self, referenced_files):
        """ Delete all files not in the referenced_files list
        """

        to_delete = [
            os.path.join(self._input_base_path, filename) for filename
            in os.listdir(self._input_base_path)
            if os.path.isfile(os.path.join(self._input_base_path, filename)) and
            filename not in referenced_files
        ]

        for filename in to_delete:
            print("Deleting file: {}".format(filename))
            os.remove(filename)

    def _rename_loop_files(self):
        """ Strip loop suffix off all loop files
        """
        for filename in os.listdir(self._input_base_path):
            if not os.path.isfile(os.path.join(self._input_base_path, filename)):
                continue

            new_filename = re.sub(r'_loop_\d', '', filename)
            if new_filename == filename:
                continue

            print("Renaming {} to {}".format(filename, new_filename))
            old_path = os.path.join(self._input_base_path, filename)
            new_path = os.path.join(self._input_base_path, new_filename)
            os.rename(old_path, new_path)


    def _rename_io_files(self):
        os.rename(self._input_file_path, "{}.bak".format(self._input_file_path))
        os.rename(self._output_file_path, re.sub(r'_clean', '', self._output_file_path))

    def _infer_output_file_name(self):
        """ Infer output file name from input file. Used if no output file name passed
        """

        filename, file_extension = os.path.splitext(self._input_filename)
        out_filename = "{}_clean.csv".format(filename)
        return out_filename


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument("--input", dest='input_filename', help="Input file")
    parser.set_defaults(input_filename=None)

    args = parser.parse_args()

    cleaner = AnimationDirectoryCleanup(args.input_filename)
    cleaner.cleanup()
