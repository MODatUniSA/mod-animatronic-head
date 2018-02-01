""" Converts output file from papagayo (Anime Studio export) to phoneme file
    Expected input is of the format:
    ----
    -1 O
    7 etc
    ----
    Outputs a CSV
    ----
    time,instruction,arg_1,arg_2
    0,PHONEME,O
    0.29,PHONEME,etc
    ----
"""

import os
import argparse
import csv

class PapagayoToPhoneme:
    def __init__(self, input_filename, output_filename=None, fps=24):
        self._input_filename = input_filename
        self._output_filename = output_filename
        self._fps = fps

        if self._output_filename is None:
            self._output_filename = self._infer_output_file_name()

        print("Input: {}".format(self._input_filename))
        print("Output: {}".format(self._output_filename))
        print("-----\n")

        self._output_file = open(self._output_filename, 'w')

        fieldnames = ['time','instruction','arg_1','arg_2']
        self._writer = csv.writer(self._output_file, delimiter=',', quotechar="'", quoting=csv.QUOTE_MINIMAL)
        self._writer.writerow(fieldnames)

    def convert(self):
        """ Iterate over input file and convert to output file
        """

        with open(self._input_filename) as f:
            for line in f:
                skip = False
                line_split = line.split(' ')
                if len(line_split) < 2:
                    skip = True
                else:
                    frame, phoneme = line_split
                    try:
                        frame = int(frame)
                    except ValueError as err:
                        skip = True

                if skip:
                    print("Skipping line: {}".format(line.rstrip()))
                    continue

                print("Converting Line: {}".format(line.rstrip()))
                seconds = round(max(0, frame / self._fps), 2)
                phoneme = phoneme.rstrip()
                self._write_instruction(seconds, phoneme)

        self._output_file.close()

    def _write_instruction(self, time, phoneme):
        """ Write a single line to the output csv
            time,instruction,arg_1,arg_2
            0.8,PHONEME,closed
        """

        row = [
            time,
            'PHONEME',
            phoneme,
        ]

        self._writer.writerow(row)

    def _infer_output_file_name(self):
        """ Infer output file name from input file. Used if no output file name passed
        """

        filename, file_extension = os.path.splitext(self._input_filename)
        out_filename = "{}_phonemes.csv".format(filename)
        return out_filename

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument("--input", dest='input_filename', help="Input file")
    parser.set_defaults(input_filename=None)

    parser.add_argument("--output", dest='output_filename', help="Output file (optional) - Inferred from input filename if absent.")
    parser.set_defaults(output_filename=None)

    parser.add_argument("--fps", dest='fps', help="Exported FPS (optional) - Used to translate frame number to seconds. Defaults to 24.")
    parser.set_defaults(fps=24)

    args = parser.parse_args()

    ptp = PapagayoToPhoneme(args.input_filename, args.output_filename, int(args.fps))
    ptp.convert()
