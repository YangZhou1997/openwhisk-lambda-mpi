#!/usr/bin/python3
import random
import string
import socket
import os
import time
import sys

PORT = 65432

def get_hostname():
    return socket.gethostname()

def get_hostip(hostname):
    return socket.gethostbyname(hostname)

def echo_ip(hostname, ip):
    # os.system("echo " + ip + " > /addrMap/" + str(hostname) + ".ipaddr")
    f = open("/addrMap/" + str(hostname) + ".ipaddr", 'w')
    f.write(str(ip))
    f.close()

def hide_ip(hostname):
    os.remove("/addrMap/" + str(hostname) + ".ipaddr")

def get_peerips(hostip):
    ips = []
    for file in os.listdir("/addrMap"):
        if file.endswith(".ipaddr"):
            f = open("/addrMap/" + file, 'r')
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

def server_listen_on(hostip)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((hostip, PORT))
    s.listen()
    conn, addr = s.accept()
    return (conn, addr)


NUM_MAPPER = 1800
NUM_REDUCER = 1800

LEN_BYTES = 32

def getPrefixVal(key):
    return (key[0] * 256 + key[1])

# splitPoints array: ascending order, string array
def buildLowerBound(splitPoints):
    lowerBoundArray = [None] * 65536
    upperBoundArray = [None] * 65536

    currentBound = 0
    lower = 0
    upper = len(splitPoints)
    for i in range(0, 65536):
        lower = currentBound
        while currentBound < upper:
            if getPrefixVal(splitPoints[currentBound]) >= i + 1:
                break;
            currentBound += 1
        lowerBoundArray[i] = lower
        upperBoundArray[i] = currentBound

    return (lowerBoundArray, upperBoundArray);

# lowerBoundArray and upperBoundArray: [Int] * 65536, each element belongs to 0, ..., len(splitPoints)
def getPartition(splitPoints, lowerBoundArray, upperBoundArray, key):
    prefixVal = getPrefixVal(key)
    lower = lowerBoundArray[prefixVal]
    upper = upperBoundArray[prefixVal]
    for i in range(lower, upper):
        if splitPoints[i] > key:
            return i
    return upper

def getRandomBytes(length):
    return bytes(random.randint(0, 255) for _ in range(length))

# source data: /addrMap/teradata/__random_bytes_32_${mapper_id}.dat
# dest data: /addrMap/terares/__random_bytes_32_${reducer_id}.dat

# after all mappers' computation ends, reducers begin to work
def main(args):

    return

if __name__ == "__main__":
    splitPoints = []
    for i in range(NUM_REDUCER - 1):
        splitPoints.append(getRandomBytes(LEN_BYTES))

    splitPoints.sort()
    #print(splitPoints)

    (lowerBoundArray, upperBoundArray) = buildLowerBound(splitPoints)
    #print(lowerBoundArray)
    #print(upperBoundArray)
