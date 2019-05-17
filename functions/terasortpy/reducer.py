import socket
import select
from bisect import insort

import redis


# key for sorted insertion is: instanceID_rowidx
def write_rows(r, rows, iid):
    for i, row in enumerate(rows):
        r.set(iid + '_' + str(i), row)


# listen on all mapper sockets for new rows
# when a row is received, use insort to insert into list in a sorted manner
def listen_mappers(mappers):
    # sockets for all mappers
    socks = [m['socket'] for m in mappers]

    rows = []

    while True:
        # mappers will send a 'done' message which tells this loop to remove
        # that socket from the socks list
        if len(socks) == 0:
            break

        # blocks until a socket is ready
        ready_socks, _, _ = select.select(socks, [], [])
        for sock in ready_socks:
            data, addr = sock.recvfrom(1024)
            if data == b'done':
                socks.remove(sock)
            else:
                # TODO: check integrity of row
                insort(rows, data)

    # this is a sorted list of rows
    return rows


# find all mappers and open sockets with them
def get_mappers(nmappers):
    pass


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

    nmappers = args.get('nmappers')
    if not nmappers:
        return {
            'err': 'No nmappers specified'
        }
    nmappers = int(nmappers)

    iid = args.get('iid')
    if not iid:
        return {
            'err': 'No iid specified'
        }

    r = redis.Redis(
        host=host,
        port=port
    )

    mappers = get_mappers()
    rows = listen_mappers(mappers)
    write_rows(r, rows, iid)


if __name__ == '__main__':
    print(main({}))
