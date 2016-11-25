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

# dropbox取log方法;
def dropbox(log_readlines_position = 0):
    dropboxList = []
    dropboxList_all = os.popen('adb shell dumpsys dropbox').readlines()
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
    getLogCommand = 'adb shell dumpsys dropbox --print %s %s' %(ymd, hms)
    dropbox_logContent_list = os.popen(getLogCommand).readlines()
    log_index = []
    keyword = 'Process: ' + processName
    dropbox_logContent = ''
    # 通过进程名定位log分片位置;
    for log_startIndex_line in range(len(dropbox_logContent_list)):
        if keyword in dropbox_logContent_list[log_startIndex_line]:
            log_index.append(log_startIndex_line)
    log_startIndex = max(log_index) + 7
    for log_endIndex_line in range(len(dropbox_logContent_list[log_startIndex:])):
        if '===' in dropbox_logContent_list[log_endIndex_line]:
            log_endIndex = log_endIndex_line
            dropbox_logContent = ''.join(dropbox_logContent_list[log_startIndex:log_endIndex])
            break
        else:
            dropbox_logContent = ''.join(dropbox_logContent_list[log_startIndex:])
    return errType, processName, dropbox_logContent

# bugreport取日志方法, 用以兼容sdktools新旧版本;
def bugReport():
    adbVersion = int(os.popen('adb version').readline().split('.')[-1].replace(r'\n', ''))
    # 新版本sdktools取bugreport为zip;
    if adbVersion > 32:
        os.popen('adb bugreport ' + folderPath())
    # 旧版本sdktools取bugreport为文本, 通过重定向获取;
    else:
        os.popen('adb bugreport > ' + folderPath('bugreport.log'))

# 取日志主函数;
def logkit(seed, errType = ''):
    timestamp = time.strftime('%Y%m%d%H%M%S',time.localtime(time.time()))
    global folderName_time
    folderName_time = 'monkeyLog' + timestamp
    os.makedirs(folderPath())
    time.sleep(1)
    os.popen('adb logcat -v time -d > ' + folderPath('logcatReport.log'))
    time.sleep(2)
    logFile_open = open(folderPath('logcatReport.log'))
    logcat_logContent = logFile_open.read()
    logFile_open.close()
    # 日志内有错误信息保留bugreport和dropbox, 日志无错误信息删除文件夹;
    if 'FATAL EXCEPTION:' in logcat_logContent or 'ANR in' in logcat_logContent:
        bugReport()
        errType, processName, dropbox_logContent = dropbox()
        file_object = open(folderPath('dropboxLog.log'), 'w')
        file_object.writelines(dropbox_logContent)
        file_object.close()
        if errType == 'ANR':
            os.popen('adb pull /data/anr/traces.txt' + folderPath())
        time.sleep(2)
        folder_rename = os.path.join(currentPath, folderName_date, folderName_time + '_%s_seed%s_%s' %(errType, seed, processName))
        os.rename(folderPath(), folder_rename)
        time.sleep(2)
    else:
        shutil.rmtree(folderPath())
    return errType
