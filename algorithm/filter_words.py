import pymongo

client = pymongo.MongoClient('10.151.2.101', 27017)
db = client.Algorithm
db.authenticate('algorithm_users', '123456', mechanism='SCRAM-SHA-1')

coll = db.dic_filterword

with open('filter_word.txt','w') as f:
	for item in coll.find():
		f.write(item['name'].strip() + '\n')
