#!/usr/bean/python3
# coding:utf-8
import sys
sys.path.append("..")
from bean.EsSpecialAgg import EsSpecialAgg
from db.db_mysql import getMysqlConnect
from utils.logger import logger
from datetime import datetime

def loadHistoryCompatibleClusterInfo(specialId):
    '''
    加载历史聚类信息
    :param specialId: 专项id
    :return:  历史聚类信息
    '''
    logger.info("loadHistoryCompatibleClusterInfo  ... ,specialID:{0}".format(specialId))
    try:
        historyClusterInfo = []
        with getMysqlConnect() as conn:
            sql = "SELECT id,specialId,topicId,first_media,media_num,article_num,negatice_num,release_time,topicDesc,phrase from t_es_special_agg_info where specialId = {0} order by topicId".format(
                specialId)
            conn.execute(sql)
            result = conn.fetchall()
            for record in result:
                cluster = EsSpecialAgg(record[0], record[1],record[2] , record[3], record[4] , record[5], record[6] , record[7] , record[8], record[9])
                historyClusterInfo.append(cluster)
    except:
        logger.error("get loadHistoryCompatibleClusterInfo data from mysql fail. ", exc_info=1)
        historyClusterInfo = []
    return historyClusterInfo


def updateCompatibleClusterInfo(conn, clusterUpdate ):
    '''
    更新聚类信息
    '''
    logger.info("updateCompatibleClusterInfo  ... ,to update cluster size:{0}".format(len(clusterUpdate)))
    try:
        with conn.cursor() as cursor:
            values = []
            for cluster in clusterUpdate:
                # createTime = updateTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                sql = "update t_es_special_agg_info set article_num = %s ,negatice_num = %s where id = %s"
                values.append([cluster.article_num , cluster.negatice_num , cluster.id])
            res = cursor.executemany(sql, values)
            logger.info("成功更新{0}条聚类记录".format(res))
    except:
        logger.error("updateCompatibleClusterInfo error.", exc_info=1)
        raise Exception


def saveCompatibleClusterInfo(conn, clusterAdd):
    '''
    新增聚类信息
    :param clusterAdd: 待新增的聚类list
    '''
    logger.info("saveCompatibleClusterInfo  ... ,to save cluster size:{0}".format(len(clusterAdd)))
    try:
        with conn.cursor() as cursor:
            values = []
            for cluster in clusterAdd:

                # print("phrase:{0}".format(cluster.phrase) )
                createTime = updateTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                sql = "insert into t_es_special_agg_info(specialId,topicId,first_media,media_num,article_num,negatice_num,release_time,topicDesc,phrase) values(%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                values.append([cluster.specialId, cluster.topicId, cluster.first_media, cluster.media_num,cluster.article_num, cluster.negatice_num,cluster.release_time, cluster.topicDesc,cluster.phrase])
            res = cursor.executemany(sql, values)
            logger.info("成功新增{0}条聚类记录".format(res))
    except:
        logger.error("saveCompatibleClusterInfo error.", exc_info=1)
        raise Exception


def saveCompatibleArticleDetailInfo(conn, articleDetailsAdd):
    '''
    保存新增文章详情信息
    :param articleDetailsAdd: 新增文章详情列表
    '''
    logger.info("saveCompatibleArticleDetailInfo  ... ,to save cluster article detail size:{0}".format(len(articleDetailsAdd)))
    try:
        with conn.cursor() as cursor:

            values = []
            for article in articleDetailsAdd:
                createTime = updateTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                sql = "insert into t_es_special_infos(specialId,topicId,topicDesc,sysId,release_time,emotion,site) values(%s,%s,%s,%s,%s,%s,%s) "
                # .format(article.specialId,article.clusterIndex, article.sysId, article.userName, article.emotion,article.releaseTime,article.site,article.url,article.title,article.content,article.refedTimes,article.dateIndex)
                values.append( [article.specialId, article.topicId, article.topicDesc, article.sysId, article.release_time,article.emotion, article.site])
            res = cursor.executemany(sql, values)
            logger.info("成功新增{0}条聚类文章详情信息".format(res))
    except:
        logger.error("saveCompatibleArticleDetailInfo error.", exc_info=1)
        raise Exception

def getCompatibleSpecialHistoryInfo():
    '''
    获取专项历史处理记录
    :return:  dictionary key: specialId value: latestRetweetId
    '''
    logger.info("getSpecialHistoryInfo  ...")
    try:
        with getMysqlConnect() as conn:

            sql = "SELECT special_id,latest_retweet_id from t_special_history"
            conn.execute(sql)
            result = conn.fetchall()
            historyRecordDic = {}  ##专项列表信息
            for record in result:
                historyRecordDic[record[0]] = record[1]
    except Exception as e:
        logger.error("get data from mysql fail. ", exc_info=1)
        historyRecordDic = ()
    return historyRecordDic

def saveCompatibleSpecialHistoryInfo(conn,specialId,articleId):
    '''
    保存专项文章历史记录信息
    :param specialId:  专项id
    :param articleId: 文章id
    '''
    logger.info("saveCompatibleSpecialHistoryInfo...specialId:{0},articleId:{1}".format(specialId,articleId))
    try:
        with conn.cursor() as cursor:
            createTime = updateTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            sql = "insert into t_special_history(special_id,latest_retweet_id,create_time) values({0},{1},'{2}')".format(specialId,articleId,createTime)
            res = cursor.execute(sql)
            logger.info("成功新增{0}条聚类历史记录信息".format(res))
    except:
        logger.error("saveCompatibleSpecialHistoryInfo error.", exc_info=1)
        raise Exception

####### 更新媒体数统计信息
def updateCompatibleClusterMeidaNum(conn,specialId):
    '''
    更新媒体数信息
    :param conn:
    :param specialId:
    :return:
    '''
    logger.info("updateCompatibleClusterMeidaNum  ... ,specialId :{0}".format(specialId))
    try:
        with conn.cursor() as cursor:
            sql = "SELECT A.id,COUNT(DISTINCT site) AS site FROM `t_es_special_agg_info` A, t_es_special_infos B WHERE A.specialId = B.specialId AND A.topicId = B.topicId "
            if specialId :
                sql += "AND A.SpecialId = " + str(specialId) + " "
            sql += " GROUP BY A.id"

            cursor.execute(sql)
            result = cursor.fetchall()
            for record in result:
                updateSql = "update t_es_special_agg_info set media_num={0} where id = {1}".format(record[1],record[0])
                cursor.execute(updateSql)
        logger.info("成功更新{0}条聚类媒体数信息".format(len(result)))
    except:
        logger.error("updateCompatibleClusterMeidaNum error.", exc_info=1)
        raise Exception

