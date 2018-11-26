#!/usr/bean/python3
#coding:utf-8

'''
专项聚类
'''
import sys
sys.path.append("..")

from utils.cluster_util import mergeClusterInfo
from algorithm.cluster import ClusterResult
import time
import warnings

from db.db_compatible import updateCompatibleClusterMeidaNum, saveCompatibleArticleDetailInfo, \
    saveCompatibleClusterInfo, updateCompatibleClusterInfo, loadHistoryCompatibleClusterInfo, \
    saveCompatibleSpecialHistoryInfo, getCompatibleSpecialHistoryInfo

from utils.time_util import getQueryStartTimeBySpecailCreatetime
from db.db_mysql import getSpecialArticleInfoById, getMysqlConnect, getSpecialIds

from utils.logger import logger

#### zyy added ####

def saveResult( clusterUpdate, clusterAdd, articleDetailsAdd,specialId,latestId):
    try:
        conn = getMysqlConnect()
        ## step1: 更新信息
        if len(clusterUpdate) > 0:
            updateCompatibleClusterInfo(conn, clusterUpdate)
        ## step2: 保存新增聚类信息
        if len(clusterAdd) > 0:
            saveCompatibleClusterInfo(conn,clusterAdd)

        ## step3 : 保存文章聚类详情信息
        if len(articleDetailsAdd) > 0:
            saveCompatibleArticleDetailInfo(conn,articleDetailsAdd)

            ## step4: 保存new_t_special_history表中文章id信息
            saveCompatibleSpecialHistoryInfo(conn, specialId, latestId)

            ## 更新聚类表中的媒体信息
            updateCompatibleClusterMeidaNum(conn, specialId)

        ## 手动事务提交
        conn.commit()
    except:
        logger.error("saveResult error,rollback now",exc_info=1)
        conn.rollback() ## 发生异常则回滚
    finally:
        conn.close()

from config.config import updateConfig

if __name__=='__main__':
    start = time.clock()
    try:
        env = 'dev'
        if len(sys.argv) == 2:
            env = sys.argv[1]
        configure = updateConfig('env', 'env_active', env)
        warnings.filterwarnings(action='ignore', category=UserWarning, module='gensim')
        specialIdCreatetimeDic= getSpecialIds()  ## 专项列表
        logger.info("get specialIds from db: {0}".format(specialIdCreatetimeDic.keys()))
        ##获取专项对应的历史记录信息，dictionary: key：specialId, value: latestReTweetId
        specialIdHistoryDic = getCompatibleSpecialHistoryInfo()

        for specialId ,createTime in specialIdCreatetimeDic.items():
            try:
                logger.info("current special Id:{0},createTime:{1} ".format(specialId,createTime))
                if len(specialIdHistoryDic) == 0 or specialId not in specialIdHistoryDic:
                    startId = 0
                else:
                    startId = specialIdHistoryDic[specialId]
                ## 计算T-3天的开始日期
                queryStarttime = getQueryStartTimeBySpecailCreatetime(specialIdCreatetimeDic[specialId])

                articles = getSpecialArticleInfoById(specialId, startId,queryStartTime=queryStarttime)
                if articles is None or len(articles) == 0:
                    logger.info("没有获取到数据。spcialId:{0}, startId:{1} ".format(specialId, startId))
                    continue
                ## 没有过历史记录，则需要对所有的文章进行聚类
                lastArticleId = articles[-1].id  ## 最后一条记录的id 先保存起来，防止后期有其它地方修改
                lastClusterIndex = 0  ## 最后一条记录的聚类序号

                 ############### 获取数据结束，开始处理算法

                #### zyy modified ####
                logger.info('新来数据的开始聚类')
                clusterList = ClusterResult(articles)
                # print(clusterList)
                # update_phrase(clusterList)
                logger.info('新来数据的聚类已完成')
                # clusterList = getClusterResult(articles)
                if specialId not in specialIdHistoryDic:
                    historyClusterInfo = []
                else:
                    ## 从数据库中加载聚类历史数据
                    historyClusterInfo = loadHistoryCompatibleClusterInfo(specialId)
                    lastClusterIndex = 0 if historyClusterInfo is None or len(historyClusterInfo) == 0 else historyClusterInfo[-1].topicId
                ## 合并两个聚类结果信息
                clusterUpdate, clusterAdd, articleDetailsAdd = mergeClusterInfo(historyClusterInfo, clusterList, lastClusterIndex)
                ### 算法处理结束

                ## 保存信息到数据库
                saveResult(clusterUpdate, clusterAdd, articleDetailsAdd, specialId, lastArticleId)
            except Exception as ex:
                ## 在循环体内添加异常捕获，从而使得发生异常的时候，不至于影响其他的专项运行
                logger.error("specialId：{0} running occur exception now..".format(specialId), exc_info=1)

    except Exception as ex:
        logger.error("main function exception now..",exc_info = 1)

    end = time.clock()
    logger.info("spend time: {0} cpu seconds".format((end - start) ) )












