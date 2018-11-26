#!/usr/bean/python3
#coding:utf-8

'''
文章信息
'''
import sys
sys.path.append("..")
class Article():

    def __init__(self,id=None,sysId='',channelId=None,channelName='',userName='',releaseTime='',title='',content='',referChannelId=None,groupId=None,createTime=None,url=None,emotion = 0,phrase = '' ):
        self.id = id
        self.sysId = sysId  ## 文章id
        self.channelId = channelId  ## 渠道id
        self.channelName = channelName ## 渠道名称
        self.userName = userName  ## 文章发表的媒体名称
        self.releaseTime = releaseTime ## 发表时间  yyyy-MM-dd hh:mm:ss 格式
        self.title = title  ## 文章标题
        self.content=content  ##文章内容
        self.referChannelId = referChannelId ## 引用渠道
        self.groupId = groupId ## 专项id
        self.createTime = createTime ## 创建时间 yyyy-MM-dd hh:mm:ss 格式
        self.url = url ## 文章url.
        self.refedTimes = 0
        self.emotion = emotion
        self.phrase = phrase


    def getRefedNum(self):
        return self.refedTimes

    def autoIncreaseRefedNum(self):
        self.refedTimes += 1

    def updatePhrase(self,phrase):
        self.phrase = phrase