#!/usr/bin/python
from bluepy.btle import Scanner, DefaultDelegate
import subprocess


status = "LOCKED"
authDeviceAddress = ["mac:address:here", "another-device-mac:address:here"]
minLockDistance = 3.0
minUnlockDistance = 1.5
minDistanceHistoryToVerifyB4Lock = 16
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

def getSessionId():
    # result = subprocess.run("loginctl session-status | grep \"$whoami\" | head -n1 | awk '{print $1;}'", shell=True, stdout=subprocess.PIPE)
    result = subprocess.run("loginctl | grep \"$whoami\" | head -n2 | awk 'FNR == 2 {print $1}'", shell=True, stdout=subprocess.PIPE)
    return result.stdout.decode("utf-8")



def triggerDeviceLockscreen(rssi, distance): 
    global status
    getCurrentLockscreenStatus()

    sessionId = str(getSessionId())
    if distance >= minLockDistance and status == "UNLOCKED" and isAuthDeviceReallyFarAway():
        status = "LOCKED"
        print("==> ✘ LOCK device. => Distance=%f m" % distance)
        subprocess.run("loginctl lock-session " + sessionId, shell=True, stdout=subprocess.PIPE)
    elif distance <= minUnlockDistance and status == "LOCKED":
        print("==> ✓ UNLOCK device. => Distance=%f m" % distance)
        status = "UNLOCKED"
        subprocess.run("loginctl unlock-session " + sessionId, shell=True, stdout=subprocess.PIPE)
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
        recordDistance(999)
        triggerDeviceLockscreen(999, 999)


def main():
    global authDeviceAddress
    stop = False

    while stop is False:
        devices = scannerTracking.scan(0.75)  
        isAuthDeviceFound = False
        nearestDevice = None

        for dev in devices:
            if dev.addr in authDeviceAddress: 
                isAuthDeviceFound = True

                # Switch to the nearest auth device to advoid far aways problem esp when timeout
                if not nearestDevice or getdistance(nearestDevice.rssi) > getdistance(dev.rssi): 
                    nearestDevice = dev

        
        if isAuthDeviceFound:
            distance = getdistance(nearestDevice.rssi)
            recordDistance(getdistance(dev.rssi))
            triggerDeviceLockscreen(nearestDevice.rssi, getdistance(dev.rssi))
        else:
            triggerDeviceLockscreenWhenAuthDeviceNoLongerInRange()
            

main()
