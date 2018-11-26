import sys
sys.path.append("..")

class EsSpecialInfos:
    def __init__(self,id,specialId,topicId,topicDesc,sysId,release_time,emotion=0,site=''):
        self.id = id
        self.specialId = specialId
        self.topicId = topicId
        self.topicDesc = topicDesc
        self.sysId = sysId
        self.release_time = release_time
        self.emotion = emotion
        self.site = site
