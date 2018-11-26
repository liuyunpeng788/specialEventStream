#!/usr/bean/python3
#coding:utf-8

'''
聚类详情信息
'''
import sys
sys.path.append("..")
class ArticleAggregationDetail:
    def __init__(self,id = None,specialId= None,clusterIndex=None ,sysId='',mediaName=''
                 ,emotion = 0,releaseTime= '',site='',url='',title='',  content='', refedTimes=0,createTime=None,updateTime=None,dateIndex=''):
        self.id = id
        self.specialId = specialId
        self.clusterIndex = clusterIndex  # 聚类索引
        self.sysId = sysId
        self.mediaName = mediaName
        self.emotion = emotion
        self.releaseTime= releaseTime
        self.site= site
        self.url= url
        self.title= title
        self.content= content
        self.refedTimes = refedTimes
        self.createTime= createTime ## 数据库自动更新
        self.updateTime= updateTime ## 数据库自动更新
        self.dateIndex = dateIndex


    def getRefedNum(self):
        return self.refedTimes

    def autoIncreaseRefedNum(self):
        self.refedTimes += 1
