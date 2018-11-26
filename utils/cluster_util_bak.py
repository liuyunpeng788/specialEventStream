#!/usr/bean/python3
#coding:utf-8

'''
处理聚类相关的辅助类
'''
import sys
sys.path.append("..")
from datetime import datetime
from gensim import similarities, corpora
from bean.EsSpecialAgg import EsSpecialAgg
from bean.EsSpecialInfos import EsSpecialInfos
from config.config import getConfig
from utils.jieba_util import getBreakWordTitleList, getJiebaTitleList
from utils.logger import logger
from utils.model_util import buildTfidfModel
from gensim.similarities import Similarity

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

    if len(articles) == 1: ## 只有一篇文章，直接返回
        result = []  ## 聚类结果
        result.append(articles)
        logger.info( "聚类结束后，文章数量：{0} ，聚类数:{1},其中，单个聚类中最大的文章数：{2}，无法聚类的文章数：{3} ".format(1, 1, 1, 1))
        return result

    articles.sort(key=lambda x: x.releaseTime)
    jiebaTitleList = getBreakWordTitleList(articles)
    if jiebaTitleList is None or len(jiebaTitleList) == 0:
        return None

    title

    # 生成字典和向量语料
    dictionary = corpora.Dictionary(jiebaTitleList)  ## 将每个词放入到字典中，即每个词对应一个从0开始的id. 如0: 姓名 1: 经济

    corpus = [dictionary.doc2bow(text) for text in jiebaTitleList]
    ## 计算模型中相似的文章
    clusterDic = {}  ## 聚类词典
    ####文档相似性的计算
    flag = [0] * len(corpus)  ##标记文章是否已经合并过
    logger.info("artilces size :{0},flag size:{1},corpus size:{2}".format(len(articles),len(flag),len(corpus)))

    index = Similarity(None, corpus=corpus, num_features=len(dictionary))  # 余弦相似度
    for i in range(len(corpus)):  ## id表示的文档向量
        if flag[i] == 1: continue
        sims = index[corpus[i]]
        # sims = index[tfidf_model[corpus[i]]]
        sorted_sims = sorted(enumerate(sims), key=lambda item: -item[1])  ## 返回 文章序号 和 相似度值
        ## 获取相似度最高的作为文章归属的依据
        similarArticleItems = sorted([item for item in sorted_sims if item[1] >= similar_threshold and flag[item[0]] == 0] )[1:] # 所有相似度大于0.45（除自身外）的索引集合

        if len(similarArticleItems) == 0:
            continue

        sysId = articles[i].sysId

        logger.info("cluster:{0},sysid:{1},title:{2} ---------".format(i,sysId,articles[i].title))
        for item in similarArticleItems:
            if flag[item[0]] == 1:
                continue
            logger.info("index:{0}  title:{1},相似度：{2}".format(item[0], articles[item[0]].title,item[1]))
            flag[i] = 1
            flag[item[0]] = 1
            if item[1] >= 1.0:
                # 该文章可能为转载
                articles[i].autoIncreaseRefedNum()  ## 引用量自增
            if sysId not in clusterDic:
                 logger.info("{0} not in clusterDic".format(sysId))
                 clusterDic[sysId] = [articles[i],articles[item[0]]]
            else:
                clusterDic[sysId].append(articles[item[0]])

        logger.info("--------------------------")

    for unSimilarIndex in range(len(flag)):  ## 处理不相似的数据
        ## 最大相似度都不大于阀值，则应独立生成一个聚类
        if flag[unSimilarIndex] == 0:
            clusterDic[articles[unSimilarIndex].sysId] = [articles[unSimilarIndex]]
            flag[unSimilarIndex] = 1
            logger.info("unSimilarIndex:{0},sysid:{1},title:{2} ---------".format(unSimilarIndex, articles[unSimilarIndex].sysId, articles[unSimilarIndex].title))

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


def ArtilceToArticleClusterDetail(specialId,topicId,articles):
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
        articleAggDetail = EsSpecialInfos(
            id = None
            ,specialId = specialId
            ,topicId = topicId
            ,topicDesc = article.title
            ,sysId = article.sysId
            ,release_time = article.releaseTime
            ,emotion = article.emotion  ## 待修改
            ,site = article.channelName  ## 媒体名称
        )
        articleAggDetails.append(articleAggDetail)

    return articleAggDetails

def parseFirstArtilceToCluster(clusterIndex,artilce,article_num = 0,negatice_num = 0):
    '''
    将聚类的首篇文章转换为聚类。
    :param clusterIndex: 聚类id
    :param artilce: 文章
    :param refedTimes : 被引用文章数
    :return:
    '''
    createTime = updateTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return EsSpecialAgg(
        id = None,
        topicId = clusterIndex,
        specialId= artilce.groupId,
        first_media = artilce.channelName,
        media_num = 0 ,
        article_num = article_num,
        negatice_num = negatice_num,
        release_time = artilce.releaseTime,
        topicDesc = artilce.title
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
    # 生成字典和向量语料
    dictionary = corpora.Dictionary(jiebaTitleList)  ## 将每个词放入到字典中，即每个词对应一个从0开始的id. 如0: 姓名 1: 经济
    historyCorpus = [dictionary.doc2bow(text) for text in jiebaTitleList]

    toJiebaClusterTitleList = getJiebaTitleList(toClusterArticles)
    # dictionary, tfidf_model, corpus_tfidf = buildTfidfModel(jiebaTitleList)
    corpus = [dictionary.doc2bow(text) for text in toJiebaClusterTitleList]

    ####文档相似性的计算
    index = Similarity(None, corpus=historyCorpus, num_features=len(dictionary))  # 余弦相似度
    for i in range(len(corpus)):
        sims = index[corpus[i]]
        sorted_sims = sorted(enumerate(sims), key=lambda item: -item[1])  ## 返回 文章序号 和 相似度值
        maxSimilar = sorted_sims[0]

        if maxSimilar[1] < similar_threshold:
            simDic[i] = None
        if maxSimilar[1] >= similar_threshold:
            simDic[i] = maxSimilar[0]
    return simDic


def mergeClusterInfo(historyClusterInfo,clusterList,lastClusterIndex):
    '''
    合并聚类信息 ,如果没有已聚类的信息，则返回转换后的新增聚类信息。
    如果有聚类信息，则返回合并后的聚类信息，包括更新和新增部分

    :param historyClusterInfo: 历史聚类信息 list
    :param clusterList: 新增数据的聚类信息 list
    :param lastClusterIndex 最后一条记录的聚类序号
    :return:  合并后的聚类信息： clusterUpdate：更新聚类信息（相似文章数），clusterAdd: 新增聚类信息
                articleDetailsAdd：新增文章详情
    '''
    articleDetailsAdd = []
    clusterUpdate = []  #如果有合并的相似文章，则需要更新文章数，媒体数量添加完详情数据后再更新
    clusterAdd = []
    try:
        if historyClusterInfo is None or len(historyClusterInfo) == 0:
            logger.info("历史聚类信息中无数据")
            ## 将clusterList 转换为聚类信息即可
            index = 1
            for newCluster in clusterList:
                index += 1
                ## 将新增文章添加到文章列表
                articleClusterDetails = ArtilceToArticleClusterDetail(newCluster[0].groupId, index, newCluster)
                negArticleNum = len(list(filter(lambda x:x.emotion == -1,newCluster)))
                clusterAdd.append(parseFirstArtilceToCluster(index,newCluster[0],article_num = len(newCluster),negatice_num = negArticleNum))
                if len(articleClusterDetails) > 0:
                    articleDetailsAdd.extend(articleClusterDetails)
        else:
            maxHistoryClusterIndex = lastClusterIndex  ##聚类id 的最大序号
            clusterMergeDic = getMostSimilarCluster(historyClusterInfo,clusterList) ## 聚类合并字典
            specialId = historyClusterInfo[0].specialId
            for toMergeClusterIndex,historyClusterIndex in clusterMergeDic.items():  ## key: 待合并的文章聚类，value: 合并的目标历史聚类序号
                if historyClusterIndex is None:
                    # 为None,表示新增
                    ## 将新增文章添加到文章列表
                    maxHistoryClusterIndex += 1
                    negArticleNum = len(list(filter(lambda x: x.emotion == -1, clusterList[toMergeClusterIndex])))
                    clusterAdd.append(parseFirstArtilceToCluster(maxHistoryClusterIndex, clusterList[toMergeClusterIndex][0], article_num = len(clusterList[toMergeClusterIndex]),negatice_num = negArticleNum))
                    articleClusterDetails = ArtilceToArticleClusterDetail(specialId, maxHistoryClusterIndex , clusterList[toMergeClusterIndex])
                    if len(articleClusterDetails) > 0:
                        articleDetailsAdd.extend(articleClusterDetails)
                else:
                    #待合并的文章中，负面文章数
                    negArticleNum = len(list(filter(lambda x: x.emotion == -1,clusterList[toMergeClusterIndex])))
                    historyClusterInfo[historyClusterIndex].negatice_num += negArticleNum
                    #判断首篇文章被引用数
                    if historyClusterInfo[historyClusterIndex].topicDesc == clusterList[toMergeClusterIndex][0].title:
                        historyClusterInfo[historyClusterIndex].article_num += len(clusterList[toMergeClusterIndex])

                    clusterUpdate.append(historyClusterInfo[historyClusterIndex])  ## 待更新
                    articleClusterDetails = ArtilceToArticleClusterDetail(specialId, historyClusterInfo[historyClusterIndex].topicId , clusterList[toMergeClusterIndex])
                    if len(articleClusterDetails) > 0:
                        articleDetailsAdd.extend(articleClusterDetails)
    except:
        logger.error("mergeClusterInfo error",exc_info = 1)
        articleDetailsAdd = []
        clusterUpdate = []
        clusterAdd = []
    return clusterUpdate ,clusterAdd, articleDetailsAdd




input()


output()