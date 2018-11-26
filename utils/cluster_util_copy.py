#!/usr/bean/python3
#coding:utf-8
'''
处理聚类相关的辅助类
'''
from datetime import datetime
from gensim import similarities
import sys

sys.path.append("..")
from bean.ArticleAggregation import ArticleAggregation
from bean.ArticleAggregationDetail import ArticleAggregationDetail
from config.config import getConfig
from utils.jieba_util import getBreakWordTitleList, getJiebaTitleList
from utils.logger import logger
from utils.model_util import buildTfidfModel

configure = getConfig()
similar_threshold = configure.getfloat('threshold','similar_threshold')

def getClusterResult(articles):
    '''
    对当前的文章进行聚类
    :param articles: 文章
    :return:  聚类的文章列表
    '''
    # 对每个article 的title进行聚类
    logger.info("聚类前的总文章数：{0}".format(len(articles)))
    if articles is None or len(articles) == 0:
        logger.info("文章数为空")
        return None

    articles.sort(key=lambda x: x.releaseTime)
    jiebaTitleList = getBreakWordTitleList(articles)
    if jiebaTitleList is None or len(jiebaTitleList) == 0:
        return None

    ## 没有过历史记录，则需要对所有的文章进行聚类

    dictionary, tfidf_model, corpus_tfidf = buildTfidfModel(jiebaTitleList)
    corpus = [dictionary.doc2bow(text) for text in jiebaTitleList]
    ## 计算模型中相似的文章
    clusterDic = {}  ## 聚类词典
    ####文档相似性的计算
    index = similarities.MatrixSimilarity(corpus_tfidf)
    flag = [0] * len(articles)  ##标记文章是否已经合并过

    for i in range(len(corpus)):  ## id表示的文档向量
        sims = index[tfidf_model[corpus[i]]]
        sorted_sims = sorted(enumerate(sims), key=lambda item: -item[1])  ## 返回 文章序号 和 相似度值
        ## 获取相似度最高的作为文章归属的依据
        similarArticleItems = sorted([item for item in sorted_sims if item[1] >= similar_threshold])  # 所有相似度大于0.7（除自身外）的索引集合
        if len(similarArticleItems) > 0:
            minIndex = min(similarArticleItems[0][0], i)  ## 取相似列表中，下标最小的文章作为key 的索引
            sysId = articles[minIndex].sysId
        for item in similarArticleItems:
            if item[0] == i or flag[item[0]] == 1:
                continue;  ## 如果是两个相同的文章，则不必比较
            if item[1] >= 1.0:
                # 该文章可能为转载
                articles[minIndex].autoIncreaseRefedNum()  ## 引用量自增
            if clusterDic is None or sysId not in clusterDic:
                if flag[minIndex] == 0:
                    clusterDic[sysId] = [articles[minIndex]]
                    clusterDic[sysId].append(articles[item[0]])
                    flag[minIndex] = flag[item[0]] = 1
            else:
                clusterDic[sysId].append(articles[item[0]])
                flag[item[0]] = 1

    for unSimilarIndex in range(len(flag)):  ## 处理不相似的数据
        ## 最大相似度都不大于阀值，则应独立生成一个聚类
        if flag[unSimilarIndex] == 0:
            clusterDic[articles[unSimilarIndex].sysId] = [articles[unSimilarIndex]]
            flag[unSimilarIndex] = 1

    cnt = single = maxNum = 0
    result = []  ## 聚类结果
    for key, value in clusterDic.items():
        cnt += len(value)
        if len(value) == 1:
            single += 1
        if len(value) >= maxNum:
            maxNum = len(value)
        result.append(value)
    logger.info( "聚类结束后，文章数量：{0} ，聚类数:{1},其中，单个聚类中最大的文章数：{2}，无法聚类的文章数：{3} ".format(cnt, len(clusterDic), maxNum, single))
    return result


def ArtilceToArticleCluster(specialId,topicId,articles):
    '''
    文章列表转聚类文章列表
    :param specialId: 专项id
    :param topicId: 聚类id
    :param articles: 文章列表
    :return: 聚类详情列表
    '''
    if specialId is None or topicId is None or articles is None:
        logger.error("参数不能为None。specialId:{0},topicId:{1}".format(specialId,topicId))
        return ()
    if len(articles) == 0 :
        logger.error("articles 不能为空。specialId:{0},topicId:{1}".format(specialId,topicId))
        return ()
    articleAggDetails = []
    for article in articles:
        articleAggDetail = ArticleAggregationDetail(
            specialId = specialId
            ,clusterIndex = topicId
            ,sysId = article.sysId
            ,mediaName = article.userName  ## 媒体名称
            ,emotion = article.emotion
            ,releaseTime = article.releaseTime
            ,site =  article.channelName
            ,url = article.url
            ,title = article.title
            ,content = article.content
            ,refedTimes = article.refedTimes
            ,dateIndex = datetime.now().strftime("%Y-%m-%d")
        )
        articleAggDetails.append(articleAggDetail)

    return articleAggDetails

def parseFirstArtilceToCluster(clusterIndex,artilce,similarNum = 0):
    '''
    将聚类的首篇文章转换为聚类。
    :param clusterIndex: 聚类id
    :param artilce: 文章
    :param similarNum : 相似文章数
    :return:
    '''
    createTime = updateTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return ArticleAggregation(
        id=None,
        clusterIndex= clusterIndex,
        specialId= artilce.groupId,
        firstSysId= artilce.sysId,
        topicDesc= artilce.title,
        eventLabel = '',
        similarNum= similarNum,
        createTime = createTime,
        updateTime = updateTime
    )

def getMostSimilarCluster(historyClusterInfo,toClusterList):
    '''
    获取待合并的聚类与历史聚类信息的合并映射关系  如{1:3,2:None} 表示待合并的聚类1 与历史聚类3 相似,
    待合并的聚类2没有相似的历史聚类信息，属于新增聚类
    :param historyClusterInfo: 历史聚类信息
    :param toClusterList: 待合并的聚类信息
    :return:
    '''
    historyClusterArticles = []  ## 历史聚类信息
    toClusterArticles = []  ## 待聚类信息
    for historyCluster in historyClusterInfo:
        historyClusterArticles.append(historyCluster.topicDesc)

    for articles in toClusterList:
        toClusterArticles.append(articles[0].title)

    simDic = {} ## 相似文章集合 key: 历史文章，value : 待合并的聚类序号

    jiebaTitleList = getJiebaTitleList(historyClusterArticles)
    toJiebaClusterTitleList = getJiebaTitleList(toClusterArticles)
    dictionary, tfidf_model, corpus_tfidf = buildTfidfModel(jiebaTitleList)
    corpus = [dictionary.doc2bow(text) for text in toJiebaClusterTitleList]

    ## 计算模型中相似的文章
    clusterDic = {}  ## 聚类词典
    ####文档相似性的计算
    index = similarities.MatrixSimilarity(corpus_tfidf)
    for i in range(len(corpus)):
        sims = index[tfidf_model[corpus[i]]]
        sorted_sims = sorted(enumerate(sims), key=lambda item: -item[1])  ## 返回 文章序号 和 相似度值
        maxSimilar = sorted_sims[0]

        if maxSimilar[1] < similar_threshold:
            simDic[i] = None
        if maxSimilar[1] >= similar_threshold:
            simDic[i] = maxSimilar[0]
    return simDic


def mergeClusterInfo(historyClusterInfo,clusterList):
    '''
    合并聚类信息 ,如果没有已聚类的信息，则返回转换后的新增聚类信息。
    如果有聚类信息，则返回合并后的聚类信息，包括更新和新增部分

    :param historyClusterInfo: 历史聚类信息 list
    :param clusterList: 新增数据的聚类信息 list
    :return:  合并后的聚类信息： clusterUpdate：更新聚类信息（相似文章数），clusterAdd: 新增聚类信息
                articleDetailsAdd：新增文章详情
    '''
    articleDetailsAdd = []
    clusterUpdate = []
    clusterAdd = []
    try:
        if historyClusterInfo is None or len(historyClusterInfo) == 0:
            logger.info("历史聚类信息中无数据")
            ## 将clusterList 转换为聚类信息即可
            index = 0
            for newCluster in clusterList:
                ## 将新增文章添加到文章列表
                articleClusterDetails = ArtilceToArticleCluster(newCluster[0].groupId, index, newCluster)
                index += 1
                clusterAdd.append(parseFirstArtilceToCluster(index,newCluster[0],similarNum = len(newCluster)-1))
                if len(articleClusterDetails) > 0:
                    articleDetailsAdd.extend(articleClusterDetails)
        else:
            maxHistoryClusterIndex = historyClusterInfo[-1].clusterIndex  ##聚类id 的最大序号
            for aggregation in historyClusterInfo:
                ## 比较两个聚类的首篇title 是否相似
                topicDesc = aggregation.topicDesc
                set1 = set(getBreakWordTitleList([topicDesc])[0])
                for newCluster in clusterList:
                    topicId = aggregation.topicIndex
                    specialId = aggregation.specialId
                    firstClusterArticle = newCluster[0]
                    set2 = set(getBreakWordTitleList([firstClusterArticle.title])[0])
                    similar = len(set1.intersection(set2)) / len(set1.union(set2))
                    if similar >= 0.6:  ## 两个主题相似，则需要进行合并
                        aggregation.similarNum += len(newCluster)-1
                        clusterUpdate.append(aggregation)  ## 待更新
                    else:
                        topicId = maxHistoryClusterIndex = maxHistoryClusterIndex + 1
                        clusterAdd.append(firstClusterArticle)

                    ## 将新增文章添加到文章列表
                    articleClusterDetails = ArtilceToArticleCluster(specialId, topicId, newCluster)
                    if len(articleClusterDetails) > 0:
                        articleDetailsAdd.extend(articleClusterDetails)

    except:
        logger.error("mergeClusterInfo error",exc_info = 1)
        articleDetailsAdd = []
        clusterUpdate = []
        clusterAdd = []
    return clusterUpdate ,clusterAdd, articleDetailsAdd



