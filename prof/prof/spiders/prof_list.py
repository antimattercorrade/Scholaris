import scrapy
import json
import logging
import requests
import csv
import re
import datetime

from pysummarization.nlpbase.auto_abstractor import AutoAbstractor
from pysummarization.tokenizabledoc.simple_tokenizer import SimpleTokenizer
from pysummarization.web_scraping import WebScraping
from pysummarization.abstractabledoc.std_abstractor import StdAbstractor
from pysummarization.abstractabledoc.top_n_rank_abstractor import TopNRankAbstractor




filename = "profs.json"  # To save store data
logging.getLogger('scrapy').propagate = False

prof_data_list = []


class IntroSpider(scrapy.Spider):
    name = "prof_spider"     # Name of the scraper
    def summarize(self, url):
        web_scrape = WebScraping()
        document = web_scrape.scrape(url)
        auto_abstractor = AutoAbstractor()
        auto_abstractor.tokenizable_doc = SimpleTokenizer()
        auto_abstractor.delimiter_list = [".", "\n"]
        abstractable_doc = TopNRankAbstractor()
        result_dict = auto_abstractor.summarize(document, abstractable_doc)
        
        # Output 3 summarized sentences.
        limit = 7
        i = 1
        res = ""
        for sentence in result_dict["summarize_result"]:
            res+=sentence
            if i >= limit:
                break
            i += 1
        return(res)

    def start_requests(self):
        # getting the complete list of professors from cs ranking, with their homepage urls and google scholar id's
        urls = ['http://csrankings.org/#/index?all&world.html']   
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)
        
        with open('prof.csv', mode ='r',encoding='utf8')as file: 
            csvFile = csv.reader(file)
            next(csvFile)             
            for line in csvFile:
                if(line[-1] == 'scholarid'):
                    continue
                global home_page_url 
                global scholarID  
                global Univ_Name 
                global Prof_Name 
                global summarized_home_page
                home_page_url = line[2]
                scholarID = line[-1]
                Prof_Name = line[0]
                Univ_Name = line[1]
                try:
                    summarized_home_page = self.summarize(home_page_url)
                except Exception as ex:
                    summarized_home_page = None
                print(summarized_home_page)
                google_scholar_url = f"https://scholar.google.co.in/citations?user={scholarID}&hl=en&view_op=list_works&sortby=pubdate&pagesize=100"
                yield scrapy.Request(url = google_scholar_url, callback = self.parse_google_scholar)
                
        # with open("prof.json", 'w+') as f:   # Writing data in the file
        #     for data in prof_data_list: 
        #         app_json = json.dumps(data)
        #         f.write(app_json+"\n")
    

    def parse_google_scholar(self, response):
        prof_interests = response.css('div[id="gsc_prf_int"] > a::text').extract()
        citations = response.xpath('//div[@id="gsc_rsb_cit"]/table[@id="gsc_rsb_st"]/tbody/tr[1]/td[2]/text()').extract_first()
        h_index = response.xpath('//div[@id="gsc_rsb_cit"]/table[@id="gsc_rsb_st"]/tbody/tr[2]/td[2]/text()').extract_first()
        i10_index = response.xpath('//div[@id="gsc_rsb_cit"]/table[@id="gsc_rsb_st"]/tbody/tr[3]/td[2]/text()').extract_first()
        img_src_url = response.xpath('//img[@id="gsc_prf_pup-img"]/@src').extract_first()
 
        row_number = 1
        publications = []
        while(True):
            row_sel = response.xpath(f'//div[@id="gsc_a_tw"]/table/tbody/tr[{row_number}]')
            name = row_sel.xpath(".//td/a/text()").extract_first()
            venue = row_sel.xpath(".//td/div[2]/text()").extract_first()
            year = row_sel.xpath(".//td/span/text()").extract_first()
            if(name == None or year == None or int(year)< datetime.datetime.now().year -5 ):
                break
            publications.append([name, venue, year]) 
            row_number += 1

        prof_data_list.append({"Name": Prof_Name, "University_name": Univ_Name, "H Index": h_index, "img_src": img_src_url , "Citations": citations, "I10 Index": i10_index,"Research_Interests": prof_interests, "Publications": publications, "Scholar_ID": scholarID, "home_page_url": home_page_url, "home_page_summary": summarized_home_page})
        with open("prof.json", 'a+') as f:   # Writing data in the file
            app_json = json.dumps({"Name": Prof_Name, "University_name": Univ_Name, "H Index": h_index, "img_src": img_src_url , "Citations": citations, "I10 Index": i10_index,"Research_Interests": prof_interests, "Publications": publications, "Scholar_ID": scholarID, "home_page_url": home_page_url, "home_page_summary": summarized_home_page})
            f.write(app_json+"\n")



    def parse(self, response):
        prof_csv_url = response.css('p.text-muted > a:nth-child(2)::attr(href)').extract()[-1] # accessing the titles
        prof_csv_url = prof_csv_url.replace("blob", "raw")
        # print(prof_csv_url)
        r = requests.get(prof_csv_url)
        open('./prof.csv', 'wb').write(r.content)
        

