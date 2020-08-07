#!/usr/bin/python3
import socket
import subprocess
import threading

class scanIP(threading.Thread):
    def __init__(self, ip, l, lock):
        threading.Thread.__init__(self)
        self.name = "scan_thread"
        self.addr = ip
        self.l = l
        self.lock = lock

    def run(self):
        if scan(self.addr):
            self.lock.acquire()
            self.l.append(self.addr)
            self.lock.release()

# Scans local networks for RTSP servers.
# Returns list with available servers, if any.
def lan_scan():
    host = "hostname -I"
    response = subprocess.check_output(host.split())
    response = response.decode('utf-8') # response is in b''
    addresses = response.strip().split() # remove \n and get address(es)

    available = []
    lock = threading.Lock()

    for net in addresses:
        net = net.split('.')
        net = "{}.{}.{}.".format(net[0],net[1],net[2])
        scans = []
        # Start scanning the /24 network
        # TODO: Implement support for any network mask
        for ip in range(1, 255): # range[1,255[
            addr = net + str(ip)
            t = scanIP(addr, available, lock)
            t.start()
            scans.append(t)
        # Wait for scans to finish
        for s in scans:
            s.join()
    return available

def scan(ip_address, port=554):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket.setdefaulttimeout(1)
    result = s.connect_ex((ip_address,port))
    if result == 0:
        return True
    else:
        return False

if __name__ == "__main__":
    from time import time
    t1 = time()
    ret = lan_scan()
    t2 = time()
    print("Time to scan: {}s".format(t2-t1))
    print(ret)
