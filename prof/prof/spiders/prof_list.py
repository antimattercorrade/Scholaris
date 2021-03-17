import scrapy
import json
import logging
import requests
import csv
import re
import datetime
from scrapy_selenium import SeleniumRequest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

# from selenium import webdriver

# driver = webdriver.Chrome(executable_path="../../chromedriver")

filename = "profs.json"  # To save store data
logging.getLogger('scrapy').propagate = False

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
            prof_data_list = []            
            for line in csvFile:
                if(line[-1] == 'scholarid'):
                    continue
                home_page_url = line[2] 
                scholarID = line[-1] 
                google_scholar_url = f"https://scholar.google.co.in/citations?user=plJC8R0AAAAJ&hl=en&view_op=list_works&sortby=pubdate"
                # data = yield scrapy.Request(url = google_scholar_url, callback = self.parse_google_scholar)
                yield SeleniumRequest( 
                    url =google_scholar_url, 
                    wait_time = 3, 
                    screenshot = False, 
                    callback = self.parse_google_scholar,  
                    wait_until= EC.element_to_be_clickable((By.ID, 'gsc_bpf_more'))
                )
                break
                # yield scrapy.Request(url = home_page_url, callback = self.parse_homepage)
                prof_data_list.append({"Name": line[0], "University_name": line[1], "Research_Interests": [], "Publications": [], "Scholar_ID": line[-1]})

    

    def parse_google_scholar(self, response):
        prof_interests = response.css('div[id="gsc_prf_int"] > a::text').extract()
        row_number = 1
        while(True):
            row_sel = response.xpath(f'//div[@id="gsc_a_tw"]/table/tbody/tr[{row_number}]')
            name = row_sel.xpath(".//td/a/text()").extract_first()
            venue = row_sel.xpath(".//td/div[2]/text()").extract_first()
            year = row_sel.xpath(".//td/span/text()").extract_first()
            if(int(year)< datetime.datetime.now().year -5 ):
                flag = False
                break
            # print([name,venue,year])
            if response.xpath("//button[@class='gs_btnPR gs_in_ib gs_btn_half gs_btn_lsb gs_btn_srt gsc_pgn_pnx']/@onclick").extract_first() != "" and row_number%20 == 0:
                print("more entries")
                # response.xpath("//button[@id='gsc_bpf_more']/@onclick").extract_first().replace("\\x3d","=").replace("\\x26","?")
            row_number += 1


                
			# link = prof_sel.xpath(".//table/tbody").extract_first()
			# url = response.urljoin(link)
			# yield scrapy.Request(url,callback=self.parse_url_to_crawl)
		
		
        # prof_publications_name = response.xpath('//div[@id="gsc_a_tw"]/table/tbody/tr/td:nth-child(1)/a/text()').get()
        # prof_publications_year = response.xpath('//div[@id="gsc_a_tw"]/table/tbody/tr/td:nth-child(3)/span/text()').get()
        
        # prof_publications_name = response.css('div[id="gsc_a_tw"] > table > tbody > tr > td:nth-child(1) > a::text').extract()
        # prof_publications_venue = response.css('div[id="gsc_a_tw"] > table > tbody > tr > td:nth-child(1) > div:nth-child(3)::text').extract()
        # prof_publications_year = response.css('div[id="gsc_a_tw"] > table > tbody > tr > td:nth-child(3) > span::text').extract()
        
        # n = len(prof_publications_year) 
        # for i in range(n):
        #     if(int(prof_publications_year[i]) >=  datetime.datetime.now().year -5):
        #         print([prof_publications_name[i],prof_publications_year[i]])


        # for publication in prof_publications_name:
        #     print(publication)
        #     break
        # print(prof_publications)
        # return prof_interests
        # print(prof_interests)
    
    def parse_homepage(self,response):
        print("aagaya")
        # if re.search("Neuroscience",response.text):
        #     print("Neuroscience")
        
        # print(response.text)

    def parse(self, response):
        list_data=[]
        prof_csv_url = response.css('p.text-muted > a:nth-child(2)::attr(href)').extract()[-1] # accessing the titles
        prof_csv_url = prof_csv_url.replace("blob", "raw")
        # print(prof_csv_url)
        r = requests.get(prof_csv_url)
        open('./prof.csv', 'wb').write(r.content)

        
        


        # i=0
        # for book_title in book_list:
        #     data={
        #         'book_title' : book_title,
        #         'price' : price_list[i],
        #         'image-url' : image_link[i],
        #         'url' : link_list[i]
        #     }
        #     i+=1
        #     list_data.append(data)
            
        # with open(filename, 'a+') as f:   # Writing data in the file
        #     for data in list_data : 
        #         app_json = json.dumps(data)
        #         f.write(app_json+"\n")
# IntroSpider.fetch_data()
