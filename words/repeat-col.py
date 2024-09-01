import argparse
import os

def expand(inputFile, columns,  outputFile):
    with open(inputFile, 'r') as inFile, open(outputFile, 'w') as outFile:
        strings = inFile.read().split("\n")
        for a_str in strings:
            a_str = a_str.strip()
            if (len(a_str) == 0 or all(char.isspace() for char in a_str)):
                continue
            a_outstr = ""
            for i in range(columns):
                a_outstr += a_str;
                a_outstr += ". "
            outFile.write(a_outstr + "\n")
    return


if __name__ == '__main__':
    print("hello world!")
    parser = argparse.ArgumentParser()
    parser.add_argument("inputFile", type=str, help="original text file")
    parser.add_argument("repeatCols", type=int, help="repeat columns, default is 5")
    parser.add_argument("outputFile", type=str, help="output text file")
    args = parser.parse_args()

    expand(args.inputFile, args.repeatCols, args.outputFile)

