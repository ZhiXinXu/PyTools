import argparse
import png


def _bin2png(binFile, width, height, pngFile):
    with open(binFile, 'rb') as inFile, open(pngFile, 'wb') as outFile:
        data = bytearray(inFile.read())
        png_writer = png.Writer(width, height, greyscale=False, alpha=True)
        png_writer.write_array(outFile, data)
    return True


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("binFile", type=str, help="binary input file")
    parser.add_argument("width", type=int, help="output image width")
    parser.add_argument("height", type=int, help="output image height")
    parser.add_argument("pngFile", type=str, help="output png file")
    args = parser.parse_args()
    if _bin2png(args.binFile, args.width, args.height, args.pngFile):
        print('"' + args.pngFile + '" saved.')
    else:
        print("Conversation failed.")
