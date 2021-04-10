#!/usr/bin/python3
from cv2 import VideoCapture, imwrite, waitKey, IMWRITE_JPEG_QUALITY
from datetime import datetime
from os import environ, chdir, system
from os import path as p
import logging as log
from json import load
import threading
from time import sleep
import lan_scan
from safe_list import SafeList

class cameraThread(threading.Thread):
    def __init__(self, ip, available):
        threading.Thread.__init__(self)
        self.ip = ip
        self.name = "cam_{}".format(self.ip)
        self.available = available
        if not self.available.contains(self.ip):
            self.available.put(self.ip)
    
    def run(self):
        log.info("Starting thread".format(self.ip))
        user,password,interval,path,servers = parse_json() # Get arguments from JSON
        log.info("Servers: {}".format(servers))
        if len(servers)>0:
            for server in servers:
                if self.ip == server["address"]:
                    if "username" in server:
                        user = server["username"]
                    if "password" in server:
                        password = server["password"]
                    break
        server = "rtsp://{}:{}@{}".format(user,password,self.ip)
        log.info("Got server {}".format(server))
        interval = interval*1000 # Convert interval in seconds to milliseconds
        path = p.expandvars(path) # In case of environment variables
        if not p.isdir(path):
            system("mkdir -p {}".format(path))
        chdir(path)
        
        log.info("Connecting to {}".format(server))
        vid = VideoCapture(server)
        while True:
            # Read frame
            ret,frame = vid.read()
            if not ret:
                # Something wrong with video stream
                # Check if `self.ip` is reachable
                if lan_scan.scan(self.ip):
                    vid = VideoCapture(server)
                    log.error("Bad frame. Restarted capture.".format(self.ip))
                    continue
                else:
                    log.error("Server went offline. Closing capture.")
                    self.available.take(self.ip)
                    return

            # Build file name
            t = datetime.now()
            path = "{}/{}/{}".format(t.year,t.month,t.day)
            if not p.isdir(path):
                system("mkdir -p {}".format(path))
            fname = "{}/{}_{}.{}.{}.jpg".format(path,self.ip,t.hour,t.minute,t.second)
            # Write frame
            self.write_frame(frame,fname)
            frame_h,frame_w,_ = frame.shape
            log.debug("Wrote {}x{} (50%) frame to {}".format(frame_w,frame_h,fname))
            # Wait `interval` milliseconds
            waitKey(interval)
        log.info("Exiting thread".format(self.ip))

    # Write `frame` as a JPG image
    def write_frame(self,frame,fname,compression=50):
        imwrite(fname, frame, [IMWRITE_JPEG_QUALITY, compression])

# Initializes logging
# Logs are written to `$CWD/camera_service.log`
def set_logging():
    logFormatter = log.Formatter("[%(asctime)s] %(threadName)s - %(message)s")
    rootLogger = log.getLogger()
    t = datetime.now()
    t_string = "{}-{}-{}_{}:{}:{}".format(t.year,t.month,t.day,t.hour,t.minute,t.second)
    fileHandler = log.FileHandler("camera_service_{}.log".format(t_string))
    fileHandler.setFormatter(logFormatter)
    rootLogger.addHandler(fileHandler)
    rootLogger.setLevel(log.INFO)

def parse_json(fname="./config.json"):
    f = open(fname)
    j = load(f)
    ret = []
    for k in j:
        log.debug("Read parameter '{}:{}'".format(k,j[k]))
        ret.append(j[k])
    f.close()
    return ret

def scan(available):
    log.info("Scanning...")
    ret = lan_scan.lan_scan()
    log.info("Available: {}".format(ret))
    log.info("var available: {}".format(available.snapshot()))
    for ip in ret:
        if not available.contains(ip):
            available.put(ip)
            cam = cameraThread(ip,available)
            cam.start()

# Main function
def main():
    set_logging()
    log.info("Service starting...")
    scan_cooldown = 30*60 # 30 minutes
    available = SafeList() # list of IP addresses
    _,_,_,_,servers = parse_json()
    for server in servers:
        ip = server["address"]
        log.info("Starting server {} from config.json...".format(ip))
        cam = cameraThread(ip,available)
        cam.start()
    while True:
        scan(available)
        sleep(scan_cooldown)

if __name__ == "__main__":
    main()
