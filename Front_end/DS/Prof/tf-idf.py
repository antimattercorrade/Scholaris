import re
import json
import pickle
import math

# Clean string function
def clean_string(text) :
	text = (text.encode('ascii', 'ignore')).decode("utf-8")
	text = re.sub("&.*?;", "", text)
	text = re.sub(">", "", text)    
	text = re.sub("[\]\|\[\@\,\$\%\*\&\\\(\)\":]", "", text)
	text = re.sub("-", " ", text)
	text = re.sub("\.+", "", text)
	text = re.sub("^\s+","" ,text)
	text = text.lower()
	return text

def indexing():
	df_data={}
	tf_data={}
	idf_data={}
	tf_idf = {}
	output_file_name = "index_file"
	input_file_name = "prof.json"

	prof_data_list = open(input_file_name).read().split("\n")
	stopwords = open("./stopword.txt").read().split("\n")

	prof_data = []
	for row in prof_data_list:
		try:
			prof_data.append(json.loads(row))
		except:
			continue

	for row in prof_data:
		tf={} 
		#clean and list word
		for data in row['Name'].split():
			clean_name = clean_string(data)
			if clean_name in stopwords:
				continue
			if clean_name in tf :
				tf[clean_name] += 1
			else :
				tf[clean_name] = 1

			#df whole document frequency
			if clean_name in df_data :
				df_data[clean_name] += 1
			else :
				df_data[clean_name] = 1

		for data in row['Publications']:
			clean_publications = clean_string(data[0])
			list_word = clean_publications.split(" ")		
			for word in list_word :
				if word in stopwords:
					continue
				#tf row frequency
				if word in tf :
					tf[word] += 1
				else :
					tf[word] = 1

				#df whole document frequency
				if word in df_data :
					df_data[word] += 1
				else :
					df_data[word] = 1

		for data in row['Research_Interests']:
			clean_interests = clean_string(data)
			list_word = clean_interests.split(" ")
			for word in list_word:
				if word in tf:
					tf[word] +=1
				else:
					tf[word] = 1
				# can also add weightage to the interest 
				if word in df_data :
					df_data[word] += 1
				else :
					df_data[word] = 1

		tf_data[row['Scholar_ID']] = tf

	# Calculate Idf
	for row in df_data :
		idf_data[row] = 1 + math.log10(len(tf_data)/df_data[row])

	for word in df_data:
		list_doc = []
		for data in prof_data:
			tf_value = 0
			if word in tf_data[data['Scholar_ID']] :
				tf_value = tf_data[data['Scholar_ID']][word]
				
			weight = tf_value * idf_data[word]

			doc = {
				'Scholar_ID' : data['Scholar_ID'],
				'Name' : data['Name'],
				'img_src' : data['img_src'],
				'H Index' : data['H Index'],
				'Citations' : data['Citations'],
				'I10 Index' : data['I10 Index'],
				'Publications' : data['Publications'],
				'home_page_url' : data['home_page_url'],
				'Research_Interests' : data['Research_Interests'],
				'University_name' : data['University_name'],
				'home_page_summary' : data['home_page_summary'],
				'score' : weight
			}


			if doc['score'] != 0 :
				list_doc.append(doc)	
			
		tf_idf[word] = list_doc

	with open(output_file_name, 'wb') as file:
		pickle.dump(tf_idf, file)

if(__name__ == '__main__'):
	indexing()