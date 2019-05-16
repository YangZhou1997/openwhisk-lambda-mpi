import socket
import os
import time
import sys
from builtins import bytes
import random
import string
import struct
import redis

def main(args):

    dataSize = int(args.get("dataSize")) # 64 B
    sendNum = int(args.get("sendNum")) # 100

    socket_type = args.get("instanceID")
    if socket_type == "myname1": # client
        time.sleep(1)

        data = None

        base_sending_data = ''.join([random.choice(string.ascii_letters + string.digits + string.punctuation) for _ in range(64)])

        sending_data = ""
        for i in range(0, dataSize // 64):
            sending_data += base_sending_data
        sending_data = bytes(sending_data, encoding = "utf8")

        print("client: ")
        time1 = time.time()

        r = redis.Redis(host='10.10.1.2', port=7001, db=0)
        for i in range(sendNum):
            res1 = r.set('foo' + str(i * 2 + 1), sending_data)
            res2 = r.get('bar' + str(i * 2 + 1))
            while( res2 == None):
                time.sleep(0.1)
                res2 = r.get('bar' + str(i * 2 + 1))

        time2 = time.time()
        return {"res": time2 - time1}

    else: # server
        print("server: ")

        r = redis.Redis(host='10.10.1.2', port=7001, db=0)
        r.flushall()
        for i in range(sendNum):
            res1 = r.get('foo' + str(i * 2 + 1))
            while(res1 == None):
                time.sleep(0.1)
                res1 = r.get('foo' + str(i * 2 + 1))

            r.set('bar' + str(i * 2 + 1), res1)

        return {"res": 0}


# python test-socket.py 1 -> test client
# python test-socket.py 1 -> test server
# must be removed when creating action in wsk
# print(main({"client": sys.argv[1]}))

