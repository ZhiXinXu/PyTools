import getopt
import os
import sys


def wc_on_file(filename, skip_empty_lines):
    _local_count = 0
    with open(filename, 'r') as f:
        for _line in f:
            if skip_empty_lines:
                if _line.strip() != '':
                    _local_count += 1
            else:
                _local_count += 1

    return _local_count


def wc_on_dir(path, skip_empty_lines):
    _local_result = {}
    for root, sub_dirs, files in os.walk(path):
        for _file in files:
            _name, _ext = os.path.splitext(_file)
            if _ext in ['.h', '.hpp', '.c', '.cpp', '.m', '.mm']:
                _filename = os.path.join(root, _file)
                _local_result[_filename] = wc_on_file(_filename, skip_empty_lines)
    return _local_result


def main():
    _dir = '.'
    if len(sys.argv) > 1:
        try:
            opts, args = getopt.getopt(sys.argv[1:], 'd:', [])
        except getopt.GetoptError:
            print('pywc.py [<-d> <target dir for wc>]')
            sys.exit(1)

        for opt, arg in opts:
            if opt == '-d':
                _dir = arg

    if not os.path.isabs(_dir):
        _dir = os.path.normpath(os.path.join(os.getcwd(), _dir))

    if not os.path.isdir(_dir):
        print('Invalid dir : "' + _dir + '"')
        exit(2)

    print('_dir = ' + _dir)
    _result = wc_on_dir(_dir, False)

    _count = 0
    for k, v in _result.items():
        print(os.path.relpath(k, _dir) + ' : ' + str(v))
        _count += v

    print('Total files : ' + str(len(_result)) + ', total lines : ' + str(_count))


if __name__ == '__main__':
    main()
