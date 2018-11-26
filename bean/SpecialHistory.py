#!/usr/bean/python3
#coding:utf-8

import sys
sys.path.append("..")
'''
专项历史数据，用于确定记录每次处理专项的时，从retween表中获取数据的最大id
'''

class SpecialHistory:
    def __init__(self,id,specialId,latestRetweetId,createTime=None):
        self.id = id  ## 自增主键
        self.specialId = specialId  ## 专项id
        self.latestRetweetId = latestRetweetId  ## 上次处理的数据id
        self.createTime = createTime ## 创建时间 yyyy-MM-dd hh:mm:ss格式

