# -*- coding:utf-8 -*-
import sys
sys.path.append("..")
from pyhanlp import *

'''
词典维护
'''
# 读取用户词典
CustomDictionary = JClass("com.hankcs.hanlp.dictionary.CustomDictionary")

# 加新词进词典
def add_new_word(file,CustomDictionary):
    with open(file,'r') as f:
        for line in f.readlines():
            CustomDictionary.insert(line.strip(), "nz 1024")

# 删掉原来的词
def del_dict_word(file,CustomDictionary):
    with open(file,'r') as f:
        for line in f.readlines():
            CustomDictionary.remove(line.strip())

# 运行删改词库
add_new_word('../algorithm/add_new_word.txt',CustomDictionary)
del_dict_word('../algorithm/del_dict_word.txt',CustomDictionary)

'''
停用词
'''
def get_stop_words():

    stop_word_file = '../algorithm/stop_word.txt'
    filter_word_file = '../algorithm/filter_word.txt'
    stop_words_list = set()

    with open(stop_word_file, 'r',encoding='utf-8') as f:
        content = f.readlines()
        for line in content:
            if line.strip():
                stop_words_list.add(line.strip())

    with open(filter_word_file, 'r',encoding='utf-8') as f:
        content = f.readlines()
        for line in content :
            if line.strip():
                stop_words_list.add(line.strip())

    return stop_words_list

# 运行生成stopwords
keywords = get_stop_words()

'''
分词
'''
# 词典分词
def segment(s):
    return [item.word for item in HanLP.segment(s) if item.word not in keywords]

# 找名词动词
def find_verb_noun(text):
    tmp = []
    for term in HanLP.segment(text):

        if term.word in keywords:
            continue

        if (str(term.nature)[0] == 'n' or str(term.nature)[0] == 'v'):
            tmp.append(term.word)

    return list(set(tmp))

# 找动词名词+过滤掉单字
def nv_segment(text):
    tmp = []
    for term in HanLP.segment(text):

        if term.word in keywords:
            continue

        if len(term.word) == 1:
            continue

        if (str(term.nature)[0] == 'n' or str(term.nature)[0] == 'v'):
            tmp.append(term.word)

    return list(set(tmp))

