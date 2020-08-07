# Save RTSP camera
Connect to a security camera through RTSP and save the frames in storage. Cameras in the local network (LAN) running RTSP with default port (554) are automatically discovered.

# Quick-start
## Requirements
```
apt install python3-opencv
```
## Setup
1. Copy `config.json.default` to `config.json` and set it up to your liking.
2. Adapt `camera.service` to your **Path** and **user**.
3. Move `camera.service` to `/etc/systemd/system/`
4. Enable service: `sudo systemctl daemon-reload && sudo systemctl enable camera.service`
5. Start service: `sudo systemctl start camera`

## Config
Below is an example of a potential `config.json`. For every new discovered server, the default credentials are used. A new frame is stored in `path` every `interval` seconds, with the following format: `path/<year>/<month>/<day>/hour:min:sec.jpg`.
Before running the LAN scan, the software will try to connect to the servers in the list, using their credentials or the default ones if there are none.
The `servers` key can also be empty (`"servers": []`).
```
{
  "default_username": "admin",
  "default_password": "admin",
  "interval": 3,
  "path": "$HOME/frames",
  "servers": [ 
	       {
		 "address": "10.0.0.33"
	       },
	       {
		 "address": "1.2.3.4",
		 "username": "kibHJI8j",
		 "password": "78gImbEuuCvs4"
	       }
	     ]
}
```
