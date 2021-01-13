import argparse
import os
from itertools import cycle


# Print iterations progress
def print_progress_bar(iteration, total, prefix='Progress', suffix='Complete', decimals=1, length=100, fill='█', print_end="\r"):
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filled_length = int(length * iteration // total)
    bar = fill * filled_length + '-' * (length - filled_length)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end=print_end)
    if iteration == total:
        print()


def _xor(src_file, dst_file, key):
    buffer_size = 4096
    key_length = len(key)
    key_index = 0
    file_size = os.stat(src_file).st_size
    offset = 0

    with open(src_file, 'rb') as in_file, open(dst_file, 'wb') as out_file:
        print_progress_bar(offset, file_size, length=50)
        data = bytearray(in_file.read(buffer_size))
        while len(data) > 0:
            for i in range(len(data)):
                data[i] = data[i] ^ ord(key[key_index])
                key_index = (key_index + 1) % key_length
            out_file.write(data)
            offset += len(data)
            print_progress_bar(offset, file_size, length=50)
            data = bytearray(in_file.read(buffer_size))

    return True


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("srcFile", type=str, help="file to be encrypted")
    parser.add_argument("dstFile", type=str, help="Encrypted file name")
    parser.add_argument("key", type=str, help="Xor encryption key")
    args = parser.parse_args()
    if _xor(args.srcFile, args.dstFile, args.key):
        print('"' + args.dstFile + '" saved.');
    else:
        print("Encryption failed.")
