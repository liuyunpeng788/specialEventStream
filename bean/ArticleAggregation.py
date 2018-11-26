#!/usr/bean/python3
#coding:utf-8

'''
文章聚类结果类
'''
import sys
sys.path.append("..")
class ArticleAggregation:
    def __init__(self,id = None,clusterIndex=None,specialId = None,firstSysId = '',topicDesc ='',eventLabel ='',refedTimes = 0,createTime=None,updateTime=None):
        self.id = id     ## 聚类id
        self.clusterIndex = clusterIndex # 聚类索引
        self.specialId = specialId  ## 专项id
        self.firstSysId = firstSysId  ## 首篇文章id
        self.topicDesc =  topicDesc  ## topic描述，一般为首篇文章title
        self.eventLabel = eventLabel ## 事件流标识
        self.refedTimes = refedTimes ## 被引用文章数
        self.createTime = createTime ## 创建时间 yyyy-MM-dd hh:mm:ss 格式
        self.updateTime = updateTime  ## 更新时间



