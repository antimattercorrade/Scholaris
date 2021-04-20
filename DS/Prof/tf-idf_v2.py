import re
import json
import pickle
import math
from collections import Counter

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
			indoc = 1
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
					df_data[word] += indoc
					indoc = 0
				else :
					df_data[word] = indoc
					indoc = 0


		for data in row['Research_Interests']:
			clean_interests = clean_string(data)
			list_word = clean_interests.split(" ")
			indoc = 1
			for word in list_word:
				if word in stopwords:
					continue
				if word in tf:
					tf[word] +=1
				else:
					tf[word] = 1
				# can also add weightage to the interest 
				if word in df_data :
					df_data[word] += indoc
					indoc = 0
				else :
					df_data[word] = indoc
					indoc = 0
		for word in tf:
			tf[word] = tf[word]/len(tf)     # tf(word,doc) = frequency of word in doc / total no of words in doc 

		tf_data[row['Scholar_ID']] = tf

	

		

	# Calculate Idf
	for word in df_data :
		if(df_data[word]):
			idf_data[word] = math.log(len(tf_data)/df_data[word])  #ln(No of docs/ No of docs  containing word) = idf[word];  0 otherwise
		else :
			idf_data[word] = 0 


    # relevance for each doc (final score) idf(word,doc) = tf(word,doc) * idf(word)
    #i.e. for each word in tf_data[row['Scholar_ID']] * idf[same word]
	for word in df_data:
		list_doc = []
		for row in prof_data:
			tf_value = 0
			if word in tf_data[row['Scholar_ID']] :
				tf_value = tf_data[row['Scholar_ID']][word]
				
			weight = tf_value * idf_data[word]

			doc = {
				'Scholar_ID' : row['Scholar_ID'],
				'Name' : row['Name'],
				'img_src' : row['img_src'],
				'H Index' : row['H Index'],
				'Citations' : row['Citations'],
				'I10 Index' : row['I10 Index'],
				'Publications' : row['Publications'],
				'home_page_url' : row['home_page_url'],
				'Research_Interests' : row['Research_Interests'],
				'University_name' : row['University_name'],
				'home_page_summary' : row['home_page_summary'],
				'score' : weight
			}


			if doc['score'] != 0 :
				list_doc.append(doc)	
			
		tf_idf[word] = list_doc

	with open(output_file_name, 'wb') as file:
		pickle.dump(tf_idf, file)

if(__name__ == '__main__'):
	indexing()