import argparse
import os.path

import png


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press ⌘F8 to toggle the breakpoint.


def isFloat(str):
    return str.replace('.', '', 1).isdigit()


def read_cube(fileName):
    lut_size = -1
    lut_data = bytearray()
    pixels = -1

    with open(fileName) as aFile:
        for aLine in aFile:
            if lut_size < 0 and aLine.upper().startswith('LUT_3D_SIZE'):
                a = aLine.split()
                lut_size = int(a[1])
                lut_data = bytearray(lut_size * lut_size * lut_size * 4)
                print(f"lut size = {lut_size}")
                continue

            if pixels < 0 and aLine.upper().startswith('#LUT DATA POINTS'):
                pixels = 0
                continue

            if pixels < 0 and lut_size >= 0:
                print(f"for line:{aLine}")
                tmp = aLine.split()
                print(tmp)
                if len(tmp) == 3 and isFloat(tmp[0]) and isFloat(tmp[1]) and isFloat(tmp[2]):
                    pixels = 0
                    print(f"set pixels = 0 by line: {aLine}")
                else:
                    continue

            if pixels >= 0:
                nums = aLine.split()
                if len(nums) == 3:
                    # print(nums)
                    lut_data[pixels * 4] = int(float(nums[0]) * 255)
                    lut_data[pixels * 4 + 1] = int(float(nums[1]) * 255)
                    lut_data[pixels * 4 + 2] = int(float(nums[2]) * 255)
                    lut_data[pixels * 4 + 3] = int(255)
                    pixels += 1
    return lut_size, lut_data


def write_png(fileName, lutSize, lutData):
    with open(fileName, 'wb') as aFile:
        png_writer = png.Writer(lutSize * lutSize, lutSize, greyscale=False, alpha=True)
        png_writer.write_array(aFile, lutData)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("cubeFile", type=str, help="Input cube file")
    args = parser.parse_args()

    if os.path.isfile(args.cubeFile) and os.path.exists(args.cubeFile):
        outputFileName = str(args.cubeFile)
        if outputFileName.upper().endswith('.CUBE'):
            outputFileName = outputFileName[:-len('.CUBE')]
        outputFileName += '.png'

        lut_size, lut_data = read_cube(args.cubeFile)
        if lut_size > 0 and len(lut_data) == lut_size * lut_size * lut_size * 4:
            write_png(outputFileName, lut_size, lut_data)
            print(f'{outputFileName} saved.')
        else:
            print(f'unrecognized input file "{args.cubeFile}"')
    else:
        print(f'Can\'t find input file "{args.cubeFile}"')
# See PyCharm help at https://www.jetbrains.com/help/pycharm/
