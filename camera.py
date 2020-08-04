#!/usr/bin/python3
from cv2 import VideoCapture, imwrite, waitKey, IMWRITE_JPEG_QUALITY
from datetime import datetime
from os import environ, chdir, system
from os import path as p
import logging as log

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

# Main function
def main():
    set_logging()
    server = "rtsp://admin:admin@10.0.0.17"
    interval = 3*1000 # 3 seconds
    log.debug("Service starting...")
    log.debug("PARAMETER:: Server: {}".format(server))
    log.debug("PARAMETER:: Interval: {}ms".format(interval))
    path = environ["HOME"]+"/SSD/camera_frames/"
    chdir(path)
    log.debug("Changed current path to {}".format(path))

    vid = VideoCapture(server)
    while True:
        # Read frame
        ret,frame = vid.read()
        if not ret:
            # Something wrong with video stream, restarting capture
            vid = VideoCapture(server)
            log.debug("Bad frame. Restarted capture.")
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
