import socket
from bisect import bisect

import redis


# send the row over the socket associated with this reducer along with the
# length of the message (should always be 100 bytes unless sending a 'done'
# message)
def send_row(row, reducer):
    pass


# after all the rows that this mapper processes are gathered, we use the bisect
# module to determine where a particular row would fit into the list of sample
# keys. The index into the sample keys (where there are nreducers - 1 sample
# keys) where a particular row would be inserted into is the reducer number to
# send the row to
def process_rows(sample_keys, rows, reducers):
    for row in rows:
        rkey = row[:10]
        idx = bisect(sample_keys, rkey)
        send_row(row, reducers[idx])


# find all reducers and open sockets with them
def get_reducers(nreducers):
    # placeholder
    return [i for i in range(nreducers)]


# get the rows in the database that this instance processes
def get_rows(r, rstart, rend):
    rows = []

    for i in range(rstart, rend):
        rows.append(r.get(i))

    return rows


# sample keys are the first nreducers - 1 keys in the database
def get_sample_keys(r, nreducers):
    keys = []
    for i in range(nreducers - 1):
        keys.append(r.get(i)[:10])

    return sorted(keys)


def main(args):
    host = args.get('host', None)
    if not host:
        return {
            'err': 'No host specified'
        }

    port = args.get('port')
    if not port:
        return {
            'err': 'No port specified'
        }

    port = int(port)

    nreducers = args.get('nreducers')
    if not nreducers:
        return {
            'err': 'No nreducers specified'
        }

    nreducers = int(nreducers)

    rstart = args.get('rstart')
    if not rstart:
        return {
            'err': 'No rstart specified'
        }

    rstart = int(rstart)

    rend = args.get('rend')
    if not rend:
        return {
            'err': 'No rend specified'
        }

    rend = int(rend)

    r = redis.Redis(
        host=host,
        port=port
    )

    sample_keys = get_sample_keys(r, nreducers)
    rows = get_rows(r, rstart, rend)

    # contact all reducers
    reducers = get_reducers(nreducers)

    process_rows(sample_keys, rows, reducers)


if __name__ == '__main__':
    print(main({}))
