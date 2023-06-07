import json
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=str, help="utf-8 file")
    args = parser.parse_args()

    table = []
    with open(args.input, 'r') as f:
        for line in f:
            fields = line.rstrip().split('\t')
            #
            # record = {'school_id': fields[0],
            #          'school_name': fields[1],
            #          'major_id': fields[2],
            #          'major_name': fields[3],
            #          'lowest_count': int(fields[4])}
            #
            record = {'score': int(fields[0]),
                      'count' : int(fields[1])}
            table.append(record)

    result = json.dumps(table, indent=2)
    print(result)
