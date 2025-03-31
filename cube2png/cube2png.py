import argparse
import os.path
import sys
import png
import json
import uuid

# Global variables
icons_map = []

def sort_icons_map(val):
    return val["name"]


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


def write_as_json(object, file_name, sort_keys=False):
    with open(file_name, 'w') as jsonFile:
        json_object = json.dumps(object, indent=2, sort_keys=sort_keys)
        jsonFile.write(json_object)


def write_files(file_name, categoryName):
    dir_name = os.path.dirname(file_name)
    name, ext = os.path.splitext(os.path.basename(file_name))
    lut_dir = os.path.join(dir_name, "lut")
    os.makedirs(lut_dir, exist_ok=True)

    json_file_name = os.path.join(lut_dir, categoryName + "_" + name + ".json")
    lut_uuid = (str(uuid.uuid4())).upper()
    lut = {"id": lut_uuid,
                  "path": "cubes/" + categoryName + "/" + name + ".png"
                  }
    write_as_json(lut, json_file_name)

    filter_dir = os.path.join(dir_name, "filter")
    os.makedirs(filter_dir, exist_ok=True)
    filter_uuid = (str(uuid.uuid4())).upper()
    filter = {
        "version": "1.0.0",
        "id": filter_uuid,
        "lut": lut_uuid,
        "name": {
            "en": name,
            "zh-Hans": name
        },
        "builtin": True,
        "paid": True,
        "intensity": 1.0,
        "grain-amount": 0.32,
        "grain-highlights": 0.25,
        "grain-size": 0.45,
        "grain-roughness": 0.55
    }
    filter_file_name = os.path.join(filter_dir, categoryName + "_" + name + ".json")
    write_as_json(filter, filter_file_name)

    icons_map.append({ "id": filter_uuid, "icon": "icons/" + name + ".png", "name": name })


def convert_cube(file_name, category_name):
    dir_name = os.path.dirname(file_name)
    name, ext = os.path.splitext(os.path.basename(file_name))
    if ext.upper() == '.CUBE':
        cube_dir = os.path.join(os.path.join(dir_name, "cubes"),category_name)
        os.makedirs(cube_dir, exist_ok=True)
        output_file_name = os.path.join(cube_dir, name + ".png")

        try:
            local_lut_size, local_lut_data = read_cube(file_name)
            if local_lut_size > 0 and len(local_lut_data) == local_lut_size * local_lut_size * local_lut_size * 4:
                write_png(output_file_name, local_lut_size, local_lut_data)
                write_files(file_name, category_name)
                print(f'{output_file_name} saved.')
            else:
                print(f'unrecognized input file "{file_name}"')
        except ValueError as e:
            print("\033[31m" + f'convert "{file_name}" failed: {e}' + "\033[0m")


def convert_cube_in_dir(dir_name, category_name):
    for name in os.listdir(dir_name):
        full_path_name = os.path.join(dir_name, name)
        if os.path.isfile(full_path_name) and full_path_name.upper().endswith('.CUBE'):
            convert_cube(full_path_name, category_name)

    icons_dir = os.path.join(dir_name, "icons")
    os.makedirs(icons_dir, exist_ok=True)
    icons_json_file_name = os.path.join(icons_dir, "filters_icons.json")
    icons_map.sort(key=sort_icons_map)
    write_as_json(icons_map, icons_json_file_name)

    categories_dir = os.path.join(dir_name, "categories")
    os.makedirs(categories_dir, exist_ok=True)
    categories_json_file_name = os.path.join(categories_dir, category_name + ".json")
    categories_uuid = (str(uuid.uuid4())).upper()

    filters_list = []
    for item in icons_map:
        filters_list.append(item["id"])

    categories_object = {
        "version": "1.0.0",
        "id": categories_uuid,
        "name": {
            "en": category_name,
            "zh-Hans": category_name,
            "zh-Hant": "",
            "ja": "",
            "pt": "",
            "es": "",
            "fr": "",
            "de": "",
            "nl": "",
            "it": "",
            "ru": "",
            "tr": "",
            "ar": "",
            "cy": "",
            "ko": "",
            "th": "",
            "id": ""
        },
        "filters":filters_list
    }

    write_as_json(categories_object, categories_json_file_name)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("cubeFile", type=str, help="Input cube file")
    parser.add_argument("categoryName", type=str, help="Input categoryName", default="XXX-XXX")
    args = parser.parse_args()

    if not os.path.exists(args.cubeFile):
        print(f'Invalid input : "{args.cubeFile}"')
        sys.exit()

    if os.path.isfile(args.cubeFile):
        convert_cube(args.cubeFile, args.categoryName)
    elif os.path.isdir(args.cubeFile):
        convert_cube_in_dir(args.cubeFile, args.categoryName)
    else:
        print(f'Can\'t find input file "{args.cubeFile}"')
# See PyCharm help at https://www.jetbrains.com/help/pycharm/
