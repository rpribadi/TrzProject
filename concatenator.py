import argparse
import glob
import shutil
import os

parser = argparse.ArgumentParser(
    description="Simple Python utility to concat files into one."
)

parser.add_argument(
    '-d',
    '--dir',
    dest='directory',
    nargs="?",
    help='Folder path of input files'
)
parser.add_argument(
    '-i',
    '--in',
    dest='input_file',
    help='Input files, ex: \*.txt, \*.csv, ..',
    required=True
)
parser.add_argument(
    '-o', '--out',
    dest='output_file',
    help='Output file.',
    required=True
)


def concat_files(directory, input_file, output_file):
    print "Opening output file:", output_file
    with open(output_file, 'w') as o_file:
        if directory:
            print "Changing directory to", directory
            os.chdir(directory)

        for filename in glob.glob(input_file):
            with open(filename) as i_file:
                print " - Adding file:", filename
                shutil.copyfileobj(i_file, o_file)

    print "Done."


if __name__ == '__main__':
    args = parser.parse_args()
    concat_files(args.directory, args.input_file, args.output_file)
