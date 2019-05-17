import sys
import random
import argparse

import redis


KEY_LEN = 10
ID_LEN = 32
FILL_LEN = 48


def get_args():
    parser = argparse.ArgumentParser(
        description='Generate and store teragen rows into redis'
    )

    parser.add_argument(
        'nrows',
        type=int,
        help='Number of key-value pairs to generate'
    )

    parser.add_argument(
        '--host',
        type=str,
        default='localhost',
        help='Hostname or IP address of redis server'
    )

    parser.add_argument(
        '--port',
        type=int,
        default=6379,
        help='Port of redis server'
    )

    return parser.parse_args()


def gen_key():
    ret = b''
    for i in range(KEY_LEN):
        # ascii chars from ' ' to '~'
        ret += str.encode(chr(random.randint(32, 126)))

    return ret


def gen_rowid(row):
    return str.encode('{row_id: >{width}}'.format(row_id=row, width=ID_LEN, fill=' '))


def gen_filler():
    ret = b''
    for i in range(FILL_LEN):
        # ascii chars from 'A' to 'Z'
        ret += str.encode(chr(random.randint(65, 90)))

    return ret


def gen_row(i):
    return gen_key() + b'\x00\x11' + \
           gen_rowid(i) + b'\x88\x99\xaa\xbb' + \
           gen_filler() + b'\xcc\xdd\xee\xff'


def gen_rows(args, r):
    for i in range(args.nrows):
        if i % 1000 == 0:
            print(i)

        row = gen_row(i)
        r.set(i, row)


def main():
    args = get_args()

    r = redis.Redis(
        host=args.host,
        port=args.port
    )

    # drop all keys from the db
    r.flushall()

    gen_rows(args, r)


if __name__ == '__main__':
    main()
