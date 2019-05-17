import sys
import argparse
import subprocess

import redis


invoke_base = 'wsk -i invoke {fn} -p instanceID {iid}'
invoke_redis = ' -p host {host} -p port {port}'


def get_args():
    parser = argparse.ArgumentParser(
        description='Create mappers and reducers for terasort'
    )

    parser.add_argument(
        'nrows',
        type=int,
        help='Number of key-value pairs to sort'
    )

    parser.add_argument(
        'nmappers',
        type=int,
        help='Number of mappers'
    )

    parser.add_argument(
        'nreducers',
        type=int,
        help='Number of reducers'
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


def start_mappers(args):
    # rows per mapper
    rpm = args.nrows // args.nmappers

    for i in range(args.nmappers):
        cmd = invoke_base + invoke_redis + \
                ' -p rstart {rstart} -p rend {rend} -p nreducers {nreducers}'
        cmd = cmd.format(
            fn='tsmapper',
            iid='mapper' + str(i),
            host=args.host,
            port=args.port,
            rstart=i * rpm,
            rend=(i + 1) * rpm,
            nreducers=args.nreducers

        )

        subprocess.check_output(cmd)


def start_reducers(args):
    for i in range(args.nreducers):
        cmd = invoke_base + invoke_redis + \
                ' -p nmappers {nmappers}'
        cmd = cmd.format(
            fn='tsreducer',
            iid='reducer' + str(i),
            host=args.host,
            port=args.port,
            nmappers=args.nmappers
        )

        subprocess.check_output(cmd)


def main():
    args = get_args()

    if args.nrows < args.nmappers:
        sys.stderr.write(
            'Number of mappers cannot exceed number of rows\n'
        )
        sys.exit(1)

    if args.nrows < args.nreducers:
        sys.stderr.write(
            'Number of reducers cannot exceed number of rows\n'
        )
        sys.exit(1)

    if args.nrows % args.nmappers != 0:
        sys.stderr.write(
            'The number of mappers must evenly divide the number of rows\n'
        )
        sys.exit(1)

    start_mappers(args)
    start_reducers(args)


if __name__ == '__main__':
    main()
