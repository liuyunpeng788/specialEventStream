
import jieba
from jpype import JClass
from pyhanlp import SafeJClass
from pyhanlp import HanLP

if __name__ == '__main__':
    str1= '进博会大数据:单日超600000人逛展小黄豆能签20000000美元订单'
    str2 = '进博会大数据：单日超60万人逛展小黄豆签2千万美元'
    print("str1:" ,str1)
    print("str2:",str2)

    cuts1 = jieba.cut(str1)
    cuts2 = jieba.cut(str2)
    print("cuts1 cut:", ",".join(cuts1))
    print("cuts2 cut:", ",".join(cuts2))

    cuts3 = jieba.cut(str1,cut_all=True)
    cuts4 = jieba.cut(str2,cut_all=True)
    print("cuts3 cut_all:", ",".join(cuts3))
    print("cuts4 cut_all:", ",".join(cuts4))

    import jieba.analyse

    cuts5 = jieba.analyse.extract_tags(str1,allowPOS=('n','v','ns'))
    cuts6 = jieba.analyse.extract_tags(str2,allowPOS=('n','v','ns'))
    print("cuts5 extract_tags:", ",".join(cuts5))
    print("cuts6 extract_tags:", ",".join(cuts6))

    cuts7 = jieba.analyse.textrank(str1, allowPOS=('n', 'v', 'ns'))
    cuts8 = jieba.analyse.textrank(str2, allowPOS=('n', 'v', 'ns'))
    print("cuts7 textrank:", ",".join(cuts7))
    print("cuts8 textrank:", ",".join(cuts8))

    print('hanlp now...')
    word = SafeJClass('com.hankcs.hanlp.corpus.dependency.CoNll.CoNLLWord')
    coNLLSentence = SafeJClass('com.hankcs.hanlp.corpus.dependency.CoNll.CoNLLSentence')
    CustomDictionary = JClass("com.hankcs.hanlp.dictionary.CustomDictionary")
    hanres = HanLP.segment(str1)
    print(hanres)





