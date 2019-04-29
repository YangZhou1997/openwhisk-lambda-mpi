#!/usr/bin/python3
import terasort as ts
from threading import Thread

CHUNCK_SIZE_PER_MAPPER = 1024 * 1024
NUM_THREAD = 18

def dataGen(thread_id):
    mapper_range = ts.NUM_MAPPER // NUM_THREAD
    for i in range(thread_id * mapper_range, thread_id * mapper_range + mapper_range):
        filename = "/users/yangzhou/openwhisk/addrMap/teradata/__random_bytes_" + str(ts.LEN_BYTES) + "_" + str(i) + ".dat"
        f = open(filename, 'wb')
        for j in range(CHUNCK_SIZE_PER_MAPPER):
            f.write(ts.getRandomBytes(ts.LEN_BYTES))
        f.close()

if __name__ == "__main__":
    for i in range(NUM_THREAD):
        p = Thread(target = dataGen, args=(i,))
        p.start()


