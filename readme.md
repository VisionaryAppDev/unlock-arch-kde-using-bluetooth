# ABOUT 
Having tried BlueProximity but couldn't get it to work on my Ubuntu long time ago. Having tried it again today but still couldn't make it working on my Arch Linux. So, trying google and found bluepy. Doesn't know how to make it working since I am not python developer and document contains too many cypher i couldn't understand xD. Continue google and land at [FabioTessarollo/RaspBeacon repo](https://github.com/FabioTessarollo/RaspBeacon)and steal of code and idea xD. Now I have my project done to unlock my linux easily xD.


# Install
```
sudo pip install bluepy
```


# CONFIG
- open `main.py` and add your device's bluetooth mac adress.


# Run
```
sudo python main.py
```

# Service
Create a systemd service at: `/etc/systemd/system/bluetooth-auth.service` 
```
[Unit]
Description=Bluetooth Auth Service
After=multi-user.target

[Service]
Environment=PYTHONUNBUFFERED=1
WorkingDirectory=/home/user/.bash
User=root
ExecStart=/usr/bin/python /home/user/.bash/main.py
Restart=always
StandardOutput=append:/tmp/bluetooth-auth.log
# CPUSchedulingPolicy=rr
# CPUSchedulingPriority=90

[Install]
WantedBy=multi-user.target
```

# PERMISSION
```
sudo chmod 600 main.py
sudo chown root:root main.py
```
