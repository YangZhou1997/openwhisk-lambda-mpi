import socket
import os
import time
import sys

PORT = 65432

def get_hostname():
    return socket.gethostname()

def get_hostip(hostname):
    return socket.gethostbyname(hostname)

def main(args):
    data = None
    socket_type = args.get("client")
    if socket_type == "1": # client
        serverip = "172.17.0.14"
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(10)
        s.connect((serverip, PORT))
        s.sendall(b'Hello, world')
        data = s.recv(1024)
        s.close()
    else: # server
        hostip = get_hostip(socket.gethostname())
        print(hostip)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((hostip, PORT))
        s.listen()
        conn, addr = s.accept()
        print('Connected by', addr)
        while True:
            data = conn.recv(1024)
            if not data:
                conn.close()
                break
            conn.sendall(data)

    return {"res": data}

# python test-socket.py 1 -> test client
# python test-socket.py 1 -> test server
# must be removed when creating action in wsk
print(main({"client": sys.argv[1]}))

