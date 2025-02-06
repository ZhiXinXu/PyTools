import argparse
import os.path
import sys
import png

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
                # print(f"lut size = {local_lut_size}")
                continue

            if pixels < 0 and aLine.upper().startswith('#LUT DATA POINTS'):
                pixels = 0
                continue

            if pixels < 0 <= local_lut_size:
                # print(f"for line:{aLine}")
                tmp = aLine.split()
                # print(tmp)
                if len(tmp) == 3 and is_float(tmp[0]) and is_float(tmp[1]) and is_float(tmp[2]):
                    pixels = 0
                    # print(f"set pixels = 0 by line: {aLine}")
                else:
                    continue

            if pixels >= 0:
                nums = aLine.split()
                if len(nums) == 3:
                    for n in nums:
                        fn = float(n)
                        if fn < 0.0 or fn > 1.0:
                            raise ValueError(f'value must be in range(0,1.0), value = "{fn}"')

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


def convert_cube(file_name):
    output_file_name = file_name
    if output_file_name.upper().endswith('.CUBE'):
        output_file_name = output_file_name[:-len('.CUBE')]
    output_file_name += '.png'
    try:
        local_lut_size, local_lut_data = read_cube(file_name)
        if local_lut_size > 0 and len(local_lut_data) == local_lut_size * local_lut_size * local_lut_size * 4:
            write_png(output_file_name, local_lut_size, local_lut_data)
            print(f'{output_file_name} saved.')
        else:
            print(f'unrecognized input file "{file_name}"')
    except ValueError as e:
        print("\033[31m" + f'convert "{file_name}" failed: {e}' + "\033[0m")

def convert_cube_in_dir(dir_name):
    for name in os.listdir(dir_name):
        full_path_name = os.path.join(dir_name, name)
        if os.path.isfile(full_path_name) and full_path_name.upper().endswith('.CUBE'):
            convert_cube(full_path_name)
        elif os.path.isdir(full_path_name):
            convert_cube_in_dir(full_path_name)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("cubeFile", type=str, help="Input cube file")
    args = parser.parse_args()

    if not os.path.exists(args.cubeFile):
        print(f'Invalid input : "{args.cubeFile}"')
        sys.exit()

    if os.path.isfile(args.cubeFile):
        convert_cube(args.cubeFile)
    elif os.path.isdir(args.cubeFile):
        convert_cube_in_dir(args.cubeFile)
    else:
        print(f'Can\'t find input file "{args.cubeFile}"')
# See PyCharm help at https://www.jetbrains.com/help/pycharm/
