import sys
import json
import pickle

if len(sys.argv) != 3 :
	print ("\n\python3\n\tquery.py [number of results] [query]..\n")
	sys.exit(1)

query = sys.argv[3].split(" ")
n = int(sys.argv[2])

with open("index_file", 'rb') as indexdb:
    indexFile = pickle.load(indexdb)

list_doc = {}
for q in query:
	q = q.lower()
	try:
		for doc in indexFile[q]:
			if doc['Scholar_ID'] in list_doc :
				list_doc[doc['Scholar_ID']]['score'] += doc['score']
			else :
				list_doc[doc['Scholar_ID']] = doc
	except:
		continue

list_data=[]
for data in list_doc :
	list_data.append(list_doc[data])

count = 1
for data in sorted(list_data, key=lambda k: k['score'], reverse=True):
	y = json.dumps(data)
	print(y)
	if (count == n) :
		break
	count+=1