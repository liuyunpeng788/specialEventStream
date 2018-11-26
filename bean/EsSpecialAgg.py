import sys

sys.path.append("..")
'''
ES专项聚类信息
'''


class EsSpecialAgg:
    def __init__(self, id, specialId, topicId, first_media, media_num, article_num, negatice_num, release_time,
                 topicDesc='',phrase=''):
        self.id = id
        self.specialId = specialId
        self.topicId = topicId
        self.first_media = first_media
        self.media_num = media_num
        self.article_num = article_num
        self.negatice_num = negatice_num
        self.release_time = release_time
        self.topicDesc = topicDesc
        self.phrase = phrase

    def updatePhrase(self,phrase):
        self.phrase = phrase
