# ABOUT 
Having tried BlueProximity but couldn't get it to work on my Ubuntu long time ago. Having tried it again today but still couldn't make it working on my Arch Linux. So, trying google and found bluepy. Doesn't know how to make it working since I am not python developer and document contains too many cypher i couldn't understand xD. Continue google and land at [FabioTessarollo/RaspBeacon repo](https://github.com/FabioTessarollo/RaspBeacon)and steal of code and idea xD. Now I have my project done to unlock my linux easily xD.


# Install 
sudo pip install bluepy


# CONFIG
- open main.py and add your device's bluetooth mac adress into authDeviceAddress. `authDeviceAddress=["xx:xx:xx:xx:xx:xx", "xx:xx.."]`


# PERMISSION
chmod 755 mean.py


# Run
sudo python mean.py
