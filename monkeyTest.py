#coding=UTF-8
'''
脚本使用方法:
1. 在命令行输入“python 路径/脚本”即可运行;
2. '-p' 参数为需执行monkey程序包名, 可输入多个包名, 不输入包名为整机测试;
3. '-t' 参数为时延, 单位为毫秒;
4. '-h' 帮助。
'''


import os, time, random, LogCompare_local, Logkit, threading, timeit, platform, multiprocessing
from optparse import OptionParser

# 计时器;
def timer():
    if platform.system() == 'Windows':
        default_timer = time.clock
    else:
        default_timer = time.time
    return timeit.default_timer()

# 判断设备连接状态;
def wait_for_device(devicesID):
    device_exsit = ''
    reTry = 0
    while reTry < 10:
        getDevices_command = 'adb -s %s get-state' %devicesID
        getDevices = os.popen(getDevices_command).readline()
        if 'device' in getDevices:
            device_exsit = True
            break
        else:
            os.popen('adb -s ' + devicesID + ' kill-server')
            time.sleep(2)
            os.popen('adb -s ' + devicesID + ' start-server')
            device_exsit = False
            reTry += 1
    if device_exsit == False:
        print u'未识别到手机，请查看手机是否连接成功。'
        exit()

# 获取设备list;
def getDevicesList():
    getDevices = os.popen('adb devices').readlines()
    devicesList = []
    for devices in getDevices:
        if '\t' in devices:
            devicesID = devices.split('\t')[0]
            devicesList.append(devicesID)
            set_logcat_buffer = 'adb -s %s shell logcat -G 1M' %devicesID
            os.popen(set_logcat_buffer)
    return devicesList

def monkey_commands(devicesID, seed, event):
    monkeyCommand_processName = ''
    # 参数解析;
    usage = 'monkeyTest.py [-p <processName>][-t <throttle(delay)>]'
    parser = OptionParser(usage)
    parser.add_option('-p', dest='processName', help = u'进程名, 可输入多个进程名, 为空则执行整机monkey测试。')
    parser.add_option('-t', dest='Delay', help = u'时延, 事件间时间间隔, 单位为毫秒（ms）。')
    (options, args) = parser.parse_args()
    processName = options.processName
    delay = options.Delay
    processList = args
    # 单个process和多个process处理;
    if len(processList) == 0 and processName != None:
        processList.append(processName)
        monkeyCommand_processName = ' -p ' + processList[0]
    elif len(processList) >= 1:
        processName_command = []
        processList.append(processName)
        for process in processList:
            processName_command.append(' -p ' + process)
        monkeyCommand_processName = ''.join(processName_command)
        processName = ', '.join(processList)
    else:
        # processName为空, 跳过参数解析, 执行整机测试;
        pass
    # 根据参数执行不同monkey命令并获取日志;
    if processName == None and delay == None:
        monkeyCommand = 'adb -s %s shell monkey --pct-trackball 0 --pct-nav 0 -s %s %s' %(devicesID, seed, event)
    elif processName == None and delay != None:
        monkeyCommand = 'adb -s %s shell monkey --pct-trackball 0 --pct-nav 0 -s %s --throttle %s %s' %(devicesID, seed, delay, event)
    elif processName != None and delay != None:
        monkeyCommand = 'adb -s %s shell monkey --pct-trackball 0 --pct-nav 0 %s -s %s --throttle %s %s' %(devicesID, monkeyCommand_processName, seed, delay, event)
    else:
        monkeyCommand = 'adb -s %s shell monkey --pct-trackball 0 --pct-nav 0 %s -s %s %s' %(devicesID, monkeyCommand_processName, seed, event)
    return monkeyCommand, processName, delay

def monkeyRun(devicesID):
    runcount = 200
    event = '999999999'
    for count in range(runcount):
        wait_for_device(devicesID)
        seed = str(random.randint(1, 900))
        monkeyCommand, processName, delay = monkey_commands(devicesID, seed, event)
        print u'count: %s devices: %s; process: %s; delay: %s' %(count, devicesID, processName, delay )
        os.popen('adb -s ' + devicesID + ' logcat -c')
        startTime = timer()
        os.popen(monkeyCommand)
        endTime = timer()
        runtime = str(round((endTime - startTime)/60, 2))
        wait_for_device(devicesID)
        getLog_exist = Logkit.logkit(devicesID, seed, runtime)
        if getLog_exist == 'CRASH':
            LogCompare_local.logCompare()

def main():
    devicesList = getDevicesList()
    for devicesID in devicesList:
        # monkeyThread = threading.Thread(target=monkeyRun, args=(devicesID, ))
        # monkeyThread.start()
        monkeyProcess = multiprocessing.Process(target=monkeyRun, args=(devicesID, ))
        monkeyProcess.start()

if __name__=='__main__':
    main()