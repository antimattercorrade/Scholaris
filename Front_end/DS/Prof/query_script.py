import pickle


def query_result(n, query):

	with open("./DS/Prof/index_file", 'rb') as indexdb:
		indexFile = pickle.load(indexdb)

	list_doc = {}
	query = list(query.split(" "))
	for q in query:
		q = q.lower()
		if(q == ''):
			continue
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
	res = []
	for data in sorted(list_data, key=lambda k: k['score'], reverse=True):
		res.append(data)
		if (count == n) :
			break
		count+=1
	return res

	