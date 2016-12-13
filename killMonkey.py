import os, platform

if platform.system() == 'Windows':
    seek = 'findstr'
else:
    seek = 'grep'

def getDevicesList():
    getDevices = os.popen('adb devices').readlines()
    devicesList = []
    for devices in getDevices:
        if '\t' in devices:
            devicesID = devices.split('\t')[0]
            devicesList.append(devicesID)
    return devicesList

devicesList = getDevicesList()
for devicesID in devicesList:
    command = 'adb -s %s shell ps | %s monkey' %(devicesID, seek)
    process_monkey = os.popen(command).readlines()
    if len(process_monkey) > 0:
        for line in process_monkey:
            pid = line.split(' ')[5]
            killCommand = 'adb -s %s shell kill %s' %(devicesID, pid)
            os.system(killCommand)

