import argparse


def utf16_to_8(inFile, outFile):
    with open(inFile, 'r', encoding="utf-16") as i, open(outFile, 'w+', encoding="utf-8") as o:
        for line in i:
            o.write(line)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=str, help="utf16 file")
    parser.add_argument("output", type=str, help="utf8 file")
    args = parser.parse_args()
    utf16_to_8(args.input, args.output)
