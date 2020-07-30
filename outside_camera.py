#!/usr/bin/python3
from cv2 import VideoCapture, imwrite, waitKey
import datetime
import os
import logging as log

def set_logging():
    logFormatter = log.Formatter("[%(asctime)s] %(message)s")
    rootLogger = log.getLogger()
    fileHandler = log.FileHandler("camera_service.log")
    fileHandler.setFormatter(logFormatter)
    rootLogger.addHandler(fileHandler)
    rootLogger.setLevel(log.DEBUG)

def main():
    set_logging()
    server = "rtsp://admin:admin@10.0.0.17"
    interval = 3*1000 # 3 seconds
    log.debug("Service starting...")
    log.debug("PARAMETER:: Server: {}".format(server))
    log.debug("PARAMETER:: Interval: {}ms".format(interval))
    path = os.environ["HOME"]+"/SSD/camera_frames/"
    os.chdir(path)
    log.debug("Changed current path to {}".format(path))

    vid = VideoCapture(server)
    while True:
        # Read frame
        ret,frame = vid.read()
        # Build file name
        #t = datetime.datetime.now().strftime("%Y-%b-%d_%H:%M:%S")
        t = datetime.datetime.now()
        path = "{}/{}/{}".format(t.year,t.month,t.day)
        os.system("mkdir -p {}".format(path))
        fname = "{}/{}:{}:{}".format(path,t.hour,t.minute,t.second)
        fname_png = fname+".png"
        fname_jpg = fname+".jpg"
        # Write frame
        imwrite(fname_png,frame)
        os.system("convert {} -quality 50% {}".format(fname_png,fname_jpg))
        os.system("rm {}".format(fname_png))
        log.debug("Wrote {}x{} (50%) frame to {}".format(frame.shape[1],frame.shape[0],fname_jpg))
        # Wait `interval` milliseconds
        waitKey(interval)

if __name__ == "__main__":
    main()
