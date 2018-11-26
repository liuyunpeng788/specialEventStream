
'''
  处理es 相关
'''
#!/usr/bin/python3
#coding:utf-8
import sys
sys.path.append("..")
from elasticsearch import Elasticsearch

from utils.time_util import removeIllegalChar, normalReleaseTime, getDefaultTimeRange

'''
获取连接
'''
def getESConnect():
 return Elasticsearch(
    ['fonova-hadoop2:9204'],
     sniff_on_start=True,
     sniff_on_connection_fail=True,
     sniffer_timeout=60
 )

'''
获取根据时间进行rang类型的模板
'''
def getTempletReleaseTimeRange(queryDic={}):
    if queryDic is None :
        print("param is none")
        return
    query={"source":{
        "query":{
            "range": {
                "releaseTime": {
                    "gt": "{{start}}",
                    "lte": "{{end}}"
                }
            }
        }
    } ,
        "params":{
                "start": queryDic['start'],
                "end": queryDic['end']
        }
           }
    return query





if __name__=="__main__":
    es = getESConnect()

    values = {}
    values["id"] = "b52d1db0921a96377278e9f75d3f3791"
    # query = {"query": {"term": {"id": "66bfa510ca9bd7e6234b8cba9e3bc077"}}}
    query = {"query": {
        "range": {
            "releaseTime": {
                "gt": "2018-05-29T02:00:00.000+08:00",
                "lte": "2018-05-29T08:00:00.000+08:00"
            }
        }
    }}
    res = es.search(index="new_article_uc-test", doc_type="article_uc", body=query)

    # 采用模板查询
    values['start']='2018-05-29T02:00:00.000+08:00'
    values['end'] = '2018-05-29T20:00:00.000+08:00'

    defaultTimeRange = getDefaultTimeRange() # 获取默认的时间范围

    values['start'] = defaultTimeRange[0] if values['start'] is None else values['start']
    values['end'] = defaultTimeRange[1] if values['end'] is None else values['end']

    res = es.search_template(index="new_article_uc-test", doc_type="article_uc", body=getTempletReleaseTimeRange(values))
    for result in res['hits']['hits']:
        source = result['_source']
        releaseTime = normalReleaseTime(source['releaseTime'])
        title = removeIllegalChar(source['title'])
        text = removeIllegalChar(source['text'])
        print(title + " -- " + releaseTime + " ---" + text)

