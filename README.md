# save_outside_camera
Connect to a security camera through RTSP and save the frames in storage
# Setup
## Requirements
```
sudo apt install python3-opencv
pip3 install numpy
```
## Setup
1. Set the storage path in `outside_camera.py`
2. Adapt `camera.service` to your **Path** and **user**.
3. Move `camera.service` to `/etc/systemd/system/`
4. Enable service: `sudo systemctl daemon-reload && sudo systemctl enable camera.service`
5. Start service: `sudo systemctl start camera`
