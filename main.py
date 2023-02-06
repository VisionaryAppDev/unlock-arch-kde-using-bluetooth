#!/usr/bin/python
from bluepy.btle import Scanner, DefaultDelegate
import subprocess
import datetime



def get_pc_lockscreen_status():
    result = subprocess.run("/usr/bin/ps -ef | /usr/bin/grep --count kscreenlocker_greet\ --", shell=True, stdout=subprocess.PIPE)
    result = int(str(result.stdout.decode('utf-8')))

    if result > 1:
        return "LOCKED"
    else:
        return "UNLOCKED"


def get_session_id():
    result = subprocess.run("loginctl | grep \"$whoami\" | head -n2 | awk 'FNR == 2 {print $1}'", shell=True, stdout=subprocess.PIPE)
    return str(result.stdout.decode("utf-8"))


def triggerDeviceLockscreen(command): 
    pc_lockscreen_status = get_pc_lockscreen_status()
    session_id = get_session_id()

    if pc_lockscreen_status == "UNLOCKED" and command == "LOCK":
        print("==> ✘ LOCK device.")
        subprocess.run("loginctl lock-session " + session_id, shell=True, stdout=subprocess.PIPE)
    elif pc_lockscreen_status == "LOCKED" and command == "UNLOCK":
        print("==> ✓ UNLOCK device.")
        subprocess.run("loginctl unlock-session " + session_id, shell=True, stdout=subprocess.PIPE)
    


class ScanDelegate(DefaultDelegate):
    def __init__(self, ble_mac_addresses, distance_threshold_in_meter=2):
        DefaultDelegate.__init__(self)
        self.ble_mac_addresses = ble_mac_addresses
        self.distance_threshold_in_meter = distance_threshold_in_meter
        self.last_seen_at = datetime.datetime.now()
        self.counter = 0


    def handleDiscovery(self, dev, isNewDev, isNewData):
        pc_lockscreen_status = get_pc_lockscreen_status()

        if dev.addr == self.ble_mac_addresses:
            self.last_seen_at = datetime.datetime.now()
            distance = dev.rssi / -60.0

            # Log info
            print("[%s] Device status %s, Found at %sm" % (datetime.datetime.now(), pc_lockscreen_status, format(distance, ".2f")))


            if distance <= self.distance_threshold_in_meter:
                self.counter = 0
                triggerDeviceLockscreen("UNLOCK")
            if distance > self.distance_threshold_in_meter:
                self.counter += 1

                # Reach threadhold to lock computer
                if self.counter >= 12:
                    self.counter = 0
                    triggerDeviceLockscreen("LOCK")
        elif (datetime.datetime.now() - self.last_seen_at) >= datetime.timedelta(seconds=12):
            self.counter = 0
            self.last_seen_at = datetime.datetime.now()

            print("Device status %s, not found for %sm", datetime.datetime.now() - self.last_seen_at, " second")
            triggerDeviceLockscreen("LOCK")


if __name__ == "__main__":
    scanner = Scanner().withDelegate(ScanDelegate("xxx"))
    while True:
        scanner.scan(1)
