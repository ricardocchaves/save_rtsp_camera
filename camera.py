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
    
    def run(self):
        log.debug("Starting thread".format(self.ip))
        user,password,interval,path = parse_json() # Get arguments from JSON
        server = "rtsp://{}:{}@{}".format(user,password,self.ip)
        interval = interval*1000 # Convert interval in seconds to milliseconds
        path = p.expandvars(path) # In case of environment variables
        chdir(path)
        
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
            fname = "{}/{}_{}:{}:{}.jpg".format(path,self.ip,t.hour,t.minute,t.second)
            # Write frame
            self.write_frame(frame,fname)
            frame_h,frame_w,_ = frame.shape
            log.debug("Wrote {}x{} (50%) frame to {}".format(frame_w,frame_h,fname))
            # Wait `interval` milliseconds
            waitKey(interval)
        log.debug("Exiting thread".format(self.ip))

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
    rootLogger.setLevel(log.DEBUG)

def parse_json(fname="./config.json"):
    f = open(fname)
    j = load(f)
    ret = []
    for k in j:
        log.debug("Read parameter '{}:{}'".format(k,j[k]))
        ret.append(j[k])
    return ret

def scan(available):
    log.debug("Scanning...")
    ret = lan_scan.lan_scan()
    log.debug("Available: {}".format(ret))
    for ip in ret:
        if not available.contains(ip):
            available.put(ip)
            cam = cameraThread(ip,available)
            cam.start()

# Main function
def main():
    set_logging()
    log.debug("Service starting...")
    scan_cooldown = 30*60 # 30 minutes
    available = SafeList() # list of IP addresses
    while True:
        scan(available)
        sleep(scan_cooldown)

if __name__ == "__main__":
    main()
