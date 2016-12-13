#coding=UTF-8
import os, shutil, time

# 根据时间戳创建日志存放文件夹;
datestamp = time.strftime('%Y%m%d', time.localtime(time.time()))
currentPath = os.getcwd()
folderName_date = 'monkeyTest_' + datestamp

# 路径构成;
def folderPath(fileName = ''):
    if fileName == '':
        path = os.path.join(currentPath, folderName_date, folderName_time)
    else:
        path = os.path.join(currentPath, folderName_date, folderName_time, fileName)
    return path

# 记录monkey运行时间;
def monkey_runtime(runtime):
    filePath = os.path.join(currentPath, folderName_date, 'MTTF.txt')
    fileOpen = open(filePath, 'a')
    fileOpen.writelines(runtime + '\n')
    fileOpen.close()
    time.sleep(5)

# dropbox取log方法;
def dropbox(devicesID):
    dropboxList = []
    dropboxLog = ''
    dropboxList_all = os.popen('adb -s ' + devicesID + ' shell dumpsys dropbox').readlines()
    for dropboxLog in dropboxList_all:
        if 'system_app_crash' in dropboxLog or 'data_app_crash' in dropboxLog or 'system_app_anr' in dropboxLog or 'data_app_anr' in dropboxLog:
            log_position =  dropboxList_all.index(dropboxLog)
            log = dropboxList_all[log_position] + dropboxList_all[log_position + 1]
            dropboxList.append(log)
    # drogbox最后一份log;
    dropCommand_element = dropboxList[-1].replace('\r\n', '').split(' ')
    # 获取log时间戳;
    ymd = dropCommand_element[0]
    hms = dropCommand_element[1]
    # 获取进程名;
    processName_position = dropCommand_element.index('Process:') + 1
    processName = dropCommand_element[processName_position].split('/')[0]
    # 获取错误类型, anr or crash;
    if 'anr' in dropCommand_element[2]:
        errType = 'ANR'
    else:
        errType = 'CRASH'
    # 获取log内容;
    getLogCommand = 'adb -s %s shell dumpsys dropbox --print %s %s' %(devicesID, ymd, hms)
    dropbox_logContent_all = os.popen(getLogCommand).readlines()
    if errType == 'CRASH':
        log_index = []
        keyword = 'Process: ' + processName
        # 通过进程名定位log分片位置;
        for log_startIndex_line in range(len(dropbox_logContent_all)):
            if keyword in dropbox_logContent_all[log_startIndex_line]:
                log_index.append(log_startIndex_line)
        log_startIndex = max(log_index) + 7
        dropbox_logContent = dropbox_logContent_all[log_startIndex:]
        for log_endIndex_line in range(len(dropbox_logContent)):
            if '===' in dropbox_logContent[log_endIndex_line]:
                log_endIndex = log_endIndex_line
                dropboxLog = ''.join(dropbox_logContent[:log_endIndex])
                break
            else:
                dropboxLog = ''.join(dropbox_logContent)
    else:
        dropboxLog = os.popen(getLogCommand).read()
    time.sleep(1)
    return errType, processName, dropboxLog

# bugreport取日志方法, 用以兼容sdktools新旧版本;
def bugReport(devicesID):
    adbVersion = int(os.popen('adb version').readline().split('.')[-1].replace(r'\n', ''))
    # 新版本sdktools取bugreport为zip;
    if adbVersion > 32:
        bugReportCommand = 'adb -s %s bugreport %s' %(devicesID, folderPath())
    # 旧版本sdktools取bugreport为文本, 通过重定向获取;
    else:
        bugReportCommand = 'adb -s %s bugreport > %s' %(devicesID, folderPath('bugreport.log'))
    os.popen(bugReportCommand)

# 取日志主函数;
def logkit(devicesID, seed, runtime):
    errType = ''
    timestamp = time.strftime('%Y%m%d%H%M%S',time.localtime(time.time()))
    global folderName_time
    folderName_time = 'monkeyLog' + timestamp
    os.makedirs(folderPath())
    time.sleep(1)
    logcatCommand = 'adb -s %s logcat -v time -d > %s' %(devicesID, folderPath('logcatReport.log'))
    dmesgCommand = 'adb -s %s shell dmesg -t > %s' %(devicesID, folderPath('dmesg.log'))
    topCommand = 'adb -s %s shell top -s cpu -n 1 > %s' %(devicesID, folderPath('top.log'))
    os.popen(logcatCommand)
    os.popen(dmesgCommand)
    os.popen(topCommand)
    time.sleep(2)
    logFile_open = open(folderPath('logcatReport.log'))
    logcat_logContent = logFile_open.read()
    logFile_open.close()
    # 日志内有错误信息保留bugreport和dropbox, 日志无错误信息删除文件夹;
    if 'FATAL EXCEPTION:' in logcat_logContent or 'ANR in' in logcat_logContent:
        errType, processName, dropboxLog = dropbox(devicesID)
        file_object = open(folderPath('dropboxLog.log'), 'w')
        file_object.writelines(dropboxLog)
        file_object.close()
        if errType == 'ANR':
            anrCommand = 'adb -s %s pull /data/anr/traces.txt %s' %(devicesID, folderPath())
            os.popen(anrCommand)
        # bugReport(devicesID)
        time.sleep(2)
        print u'重命名'
        folder_rename = os.path.join(currentPath, folderName_date, folderName_time + '_%s_%s_seed%s_%s' %(devicesID, errType, seed, processName))
        print u'原文件名:', folderPath()
        print u'重命名文件名:', folder_rename
        os.rename(folderPath(), folder_rename)
    else:
        print folderPath(), u'无错误日志'
        shutil.rmtree(folderPath())
    monkey_runtime(runtime)
    return errType
