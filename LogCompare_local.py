#coding=UTF-8

import os, Levenshtein, shutil


currentPath = os.getcwd()

# 计算log相似度;
def logSimilarity(str1, str2):
    log_similarity = 1 - float(Levenshtein.distance(str1, str2)) / max(len(str1), len(str2))
    return log_similarity

# 比对log相似度;
def logCompare():
    logPath = []
    # 获取当前路径下所有monkeyLog路径;
    for parent, dir, file in os.walk(currentPath):
        if '_CRASH_' in parent:
            logPath.append(parent)

    # 两份以上log开始执行比对;
    if len(logPath) > 1:
        # 提取最新生成日志内容进行过滤;
        str1_path = logPath[-1]
        str1_open = open(os.path.join(str1_path, 'dropboxLog.log'))
        str1 = str1_open.read()
        str1_open.close()

        for logPath_str2 in logPath[:-1]:
            str2_path = logPath_str2
            str2_open = open(os.path.join(str2_path, 'dropboxLog.log'))
            str2 = str2_open.read()
            str2_open.close()
            log_similarity = logSimilarity(str1, str2)
            if log_similarity >= 0.95:
                print u'log相似度大于95%, 日志删除。'
                shutil.rmtree(str1_path)
                break
    else:
        print u'只有一份log, 不进行比对。'
