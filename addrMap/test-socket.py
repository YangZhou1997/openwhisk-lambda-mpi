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
    return ["10.0.0.157"]
    ips = []
    for file in os.listdir("/addrMap"):
        if file.endswith(".ipaddr"):
            f = open("/addrMap/" + file, 'r')
            ips.append(f.readline())
            f.close()
    ips.remove(hostip)
    return ips


def main(args):
    hostname = get_hostname()
    hostip = get_hostip(hostname)
    print(hostname, hostip)

    echo_ip(hostname, hostip)
    time.sleep(1)
    ips = get_peerips(hostip)
    print(ips)

    data = None
    socket_type = int(args.get("client"))
    if socket_type == 1: # client
        print("client: ")
        for peerip in ips:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(10)
            s.connect((peerip, PORT))
            s.sendall(b'Hello, world')
            data = s.recv(1024)
            print(data)
            s.close()
    else: # server
        print("server: ")
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((hostip, PORT))
        s.listen()
        conn, addr = s.accept()
        print('Connected by', addr)
        while True:
            data = conn.recv(1024)
            print(data)
            if not data:
                conn.close()
                break
            conn.sendall(data)

    hide_ip(hostname)
    return {"res": data}

# python test-socket.py 1 -> test client
# python test-socket.py 0 -> test server
# must be removed when creating action in wsk
print(main({"client": sys.argv[1]}))

