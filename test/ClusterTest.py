from db.db_compatible import loadHistoryCompatibleClusterInfo
from utils.cluster_util import getClusterResult, mergeClusterInfo


def algorith(specialId,articles,specialIdHistoryDic):
    '''
     算法处理模块
    :param specialId:  专项id
    :param articles: 专项id对应的文章列表
    :param specialIdHistoryDic:  字典结构，专项id 和 t_special_history 表的latestReTweetId 构成的字典。dictionary: key：specialId, value: latestReTweetId
       :return:  合并后的聚类信息，其中：
            clusterUpdate：更新后的聚类信息（主要更新相似文章数、负面文章数等字段。list[EsSpecialAgg]），哪些历史聚类下新增了相似文章
            clusterAdd: 新增聚类信息(list[EsSpecialAgg])。新增的文章没有和历史聚类相似，则需要新增聚类
            articleDetailsAdd：新增文章详情 list[EsSpecialInfos]。 直接入库即可。
    '''
    clusterList = getClusterResult(articles)

    if specialId not in specialIdHistoryDic:
        historyClusterInfo = []
    else:
        ## 从数据库中加载聚类历史数据
        historyClusterInfo = loadHistoryCompatibleClusterInfo(specialId)
        lastClusterIndex = 0 if historyClusterInfo is None or len(historyClusterInfo) > 0 else historyClusterInfo[
            -1].topicId
    ## 合并两个聚类结果信息
    clusterUpdate, clusterAdd, articleDetailsAdd = mergeClusterInfo(historyClusterInfo, clusterList, lastClusterIndex)



if __name__=='__main__':
    algorith(specialId, articles, specialIdHistoryDic)
