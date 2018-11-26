#!/usr/bean/python3
#coding:utf-8

''''
 工具类
'''
import sys
sys.path.append("..")
from datetime import datetime, timedelta


'''
替换非法字符
'''
def removeIllegalChar(value):
    import re
    return re.sub("[\x00-\x1f\x7f【】]","",value)

'''
标准化es查询结果中的返回时间格式
'''
def normalReleaseTime(releaseTime = ""):
    if releaseTime.index(".") > 0:
        releaseTime = releaseTime.split(".")[0].replace("T", " ").strip()
    elif releaseTime.index("+") > 0:
        releaseTime = releaseTime.split("+")[0].replace("T", " ").strip()
    else:
        releaseTime = releaseTime.replace("T", " ").strip()

    return releaseTime

'''
格式化ES的release查询时间
'''
def normalQueryByReleaseTime(paramTime):
 return paramTime.strftime("%Y-%m-%dT%H:%M:%S.000+08:00")


'''
获取默认的起始和结束时间
当查询的时间参数为空的时候，调用此函数
'''
def getDefaultTimeRange():
    starttime = datetime.now()
    endtime = starttime - timedelta(hours=3)
    return normalQueryByReleaseTime(starttime),normalQueryByReleaseTime(endtime)

def getQueryStartTimeBySpecailCreatetime(specialCreatetime = None,delta = 3):
    '''
    根据专项的创建时间，获取T-3 天前的时间
    :param createtime:
    :return:
    '''
    startTime = datetime.now() if specialCreatetime is None else datetime.strptime(str(specialCreatetime),"%Y-%m-%d %H:%M:%S")
    startTime = startTime - timedelta(days=delta)
    return startTime.strftime("%Y-%m-%d %H:%M:%S")

if __name__=='__main__':
    res = getQueryStartTimeBySpecailCreatetime("2014-10-21 14:02:00")
    print(res)