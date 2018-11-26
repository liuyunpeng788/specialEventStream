'''
处理与mysql相关的信息
'''
#!/usr/bean/python3
#coding:utf-8
import sys
sys.path.append("..")
import time
from datetime import datetime

import pymysql

from bean.Article import Article
from bean.ArticleAggregation import ArticleAggregation
from config.config import getConfig
from utils.logger import logger

'''
获取数据库连接
'''
conn = None
def getMysqlConnect():
    '''
    获取mysql 的连接信息
    :return: 与mysql 的连接
    '''
  
    try:
        configure = getConfig()
        host = configure['mysql']['host']
        username = configure['mysql']['username']
        password = configure['mysql']['password']
        database = configure['mysql']['database']
        port = configure.getint('mysql','port')
        charset = configure['mysql']['charset']
        # connect_timeout = configure['mysql'].getint('connect_timeout') or 100

        conn = pymysql.connect(host=host, user=username, passwd=password, db=database, port=port, charset=charset ,autocommit=False,cursorclass=pymysql.cursors.Cursor)
    except:
        logger.error('connect mysql failure', exc_info=1)
    return conn


def getSpecialAggregationData(accountId = None):
    ''''
    获取专项聚类历史数据信息
    @:param accountId: 账户信息
    @:return : 聚类后的文章列表
    '''
    try:
        with getMysqlConnect() as conn:
            sql = 'SELECT B.id,B.special_id,B.topicId,B.first_sys_id,B.topic_desc' \
                  ' FROM new_t_special A, `new_t_special_aggregation` B where A.group_id = B.special_id AND A.`status` = 1'
            if accountId is not None and str(accountId) != '':
                sql += " and A.account_id =" + str(accountId)
            conn.execute(sql)
            result = conn.fetchall()
            articleAggs = []  ## 文章列表
            for record in result:
                articleAggs.append(ArticleAggregation(id = record[0],specialId = record[1],topicId = record[2],firstMedia = record[3],mediaNum = record[4],articleNum = record[5],negaticeNum = record[6],releaseTime = record[7],topicDesc = record[8]))
    except Exception as e:
        logger.error("get special aggregation data error", exc_info=1)
        articleAggs = []
    return articleAggs

timeFormats = ['%Y-%m-%d %H:%M:%S','%Y-%m-%d','%Y-%m-%d %H:%M','%Y-%m-%d %H'] ##支持四种有效的时间格式
def validTimeRange(startTime = None,endTime = None):
    '''
    判断时间区间是否有效
    :param startTime: 起始日期
    :param endTime: 结束日期
    :return: errorCode 0：有效 1: 有时间字段为空 2: 起始日期大于结束日期 3：不是有效的日期格式
    '''
    if startTime is None or endTime is None:
        logger.error("time must not be None. startTime:{0}, endTime :{1}".format( startTime, endTime))
        return 1
    ## 判断日期是否有效
    else:
        startTime = startTime.strip()
        endTime = endTime.strip()
        if  startTime > endTime :
            logger.error("startTime greater than endTime.startTime:{0}, endTime :{1}".format( startTime, endTime))
            return 2
        else:
            ## 对起始时间日期的格式进行判断。如果不能转换为时间格式，则表示时间格式有误
            ## 起始日期的格式可以不同
            try:
                for timeFormat in timeFormats:
                    time.strptime(startTime,timeFormat)
                for timeFormat in timeFormats:
                    time.strptime(endTime, timeFormat)
            except:
                logger.error("time format is error. startTime:{0}，endTime:{1} ".format(startTime , endTime) , exc_info=1)
                return 3
            return 0


def getSpecialArticleInfoByCreateTime(specialId = None,startTime = None ,endTime = None):
    '''
    获取专项文章信息
    :param specialId:
    :return:
    '''
    if specialId is None:
        logger.error("specailId is None",exc_info=1)
        # logger.error(traceback.format_exc())
        return ()

    ## 判断日期是否有效
    res = validTimeRange(startTime,endTime)
    if res != 0 :
        logger.error("时间区间校验不过")
        return ()   ## 用一个空的set 可以避免进行空判断

    logger.info("specialId :{0}".format(specialId))
    articles = []
    try:
        with getMysqlConnect() as conn:
        # cur = conn.cursor()  # 获取一个游标
            tableName = "retweet_count_" + str(specialId)
            sql = "SELECT id,sysId,channelId,channelName,userName,releaseTime,title,referChannelId,groupId,createTime,url FROM "+ tableName
            sql += " WHERE createTime >= '"  + startTime + "' AND createTime < '" + endTime + "'"
           
            conn.execute(sql)
            result = conn.fetchall()

            for record in result:
                articles.append(Article(id = record[0],sysId = record[1], channelId= record[2],channelName = record[3],userName = record[4],releaseTime = record[5], title = record[6], referChannelId = record[7], groupId = record[8], createTime = record[9],url = record[10]))
    except Exception as e:
        logger.error("get specialId data from mysql fail. ", exc_info=1 )
        articles = []
    return articles

def getSpecialArticleInfoById(specialId ,startId ,endId = None,queryStartTime=None):
    '''
    获取专项文章信息
    :param specialId:
    :param startId 起始id
    :param endId 结束id
    :return: 文章列表
    '''
    logger.info("specialId: " + str(specialId) + " ,startId: " + str(startId) + " ,endId:" + str(endId) + ",queryStartTime :" + queryStartTime)
    if specialId is None or startId is None :
        logger.error("specailId or startId mustn't be None")
        # logger.error(traceback.format_exc())
        return ()

    articles = []
    try:
        with getMysqlConnect() as conn:
        # cur = conn.cursor()  # 获取一个游标
            tableName = "retweet_count_" + str(specialId)

            ## 为左开右闭区间
            sql = "SELECT id,sysId,channelId,channelName,userName,releaseTime,title,referChannelId,groupId,createTime,url,emotion FROM "+ tableName
            if startId is not None:
                sql += " where id > " + str(startId)
            if endId is not None:
                sql += " and id <= " + str(endId)
            if queryStartTime is not None:
                sql += " and releaseTime >= '" + str(queryStartTime) + "'"

            sql += " order by id"
            conn.execute(sql)
            result = conn.fetchall()
            logger.info("getSpecialArticleInfoById sql:  " + sql)
            for record in result:
                if record[6] is None or record[6] == '':  ## 标题不能为空
                    continue
                articles.append(Article(id = record[0],sysId = record[1], channelId= record[2],channelName = record[3],userName = record[4],releaseTime = record[5], title = record[6], referChannelId = record[7], groupId = specialId, createTime = record[9],url = record[10],emotion = record[11]))
    except:
        logger.error("get data from mysql fail. ", exc_info=1 )
        articles = []

    return articles


def getSpecialIds():
    '''
    获取专项id列表信息
    :return: key: specialId, value:create_time
    '''
    logger.info("getSpecialIds  ...")
    try:
        with getMysqlConnect() as conn:
            sql = "SELECT group_id,create_time from t_special where status = 1;"
            conn.execute(sql)
            result = conn.fetchall()
            sepcialIds = {}  ##专项列表信息
            for record in result:
                sepcialIds[record[0]] = record[1]
    except Exception as e:
        logger.error("get specialIds data from mysql fail. ", exc_info=1)
        sepcialIds = {}
    return sepcialIds


def getSpecialHistoryInfo():
    '''
    获取专项历史处理记录
    :return:  dictionary key: specialId value: latestRetweetId
    '''
    logger.info("getSpecialHistoryInfo  ...")
    try:
        with getMysqlConnect() as conn:

            sql = "SELECT special_id,latest_retweet_id from new_t_special_history"
            conn.execute(sql)
            result = conn.fetchall()
            historyRecordDic = {}  ##专项列表信息
            for record in result:
                historyRecordDic[record[0]] = record[1]
    except Exception as e:
        logger.error("get data from mysql fail. ", exc_info=1)
        historyRecordDic = ()
    return historyRecordDic

def loadHistoryClusterInfo(specialId):
    '''
    加载历史聚类信息
    :param specialId: 专项id 
    :return:  历史聚类信息
    '''
    logger.info("loadHistoryClusterInfo  ... ,specialID:{0}".format(specialId))
    try:
        historyClusterInfo = []
        with getMysqlConnect() as conn:
            sql = "SELECT id,cluster_index,special_id,first_sys_id,topic_desc,event_label,refed_times,create_time,update_time from new_t_special_aggregation where special_id = {0} order by cluster_index".format(specialId)
            conn.execute(sql)
            result = conn.fetchall()
            for record in result:
                 cluster = ArticleAggregation(id = record[0]
                                    ,clusterIndex=record[1]
                                    ,specialId = record[2]
                                    ,firstSysId=record[3]
                                    ,topicDesc=record[4]
                                    ,eventLabel=record[5]
                                    ,refedTimes = record[6]
                                    ,createTime=record[7]
                                    ,updateTime=record[8]
                                    )
                 historyClusterInfo.append(cluster)
    except:
        logger.error("get historyClusterInfo data from mysql fail. ", exc_info=1)
        historyClusterInfo = []
    return historyClusterInfo
        
def updateClusterInfo(conn,clusterUpdate):
    '''
    更新聚类信息
    '''
    logger.info("updateClusterInfo  ... ,to update cluster size:{0}".format(len(clusterUpdate)))
    try:
        with conn.cursor() as cursor:
            sql = "update new_t_special_aggregation set similar_num = %s ,create_time=%s ,update_time=%s where id = %s"
            values=[]
            for cluster in clusterUpdate:
                createTime = updateTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                values.append([cluster.similarNum,createTime,updateTime,cluster.id])
            res = cursor.executemany(sql,values)
            logger.info("成功更新{0}条聚类记录".format(res))
    except:
        logger.error("updateClusterInfo error." ,exc_info = 1)
        raise Exception


def saveClusterInfo(conn,clusterAdd):
    '''
    新增聚类信息
    :param clusterAdd: 待新增的聚类list
    '''
    logger.info("saveClusterInfo  ... ,to save cluster size:{0}".format(len(clusterAdd)))
    try:
        with conn.cursor() as cursor:
            values = []
            for cluster in clusterAdd:
                createTime = updateTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                sql = "insert into new_t_special_aggregation(cluster_index,special_id,first_sys_id,topic_desc,event_label,refed_times,create_time,update_time) values(%s,%s,%s,%s,%s,%s,%s,%s)"
                values.append([cluster.clusterIndex,cluster.specialId,cluster.firstSysId,cluster.topicDesc,cluster.eventLabel,cluster.refedTimes,createTime,updateTime])
            res = cursor.executemany(sql,values)
            logger.info("成功新增{0}条聚类记录".format(res))
    except:
        logger.error("saveClusterInfo error.", exc_info=1)
        raise Exception

def saveArticleDetailInfo(conn,articleDetailsAdd):
    '''
    保存新增文章详情信息
    :param articleDetailsAdd: 新增文章详情列表
    '''
    logger.info("saveArticleDetailInfo  ... ,to save cluster article detail size:{0}".format(len(articleDetailsAdd)))
    try:
        with conn.cursor() as cursor:

            values =[]
            for article in articleDetailsAdd:
                createTime = updateTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                sql = "insert into new_t_special_aggregation_detail(special_id,cluster_index,sys_id,media_name,emotion,release_time,site,url,title,content,refed_times,create_time,update_time,date_index) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) "
                    # .format(article.specialId,article.clusterIndex, article.sysId, article.userName, article.emotion,article.releaseTime,article.site,article.url,article.title,article.content,article.refedTimes,article.dateIndex)
                values.append([article.specialId,article.clusterIndex, article.sysId, article.mediaName, article.emotion,article.releaseTime,article.site,article.url,article.title,article.content,article.refedTimes,createTime,updateTime,article.dateIndex])
            res = cursor.executemany(sql,values)
            logger.info("成功新增{0}条聚类文章详情信息".format(res))
    except:
        logger.error("saveArticleDetailInfo error.", exc_info=1)
        raise Exception

def saveSpecialHistoryInfo(conn,specialId,articleId):
    '''
    保存专项文章历史记录信息
    :param specialId:  专项id
    :param articleId: 文章id
    '''
    logger.info("saveSpecialHistoryInfo...specialId:{0},articleId:{1}".format(specialId,articleId))
    try:
        with conn.cursor() as cursor:
            createTime = updateTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            sql = "insert into new_t_special_history(special_id,latest_retweet_id,create_time) values({0},{1},'{2}')".format(specialId,articleId,createTime)
            res = cursor.execute(sql)
            logger.info("成功新增{0}条聚类历史记录信息".format(res))
    except:
        logger.error("saveSpecialHistoryInfo error.", exc_info=1)
        raise Exception


if __name__ == '__main__':
    # getSpecialArticleInfoById(17,1);

    ## 保存信息到数据库
    ## step1: 更新信息
    clusterUpdate = []
    createTime = updateTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    clusterUpdate.append(ArticleAggregation(similarNum=12,createTime=createTime,updateTime=updateTime,id=1))
    clusterUpdate.append(ArticleAggregation(similarNum=15, createTime=createTime, updateTime=updateTime, id=2))
    updateClusterInfo(clusterUpdate)

    ## step2: 保存新增聚类信息
    # clusterAdd = []
    # clusterAdd.append(ArticleAggregation(id = None,clusterIndex=0,specialId = 17,firstSysId ='123',topicDesc ='测试title',eventLabel='start',similarNum =10))
    # clusterAdd.append(ArticleAggregation(id = None,clusterIndex=1,specialId = 17,firstSysId ='1235',topicDesc ='测试title',eventLabel='start',similarNum =10))
    # clusterAdd.append(ArticleAggregation(id = None,clusterIndex=2,specialId = 17,firstSysId ='1236',topicDesc ='测试title',eventLabel='start',similarNum =10))
    # saveClusterInfo(clusterAdd)

    ## step3 : 保存文章聚类详情信息
    # articleDetailsAdd=[]
    # createTime = updateTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    #
    # articleDetailsAdd.append(ArticleAggregationDetail(None,17, 1, '1234', u'中国传媒网', '-1', '2018-01-01 10:22:11', '百度', 'www.baidu.com', 'test1','test content', 1, dateIndex='2018-04-02', createTime=createTime, updateTime=updateTime))
    # articleDetailsAdd.append(ArticleAggregationDetail(None,17, 2, '1234',u'中国传媒网', '-1', '2018-01-01 10:22:11', '百度', 'www.baidu.com', 'test1','test content', 1, dateIndex='2018-04-02', createTime=createTime, updateTime=updateTime))
    # articleDetailsAdd.append(ArticleAggregationDetail(None,17,3, '1234', u'中国传媒网', '-1', '2018-01-01 10:22:11', '百度', 'www.baidu.com', 'test1','test content', 1, dateIndex='2018-04-02', createTime=createTime, updateTime=updateTime))
    #
    # saveArticleDetailInfo(articleDetailsAdd)
    #
    # ## step4: 保存new_t_special_history表中文章id信息
    # saveSpecialHistoryInfo(specialId, articles[-1].id)




