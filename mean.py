#!/usr/bin/python
from bluepy.btle import Scanner, DefaultDelegate
import subprocess


status = "LOCKED"
authDeviceAddress = "mac:address:here"
minLockDistance = 3.0
minUnlockDistance = 1.5
minDistanceHistoryToVerifyB4Lock = 3
lastThreeDistanceHistory = []


class ScanDelegateTracking(DefaultDelegate): 
    def __init__(self):
        DefaultDelegate.__init__(self)

    def handleDiscovery(self, dev, isNewDev, isNewData): pass


def getdistance(rssi):
    txpower = -59   #one meter away RSSI
    if rssi == 0:
        return -1
    else:
        ratio = rssi*1.0 / txpower
        if ratio < 1:
            return ratio ** 10
        else:
            return 0.89976 * ratio**7.7095 + 0.111


scannerTracking = Scanner().withDelegate(ScanDelegateTracking())

def getCurrentLockscreenStatus():
    global status
    result = subprocess.run("/usr/bin/ps -ef | /usr/bin/grep --count kscreenlocker_greet\ --", shell=True, stdout=subprocess.PIPE)
    result = int(str(result.stdout.decode('utf-8')))

    if result > 1:
        # print("Current status: LOCKED")
        status = "LOCKED"
    else:
        # print("Current status: UNLOCKED")
        status = "UNLOCKED"



def triggerDeviceLockscreen(rssi, distance): 
    global status
    getCurrentLockscreenStatus()
    if distance >= minLockDistance and status == "UNLOCKED" and isAuthDeviceReallyFarAway():
        status = "LOCKED"
        print("==> ✘ LOCK device. => Distance=%f m" % distance)
        subprocess.run("loginctl lock-session", shell=True, stdout=subprocess.PIPE)
    elif distance <= minUnlockDistance and status == "LOCKED":
        print("==> ✓ UNLOCK device. => Distance=%f m" % distance)
        status = "UNLOCKED"
        subprocess.run("loginctl unlock-session", shell=True, stdout=subprocess.PIPE)
    else:
        print("Status=%s, RSSI=%d dB, Distance=%f m" % (status, rssi, distance))
    

def recordDistance(distance):
    global minDistanceHistoryToVerifyB4Lock
    global lastThreeDistanceHistory
    if len(lastThreeDistanceHistory) == minDistanceHistoryToVerifyB4Lock:
        lastThreeDistanceHistory.pop(0)
    
    lastThreeDistanceHistory.append(distance)


def isAuthDeviceReallyFarAway():
    global minDistanceHistoryToVerifyB4Lock
    global lastThreeDistanceHistory
    global minLockDistance

    if len(lastThreeDistanceHistory) != minDistanceHistoryToVerifyB4Lock:
        return False

    isFarAway = True
    for distance in lastThreeDistanceHistory:
        if distance < minLockDistance:
            isFarAway = False
            break

    return isFarAway


def triggerDeviceLockscreenWhenAuthDeviceNoLongerInRange():
    global lastThreeDistanceHistory

    # if lastThreeDistanceHistory is not empty it mean auth device was once in range 
    if lastThreeDistanceHistory:
        triggerDeviceLockscreen(999, 999)


def main():
    global authDeviceAddress
    stop = False

    while stop is False:
        devices = scannerTracking.scan(3.0)  
        isAuthDeviceFound = False

        for dev in devices:
            if dev.addr == authDeviceAddress: 
                isAuthDeviceFound = True
                break

        
        if isAuthDeviceFound:
            distance = getdistance(dev.rssi)
            recordDistance(distance)
            triggerDeviceLockscreen(dev.rssi, distance)
        else:
            triggerDeviceLockscreenWhenAuthDeviceNoLongerInRange()
            

main()