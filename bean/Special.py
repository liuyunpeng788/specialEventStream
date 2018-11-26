#!/usr/bean/python3
#coding:utf-8

'''
专项表信息
'''
import sys
sys.path.append("..")
class Special:
  def __init__(self,**kwargs):
      self.id = kwargs['id']  ## 自增主键
      self.accountId = kwargs['accountId']  ## 账户id
      self.userId = kwargs['userId']  ## 登录用户id
      self.specialName = kwargs['specialName'] ## 专项名称
      self.groupId = kwargs['groupId'] ## 专项id
      self.status = kwargs['status'] ## 状态
