#!/usr/bin/python3
import random
import string

if __name__ == "__main__":
    sampleKeys = []
    f_sample = open("/users/yangzhou/openwhisk/addrMap/teradata/cutpoints.dat", 'wb')
    for i in range(0, 1800):
        f = open("/users/yangzhou/openwhisk/addrMap/teradata/src_data/__random_bytes_32M_" + str(i) + ".dat", 'rb')
        bytes_all = f.read()
        for j in range(0, 100):
            sample_index = random.randint(0, 1024 * 1024 - 1)
            samplebytes = bytes_all[sample_index * 32: sample_index * 32 + 32]
            #print(len(samplebytes))
            sampleKeys.append(samplebytes)
    sampleKeys.sort()
    for i in range(0, 1800 - 1):
        f_sample.write(sampleKeys[i * 100 + 100])
    f_sample.close()
