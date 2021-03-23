from django.http.response import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import regex as re

def compare_research(a,b):
    if( a["score_research"]  == b["score_research"]):
        return a["H Index"] > b["H Index"]
    return a["score_research"] > b["score_research"]

import pickle

indexFile = pickle.load(open("./DS/Prof/index_file", 'rb'))

choice = "default"

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

def query_result(n, query):

    list_doc = {}

    if( choice != "Interests"):
        query = list(query.split(" "))
        for q in query:
            q = q.lower()
            if(q == '' or q not in indexFile):
                continue
            for doc in indexFile[q]:
                if doc['Scholar_ID'] in list_doc:
                    list_doc[doc['Scholar_ID']]['score'] += doc['score']

                    if(doc['score_name'] != -1):
                        list_doc[doc['Scholar_ID']]['score_name'] += doc['score_name']
                    if(doc['score_univ'] != -1):
                        list_doc[doc['Scholar_ID']]['score_univ'] += doc['score_univ']
                    # if(doc['score_research'] != -1):
                    #     list_doc[doc['Scholar_ID']]['score_research'] += doc['score_research']
                else :
                    scholar_id = doc['Scholar_ID']
                    list_doc[scholar_id] = doc.copy()
    else :
        query = query.lower()
        query = clean_string(query)
        # print(query)
        if(query in indexFile):
            for doc in indexFile[query]:
                if(doc['Scholar_ID'] in list_doc and doc['score_research'] != -1):
                    list_doc[doc['Scholar_ID']]['score_research'] += doc['score_research']
        


    list_data=[]
    
    for data in list_doc:
        list_data.append(list_doc[data])
        


    count = 1
    res = []

    if (choice == 'prof_name'):
        for data in sorted(list_data, key=lambda k: (k['score_name'],float(k['H Index'])), reverse=True):
            if(data['score_name'] == -1):
                continue
            res.append(data)
            if (count == n) :
                break
            count+=1

    elif (choice == 'university_name'):
        for data in sorted(list_data, key=lambda k: (k['score_univ'],float(k['H Index'])), reverse=True):
            if(data['score_univ'] == -1):
                continue
            res.append(data)
            if (count == n) :
                break
            count+=1

    elif(choice == 'Interests'):

        for data in sorted(list_data, key=lambda k: ((k['score_research']),float(k['H Index'])), reverse=True):
            if(data['score_research'] == -1):
                continue
            # print(data['H Index'],data['score_research'],data['Name'])
            res.append(data)
            if (count == n) :
                break
            count+=1

    elif(choice == 'default'):
        for data in sorted(list_data, key=lambda k: (k['score'],float(k['H Index'])), reverse=True):
            # print(data['score'], data['Name'])
            res.append(data)
            if (count == n) :
                break
            count+=1

    return res

def home(request):
    return render(request,"index.html")

class publication:
    def __init__(self,content,link,year):
        self.content = content
        self.link = link
        self.year = year

class prof:
    def __init__(self,id,name,imageURL,institute,interests,hIndex,i10Index,publications,homepage,homepage_summary,acPublications):
        self.id = id
        self.name = name
        self.imageURL = imageURL
        self.institute = institute
        self.interests = interests
        self.hIndex = hIndex
        self.i10Index = i10Index 
        self.publications = publications
        self.homepage = homepage
        self.summary = homepage_summary
        if homepage_summary==None:
            self.summary = "Summary Not Available!"
        actual = []
        for i in acPublications:
            actual.append(publication(i[0],i[1],i[2]))
        # pub = ""
        # for i in actual:
        #     pub += "<p>"+i+"</p><br>"
        self.acPublications = actual


import time
@csrf_exempt
def home_search(request):
    query = request.POST["search"]
    results_required = 25
    x = time.time()
    search_result = query_result(results_required,query)
    array = []
    result_size = len(search_result)
    for i in range(result_size//3+1):
        temp = []
        for j in range(3):
            if(i*3 + j >= result_size):
                break
            if(search_result[i*3+j]["University_name"] == None or search_result[i*3+j]["University_name"] == 'Homepage'):
                search_result[i*3+j]["University_name"] = "NA"
            temp.append(prof(i*3+j,search_result[i*3+j]["Name"], search_result[i*3+j]["img_src"],search_result[i*3+j]["University_name"][:30],", ".join(search_result[i*3+j]["Research_Interests"][:3])[:80],search_result[i*3+j]["H Index"],search_result[i*3+j]["I10 Index"],len(search_result[i*3+j]["Publications"]),search_result[i*3+j]["home_page_url"],search_result[i*3+j]["home_page_summary"],search_result[i*3+j]["Publications"]))
            
        array.append(temp)
    # print(time.time()-x)
    noResults = []
    if len(array[0])==0:
        noResults = [1]
    return render(request, "search.html",{"array":array,"placeholder":query,"noResults":noResults})


@csrf_exempt
def pref(request):
    # print(request.body.decode())
    global choice 
    if(request.body.decode() == 'prof_name'):
        choice = 'prof_name'
    elif(request.body.decode() == 'Interests'):
        choice = 'Interests'
    elif(request.body.decode() == 'university_name'):
        choice = 'university_name'
    else:
        choice = 'default'
    return JsonResponse({1:"done"})