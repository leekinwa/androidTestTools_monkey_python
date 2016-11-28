#coding=UTF-8
'''
脚本使用方法:
1. 在命令行输入“python 路径/脚本”即可运行;
2. '-p' 参数为需执行monkey程序包名, 可输入多个包名, 不输入包名为整机测试;
3. '-t' 参数为时延, 单位为毫秒;
4. '-h' 帮助。
'''


import os, time, random, LogCompare_local, Logkit
from optparse import OptionParser


def device():
    device_exsit = ''
    reTry = 0
    while reTry < 10:
        getDevices = os.popen('adb get-state').readline()
        if 'device' in getDevices:
            device_exsit = True
            break
        else:
            os.popen('adb kill-server')
            time.sleep(2)
            os.popen('adb start-server')
            device_exsit = False
            reTry += 1
    if device_exsit == False:
        print u'未识别到手机，请查看手机是否连接成功。'
        exit()

def Monkey(seed, runcount, event):
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
    else:
        # processName为空, 跳过参数解析, 执行整机测试;
        pass

    # 根据参数执行不同monkey命令并获取日志;
    if processName == None and delay == None:
        print u'monkey整机测试, 无时延, 第%s次测试。' %runcount
        monkeyCommand = 'adb shell monkey --pct-trackball 0 --pct-nav 0 -s %s %s' %(seed, event)
    elif processName == None and delay != None:
        print u'monkey整机测试, %s毫秒时延, 第%s次测试。' %(delay, runcount)
        monkeyCommand = 'adb shell monkey --pct-trackball 0 --pct-nav 0 -s %s --throttle %s %s' %(seed, delay, event)
    elif processName != None and delay != None:
        if len(processList) == 0:
            print u'monkey %s模块测试, %s毫秒时延, 第%s次测试。' %(processName, delay, runcount)
        else:
            print u'monkey %s模块测试, %s毫秒时延, 第%s次测试。' %(processList, delay, runcount)
        monkeyCommand = 'adb shell monkey --pct-trackball 0 --pct-nav 0 %s -s %s --throttle %s %s' %(monkeyCommand_processName, seed, delay, event)
    else:
        if len(processList) == 0:
            print u'monkey %s模块测试, 无时延, 第%s次测试。' %(processName, runcount)
        else:
            print u'monkey %s模块测试, 无时延, 第%s次测试。' %(processList, runcount)
        monkeyCommand = 'adb shell monkey --pct-trackball 0 --pct-nav 0 %s -s %s %s' %(monkeyCommand_processName, seed, event)
    os.popen('adb logcat -c')
    # print monkeyCommand
    os.popen(monkeyCommand)
    device()
    getLog_exist = Logkit.logkit(seed)
    if getLog_exist == 'CRASH':
        LogCompare_local.logCompare()

def main():
    device()
    runcount = 1
    while (runcount <= 500):
        seed = random.randint(1, 900)
        Monkey( str(seed), str(runcount), event='999999999')
        runcount += 1

if __name__=='__main__':
    main()