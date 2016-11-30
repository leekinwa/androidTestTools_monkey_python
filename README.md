#monkeyTool

##实现需求：
运行monkey测试，出现报错时获取日志保存本地，并对日志进行去重，本地仅保留唯一日志。

直接运行monkeyTest.py即可，按需添加参数，参数说明参见下方脚本说明。
##脚本说明：
1. 脚本运行方式：monkeyTest.py [-p processName][-t throttle(delay)]
2. 参数说明：
	* -p：指定monkey测试程序（可指定多个被测程序，以空格隔开）；
	* -t：monkey测试事件间时延；
	* -h：帮助信息；
	* 不输入参数运行整机测试。
2. 获取log判断错误类型（crash/anr）获取对应log：
	* crash分别取logcat、bugreport、dropbox并保留本地;
	* anr分别取logcat、bugreport、dropbox、/data/anr并保留本地；
	* 若日志内无错误信息，则删除日志文件夹；
	* 兼容sdkTools升级后monkey不能通过重定向获取错误日志问题；
	* 兼容新旧版本sdkTools bugreport获取方式。
3. 本地log去重：
	* 去重逻辑依赖三方库Levenshtein算法，使用本工具时需自行安装；
	* 只对crash类型log进行去重；
	* 去重逻辑为比对字符相似度（仅对比日志报错堆栈），如相似度大于95%，则删除日志文件夹，确保本地日志的唯一性；
	* anr类型日志无法进行去重，一律保留；
4. 后期规划：
	* 多设备运行，通过list管理多个设备并通过多线程方式（threading）实现；
	* 计算MTTF时间，monkey运行时间；
	* 自动提单，结合bug管理系统；