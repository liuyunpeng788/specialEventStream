#!/usr/bean/python3
#coding:utf-8

'''
处理分词相关信息
'''
import jieba.analyse
import sys

sys.path.append("..")
from utils.logger import logger


def getBreakWordTitleList(articles = None):
    '''
    对文章的标题进行分词
    :param articles: 文章列表，按照时间升序排序
    :return:
    '''
    if articles is None:
        logger.info("articles is None")
        return None

    jiebaTitleList = []
    jieba.load_userdict('../resources/dict.txt')
    jieba.analyse.set_stop_words('../resources/stopWord.txt')
    i = 0
    for article in articles:
        seg = jieba.analyse.extract_tags(article.title.strip().lower(), topK=20)
        # seg = list(jieba.cut(article.title.strip(), cut_all=False))
        # s = ' '.join(seg)
        # print(i, " -- ", article.title.strip().lower(),"---",str(seg))  # 输出标题
        if len(seg) > 0:
            jiebaTitleList.append(seg)
        i += 1

    return jiebaTitleList


def getJiebaTitleList(titleList = None):
    '''
    对标题列表进行分词
    :param articles: 文章列表，按照时间升序排序
    :return:
    '''
    if titleList is None or len(titleList) == 0:
        logger.info("articles is None")
        return None

    jiebaTitleList = []
    jieba.load_userdict('../resources/dict.txt')
    jieba.analyse.set_stop_words('../resources/stopWord.txt')
    i = 0
    for title in titleList:
        seg = jieba.analyse.extract_tags(title.strip().lower(), topK=20)
        # seg = list(jieba.cut(article.title.strip(), cut_all=False))
        # s = ' '.join(seg)
        # print(i, " -- ", article.title.strip().lower(),"---",str(seg))  # 输出标题
        if len(seg) > 0:
            jiebaTitleList.append(seg)
        i += 1

    return jiebaTitleList