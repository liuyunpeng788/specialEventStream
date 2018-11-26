# -*- coding:utf-8 -*-
import sys
sys.path.append("..")
import numpy as np
from simhash import Simhash
from algorithm import util_seg
from utils.logger import logger

# simhash
def simhash_cluster(articles):
    hash_dic = {}
    cluster = {}
    title_dict = {}
    article_dict = {}
    flag = True

    try:
        for item in articles:
            _id = item.sysId
            text = item.title + item.content
            # text = item.title
            title_dict[_id] = ' '.join(util_seg.segment(text))
            article_dict[_id] = item

            simhash = Simhash(text)

            # 首次进入字典，无需和别人比较
            if flag:
                hash_dic[simhash] = [_id]
                cluster[_id] = [_id]
                flag = False
                continue

            f = True
            # 与hashdic内的结果作比较
            for k in hash_dic:
                dis = simhash.distance(k)
                if dis < 15:
                    key = hash_dic[k][0]
                    cluster[key].append(_id)
                    f = False
                    break
            # 与dic中完全不相似
            if f:
                hash_dic[simhash] = [_id]
                cluster[_id] = [_id]

    except:
        logger.error("Simhash Clustering error", exc_info=1)

    return cluster, title_dict, article_dict

def gen_keyword(cluster, title_dict):
    keyword_dict = {}

    try:
        for obj in cluster:
            text = ''
            for s in cluster[obj]:
                text += title_dict.get(s)
            keyword_dict[obj] = util_seg.nv_segment(text)
    except Exception as e:
        logger.error("Generating Phrase error", exc_info=1)

    return keyword_dict

# 通过keyword找相似主题,返回id——idlist对
def find_similar(keyword_dict):
    news_pool = list()
    similar_dict = {}

    try:
        for obj in keyword_dict:
            if obj not in news_pool:
                similar_dict[obj] = [obj]
                news_pool.append(obj)
            else:
                continue

            for s in keyword_dict:
                if s in news_pool:
                    continue

                bing = list(set(keyword_dict[obj] + keyword_dict[s]))
                jiao = [l for l in keyword_dict[obj] if l in keyword_dict[s]]

                if len(bing) == 0:
                    continue

                if len(jiao) * 1.0/len(bing) > 0.7:
                # if len([l for l in keyword_dict[obj] if l in keyword_dict[s]]) >= 3:
                    similar_dict[obj].append(s)
                    news_pool.append(s)
    except:
        logger.error("Phrase Clustering error", exc_info=1)

    return similar_dict

# 合并成类
def combine2list(cluster2, cluster3):
    topic_list = []

    try:
        for key in cluster3:
            topic_little = cluster3[key]
            length = len(cluster3[key])
            for i in range(length):
                id = cluster3[key][i]
                topic_little.extend(cluster2[id])
            topic_little = list(set(topic_little))
            topic_list.append(topic_little)
    except:
        logger.error("Combine Clustering error", exc_info=1)

    return topic_list

# 计算权重
def calculate(dic):
    average = 0
    length = len(dic.keys())

    try:
        for key in dic:
            average += dic[key]
        average = average / length
        for key in dic:
            dic[key] = 1 / (1 + np.exp(-(dic[key] - average) / (average + 1)))
    except:
        logger.error("Calculate Weight error", exc_info=1)

    return dic


# 计算每条新闻关键词权重
def keyword_weight(topic_list, title_list):
    dic = {}
    total_title = ''
    words = []

    try:
        for news_id in topic_list:
            total_title += title_list[news_id]
        words = util_seg.nv_segment(total_title)
        for news_id in topic_list:
            title = title_list[news_id]
            keyword = util_seg.nv_segment(title)
            dic[news_id] = len([l for l in keyword if l in words])
        dic = calculate(dic)
    except:
        logger.error("Calculate Phrase Weight error", exc_info=1)

    return dic,words

def top_news_list(topic_list,title_list,article_list):
    ans = []

    try:
        for l in topic_list:
            ans_little = []
            w_dic,words = keyword_weight(l, title_list)
            w_sort = sorted(w_dic.items(), key=lambda d: d[1], reverse=True)
            for id in w_sort:
                article_list[id[0]].updatePhrase(','.join(words[0:10]))
                ans_little.append(article_list[id[0]])
            ans.append(ans_little)
    except:
        logger.error("Find Top News error", exc_info=1)

    return ans

def ClusterResult(articles):
    '''
    添加异常处理
    :param articles: 文章对象
    :return:
    '''
    d = 0
    keyword_dict=article_dict={}
    try:
        cluster1, title_dict, article_dict = simhash_cluster(articles)
        keyword_dict = gen_keyword(cluster1, title_dict)
        cluster2 = find_similar(keyword_dict)
        topic_list = combine2list(cluster1, cluster2)
        d = top_news_list(topic_list,title_dict,article_dict)
    except Exception as ex:
        logger.error("ClusterResult 文章长度：{0} running occur exception now..".format(len(articles)), exc_info=1)
    return d