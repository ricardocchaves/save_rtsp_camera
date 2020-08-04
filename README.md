# Save RTSP camera
Connect to a security camera through RTSP and save the frames in storage
# Setup
## Requirements
```
apt install python3-opencv
```
## Setup
1. Setup `config.json` to your liking.
2. Adapt `camera.service` to your **Path** and **user**.
3. Move `camera.service` to `/etc/systemd/system/`
4. Enable service: `sudo systemctl daemon-reload && sudo systemctl enable camera.service`
5. Start service: `sudo systemctl start camera`
