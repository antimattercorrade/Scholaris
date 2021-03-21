# from Prof import query_script
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from inspect import getsourcefile
import os.path
import sys
import pathlib

p = pathlib.Path(os.getcwd())
path = str(p.parents[1])+"/Prof/"
sys.path.append(path)

from .Prof.query_script import query_result 

def home(request):
    return render(request,"index.html")

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
            actual.append(i[0])
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
            if(search_result[i*3+j]["University_name"] == None):
                search_result[i*3+j]["University_name"] = "NA"
            temp.append(prof(i*3+j,search_result[i*3+j]["Name"], search_result[i*3+j]["img_src"],search_result[i*3+j]["University_name"][:30],", ".join(search_result[i*3+j]["Research_Interests"][:3])[:80],search_result[i*3+j]["H Index"],search_result[i*3+j]["I10 Index"],len(search_result[i*3+j]["Publications"]),search_result[i*3+j]["home_page_url"],search_result[i*3+j]["home_page_summary"],search_result[i*3+j]["Publications"]))
            
        array.append(temp)
    # print(time.time()-x)
    noResults = []
    if len(array[0])==0:
        noResults = [1]
    return render(request, "search.html",{"array":array,"placeholder":query,"noResults":noResults})