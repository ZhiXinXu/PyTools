import argparse
import io
import os

# 00:00:35,720
def timestamp_to_ms(timestamp):
    tokens = timestamp.split(':')
    hours = int(tokens[0])
    minutes = int(tokens[1])
    tmp = tokens[2].split(',')
    seconds = int(tmp[0])
    million_secs = int(tmp[1])
    return million_secs + seconds * 1000 + minutes * 60 * 1000 + hours * 60 * 1000 * 1000


def ms_to_timestamp(duration):
    hours = int(duration / (60 * 1000 * 1000))
    remain = duration % (60 * 1000 * 1000)
    minutes = int(remain / (60 * 1000))
    remain = remain % (60 * 1000)
    seconds = int(remain / 1000)
    million_secs = int(remain % 1000)
    return "{:0>2d}:{:0>2d}:{:0>2d},{:0>3d}".format(hours, minutes, seconds, million_secs)



def load_file(fileName):
    with open(fileName, 'r', encoding="utf-8") as input_file:
        data = {}
        index = 0
        for line in input_file:
            a = line.replace(u'\ufeff', '').strip()
            if len(a) == 0:
                if index in data:
                    index += 1
                continue
            if index in data:
                data[index].append(a)
            else:
                x = a.split()
                if x[0].isdigit():
                    i = int(x[0])
                    if i >= index:
                        index = i
                        if len(x) == 1:
                            data[i] = []
                        else:
                            data[i] = [' '.join(x[1:])]
        return data


def shift_time(delta, data):
    for key in data.keys():
        tokens = data[key][0].split()
        ms0 = timestamp_to_ms(tokens[0])
        ms1 = timestamp_to_ms(tokens[2])
        ms0 += delta
        ms1 += delta
        tokens[0] = ms_to_timestamp(ms0)
        tokens[2] = ms_to_timestamp(ms1)
        data[key][0] = ' '.join(tokens)


def save_file(output_file, data):
    with open(output_file, "w", encoding="utf-8") as out_file:
        for (key,value) in data.items():
            out_file.write("{}\n".format(key))
            for s in value:
                out_file.write("{}\n".format(s))
            out_file.write("\n")
    print("{} saved.", output_file)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("srt_file", type=str, help=".srt file")
    parser.add_argument("-s", "--shift", type=int, help="time shift in ms")
    parser.add_argument("-o", "--output", type=str, help="output file name")
    args = parser.parse_args()
    result = load_file(args.srt_file)
    if args.shift:
        if args.output:
            shift_time(args.shift, result)
            save_file(args.output, result)
        else:
            print("You must specify the output file name, use -h for usage")
    else:
        print(result)

