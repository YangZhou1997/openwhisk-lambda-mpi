#!/usr/bin/python3
import random
import string
import os

if __name__ == "__main__":
    last_bytes = b''
    for i in range(0, 1800):
        filename = "/addrMap/teradata/dst_data/__random_bytes_32M_" + str(i) + ".dat"
        if not os.path.exists(filename):
            continue
        f = open(filename, 'rb')
        bytes_all = f.read()
        for j in range(0, len(bytes_all) // 32):
            cur_bytes = bytes_all[j * 32: j * 32 + 32]
            # print(last_bytes, cur_bytes)
            assert last_bytes <= cur_bytes
            last_bytes = cur_bytes
        print("check successfully for " + str(i))
        f.close()
