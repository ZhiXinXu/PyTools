import argparse
import os.path
import png


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press ⌘F8 to toggle the breakpoint.


def is_float(s):
    return s.replace('.', '', 1).isdigit()


def read_cube(fileName):
    local_lut_size = -1
    local_lut_data = bytearray()
    pixels = -1

    with open(fileName) as aFile:
        for aLine in aFile:
            if local_lut_size < 0 and aLine.upper().startswith('LUT_3D_SIZE'):
                a = aLine.split()
                local_lut_size = int(a[1])
                local_lut_data = bytearray(local_lut_size * local_lut_size * local_lut_size * 4)
                print(f"lut size = {local_lut_size}")
                continue

            if pixels < 0 and aLine.upper().startswith('#LUT DATA POINTS'):
                pixels = 0
                continue

            if pixels < 0 and local_lut_size >= 0:
                print(f"for line:{aLine}")
                tmp = aLine.split()
                print(tmp)
                if len(tmp) == 3 and is_float(tmp[0]) and is_float(tmp[1]) and is_float(tmp[2]):
                    pixels = 0
                    print(f"set pixels = 0 by line: {aLine}")
                else:
                    continue

            if pixels >= 0:
                nums = aLine.split()
                if len(nums) == 3:
                    # print(nums)
                    local_lut_data[pixels * 4] = int(float(nums[0]) * 255)
                    local_lut_data[pixels * 4 + 1] = int(float(nums[1]) * 255)
                    local_lut_data[pixels * 4 + 2] = int(float(nums[2]) * 255)
                    local_lut_data[pixels * 4 + 3] = int(255)
                    pixels += 1
    return local_lut_size, local_lut_data


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
