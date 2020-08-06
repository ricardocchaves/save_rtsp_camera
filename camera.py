#!/usr/bin/python3
from cv2 import VideoCapture, imwrite, waitKey, IMWRITE_JPEG_QUALITY
from datetime import datetime
from os import environ, chdir, system
from os import path as p
import logging as log
from json import load

# Initializes logging
# Logs are written to `$CWD/camera_service.log`
def set_logging():
    logFormatter = log.Formatter("[%(asctime)s] %(message)s")
    rootLogger = log.getLogger()
    fileHandler = log.FileHandler("camera_service.log")
    fileHandler.setFormatter(logFormatter)
    rootLogger.addHandler(fileHandler)
    rootLogger.setLevel(log.DEBUG)

# Writes `frame` as a JPG image
def write_frame(frame,fname,compression=50):
    imwrite(fname, frame, [IMWRITE_JPEG_QUALITY, compression])

def parse_json(fname="./config.json"):
    f = open(fname)
    j = load(f)
    ret = []
    for k in j:
        log.debug("Read parameter '{}:{}'".format(k,j[k]))
        ret.append(j[k])
    return ret

# Main function
def main():
    set_logging()
    # Get arguments from JSON
    user,password,interval,path = parse_json()
    server = "rtsp://{}:{}@10.0.0.2".format(user,password)
    interval = interval*1000 # Convert interval in seconds to milliseconds
    log.debug("Service starting...")
    log.debug("Server: {}".format(server))
    path = p.expandvars(path) # In case of environment variables
    chdir(path)
    log.debug("Changed current path to {}".format(path))

    vid = VideoCapture(server)
    while True:
        # Read frame
        ret,frame = vid.read()
        if not ret:
            # Something wrong with video stream, restarting capture
            vid = VideoCapture(server)
            log.error("Bad frame. Restarted capture.")
            continue
        # Build file name
        t = datetime.now()
        path = "{}/{}/{}".format(t.year,t.month,t.day)
        if not p.isdir(path):
            system("mkdir -p {}".format(path))
        fname = "{}/{}:{}:{}.jpg".format(path,t.hour,t.minute,t.second)
        
        # Write frame
        write_frame(frame,fname)
        frame_h,frame_w,_ = frame.shape
        log.debug("Wrote {}x{} (50%) frame to {}".format(frame_w,frame_h,fname))
        # Wait `interval` milliseconds
        waitKey(interval)

if __name__ == "__main__":
    main()
