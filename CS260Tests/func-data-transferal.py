import socket
import os
import time
import sys
from builtins import bytes
import random
import string
import struct

PORT = 65432

def get_peerips():

    f = open("/addrMap/addrMap.txt", 'r')
    idipStr = f.readline().strip('\n')
    f.close()


    idipPairs = idipStr.split("&")
    idipMap = dict()
    for idip in idipPairs:
        temp = idip.split("=")
        idipMap[temp[0]] = temp[1]
    print(idipMap)
    return idipMap

def send_msg(sock, msg):
    # Prefix each message with a 4-byte length (network byte order)
    msg = struct.pack('>I', len(msg)) + msg
    sock.sendall(msg)

def recv_msg(sock):
    # Read message length and unpack it into an integer
    raw_msglen = recvall(sock, 4)
    if not raw_msglen:
        return None
    msglen = struct.unpack('>I', raw_msglen)[0]
    # Read the message data
    return recvall(sock, msglen)

def recvall(sock, n):
    # Helper function to recv n bytes or return None if EOF is hit
    data = b''
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data += packet
    return data

def main(args):
    time.sleep(3)

    dataSize = int(args.get("dataSize")) # 64 B
    sendNum = int(args.get("sendNum")) # 100

    selfid = args.get("instanceID") # myname0 or myname1: String
    if selfid == "myname0":
        peerid = "myname1"
    else:
        peerid = "myname0"


    idipMap = get_peerips()
    peerip = idipMap[peerid]
    selfip = idipMap[selfid]

    socket_type = selfid
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
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((peerip, PORT))
        for i in range(sendNum):
            send_msg(s, sending_data)
            data = recv_msg(s)
        time2 = time.time()
        s.close()
        return {"res": time2 - time1}

    else: # server
        print("server: ")
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((selfip, PORT))
        s.listen()
        conn, addr = s.accept()
        print('Connected by', addr)
        while True:
            data = recv_msg(conn)
            # print(data)
            if not data:
                conn.close()
                break
            send_msg(conn, data)
        return {"res": 0}


# python test-socket.py 1 -> test client
# python test-socket.py 1 -> test server
# must be removed when creating action in wsk
# print(main({"client": sys.argv[1]}))

