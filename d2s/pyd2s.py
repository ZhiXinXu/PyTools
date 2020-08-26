import getopt
import os
import sys

def convert(filename):
    data = []
    with open(filename, 'rb') as f:
        data = f.read()
    print('# Read ' + str(len(data)) + ' bytes from ' + filename)
    print('{', end='')
    for ch in data:
        print(hex(ch) + ',', end='')
    print('}')


def output_usage():
    print('Converts data to {0xa,0xf,...}')
    print('pyd2s.py -f <data file name>')


def main():
    if len(sys.argv) > 1:
        try:
            opts, args = getopt.getopt(sys.argv[1:], 'f:', [])
        except getopt.GetoptError:
            output_usage()
            sys.exit(1)

        for opt, arg in opts:
            if opt == '-f':
                convert(arg)

    else:
        output_usage()
        sys.exit(2)


if __name__ == '__main__':
    main()
