#!/usr/bin/python3
import random
import string
import socket
import os
import time
import sys
import struct

PORT = 65432

def get_hostname():
    return socket.gethostname()

def get_hostip(hostname):
    return socket.gethostbyname(hostname)

def echo_ip(hostname, ip):
    # os.system("echo " + ip + " > /addrMap/" + str(hostname) + ".ipaddr")
    f = open("/addrMap/addrMap/" + str(hostname) + ".ipaddr", 'w')
    f.write(str(ip))
    f.close()

def hide_ip(hostname):
    os.remove("/addrMap/addrMap/" + str(hostname) + ".ipaddr")

def get_peerips(hostip):
    ips = []
    for file in os.listdir("/addrMap/addrMap"):
        if file.endswith(".ipaddr"):
            f = open("/addrMap/addrMap/" + file, 'r')
            ips.append(f.readline())
            f.close()
    ips.remove(hostip)
    return ips

def client_try_connect(serverip):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(10)
# if server is not on listening, code will crash; needs to fix
    s.connect((serverip, PORT))
    return s

def server_listen_on(hostip):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((hostip, PORT))
    s.listen()
    conn, addr = s.accept()
    return (conn, addr)


MAPPER_NUM = 1800
REDUCER_NUM = 1800

STR_NUM_PER_MAPPER = 1024 * 1024
LEN_BYTES = 32

def getPrefixVal(key):
    return (key[0] * 256 + key[1])

# splitPoints array: ascending order, string array
def buildBound(splitPoints):
    partitionMap = [[] for i in range(0, 65536)]
    num_splitpoints = len(splitPoints)
    for i in range(0, num_splitpoints):
        prefixVal = getPrefixVal(splitPoints[i])
        partitionMap[prefixVal].append(i)
    last_set  = [num_splitpoints]
    for i in reversed(range(65536)):
        if len(partitionMap[i]) == 0:
            partitionMap[i] = last_set
        else:
            last_set = partitionMap[i]
    return partitionMap

# lowerBoundArray and upperBoundArray: [Int] * 65536, each element belongs to 0, ..., len(splitPoints)
def getPartition(splitPoints, partitionMap, key):
    prefixVal = getPrefixVal(key)
    num_splitpoints = len(splitPoints)
    for reducer_id in partitionMap[prefixVal]:
        if reducer_id == num_splitpoints:
            return num_splitpoints
        if key < splitPoints[reducer_id]:
            return reducer_id
    return partitionMap[prefixVal][-1] + 1

def getRandomBytes(length):
    return bytes(random.randint(0, 255) for _ in range(length))

MAPPER_TYPE = 0
REDUCER_TYPE = 1

# source data: /addrMap/teradata/src_data/__random_bytes_32M_${mapper_id}.dat
# intermediate data: /addrMap/teradata/ephe_data/__random_bytes_32M_${reducer_id}.dat
# dest data: /addrMap/teradata/dst_data/__random_bytes_32M_${reducer_id}.dat

# after all mappers' computation ends, reducers begin to work
def main(args):
    global MAPPER_NUM
    global REDUCER_NUM
    mapper_or_reducer = int(args.get("type"))
    work_id = int(args.get("id"))
    # mapper_or_reducer = int(args[0])
    # work_id = int(args[1])

    if mapper_or_reducer == MAPPER_TYPE:
        time1 = time.time()
        selfip = get_hostip(get_hostname())
        echo_ip("mapper_" + str(work_id), selfip)

        time2 = time.time()
        # read splitPoints from file
        splitPoints = []
        f_sample = open("/addrMap/teradata/cutpoints.dat", 'rb')
        for i in range(REDUCER_NUM - 1):
            key = f_sample.read(LEN_BYTES)
            splitPoints.append(key)
        f_sample.close()

        time3 = time.time()
        # build partitionMap
        partitionMap = buildBound(splitPoints)

        time4 = time.time()
        # src data read
        f_src = open("/addrMap/teradata/src_data/__random_bytes_32M_" + str(work_id) + ".dat", 'rb')
        key_array = f_src.read(STR_NUM_PER_MAPPER * LEN_BYTES)
        f_src.close()

        time5 = time.time()
        # mapping each key into its reducer
        reducer_keys = [b'' for i in range(0, REDUCER_NUM)]
        for i in range(STR_NUM_PER_MAPPER):
            key = key_array[i * LEN_BYTES: i * LEN_BYTES + LEN_BYTES]
            reducer_id = getPartition(splitPoints, partitionMap, key)
            reducer_keys[reducer_id] += key
            # if reducer_id == 0:
                # assert key < splitPoints[reducer_id]
            # elif reducer_id == len(splitPoints):
                # assert key >= splitPoints[reducer_id - 1]
            # else:
                # assert key >= splitPoints[reducer_id - 1] and key < splitPoints[reducer_id]

        time6 = time.time()
        # write intermediate data into storage
        f_ephe = open("/addrMap/teradata/ephe_data/__random_bytes_32M_" + str(work_id) + ".dat", 'wb')
        total_size = 0
        for bytesarray in reducer_keys:
            f_ephe.write(struct.pack(">I", total_size))
            print(len(struct.pack(">I", total_size)))
            total_size += len(bytesarray)
        for bytesarray in reducer_keys:
            f_ephe.write(bytesarray)
        f_ephe.close()

        hide_ip("mapper_" + str(work_id))

        time7 = time.time()
        return {"0_ip_echo": (time2 - time1),
                "1_cutpoint_read": (time3 - time2),
                "2_partitionMap_build": (time4 - time3),
                "3_src_data_read": (time5 - time4),
                "4_mapper_exe": (time6 - time5),
                "5_ephe_write": (time7 - time6)}

    elif mapper_or_reducer == REDUCER_TYPE:
        time1 = time.time()
        # gather all mapper's data
        key_array = b''
        for i in range(0, MAPPER_NUM):
            f_ephe = open("/addrMap/teradata/ephe_data/__random_bytes_32M_" + str(i) + ".dat", 'rb')
            f_ephe.seek(work_id * 4, 0)
            offset = struct.unpack(">I", f_ephe.read(4))[0]
            offset_next = struct.unpack(">I", f_ephe.read(4))[0]

            f_ephe.seek(REDUCER_NUM * 4 + offset, 0)
            key_array_size = offset_next - offset
            key_array += f_ephe.read(key_array_size)
            f_ephe.close()

        time2 = time.time()
        # sorting
        sort_keys = []
        for i in range(0, len(key_array) // LEN_BYTES):
            sort_keys.append(key_array[i * LEN_BYTES: i * LEN_BYTES + LEN_BYTES])
        sort_keys.sort()


        time3 = time.time()
        # write results into dst data
        f_dst = open("/addrMap/teradata/dst_data/__random_bytes_32M_" + str(work_id) + ".dat", 'wb')
        for key in sort_keys:
            f_dst.write(key)
        f_dst.close()

        time4 = time.time()
        return {"0_ephe_data_read": (time2 - time1),
                "1_sort_time": (time3 - time2),
                "2_dst_data_write": (time4 - time3)}
    else:
        return {"res": "error"}

# if __name__ == "__main__":
    # print(main((sys.argv[1], sys.argv[2])))
