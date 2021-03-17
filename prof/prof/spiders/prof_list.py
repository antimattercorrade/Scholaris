import scrapy
import json
import logging
import requests
import csv
import re
import datetime


filename = "profs.json"  # To save store data
logging.getLogger('scrapy').propagate = False

prof_data_list = []


class IntroSpider(scrapy.Spider):
    name = "prof_spider"     # Name of the scraper
    
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
                home_page_url = line[2] 
                global scholarID  
                global Univ_Name 
                global Prof_Name 
                scholarID = line[-1]
                Prof_Name = line[0]
                Univ_Name = line[1]
                google_scholar_url = f"https://scholar.google.co.in/citations?user={scholarID}&hl=en&view_op=list_works&sortby=pubdate&pagesize=100"
                yield scrapy.Request(url = google_scholar_url, callback = self.parse_google_scholar)
                # print(data)
                # yield scrapy.Request(url = home_page_url, callback = self.parse_homepage)
                # prof_data_list.append({"Name": line[0], "University_name": line[1], "Research_Interests": [], "Publications": [], "Scholar_ID": line[-1]})
        with open("prof.json", 'w+') as f:   # Writing data in the file
            for data in prof_data_list: 
                app_json = json.dumps(data)
                f.write(app_json+"\n")
    

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

        prof_data_list.append({"Name": Prof_Name, "University_name": Univ_Name, "H Index": h_index, "img_src": img_src_url , "Citations": citations, "I10 Index": i10_index,"Research_Interests": prof_interests, "Publications": publications, "Scholar_ID": scholarID})
        

    
    def parse_homepage(self,response):
        print("aagaya")


    def parse(self, response):
        prof_csv_url = response.css('p.text-muted > a:nth-child(2)::attr(href)').extract()[-1] # accessing the titles
        prof_csv_url = prof_csv_url.replace("blob", "raw")
        # print(prof_csv_url)
        r = requests.get(prof_csv_url)
        open('./prof.csv', 'wb').write(r.content)
        

