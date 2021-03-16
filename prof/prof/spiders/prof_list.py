import scrapy
import json
import logging
import requests
import csv

filename = "profs.json"  # To save store data
logging.getLogger('scrapy').propagate = False

class IntroSpider(scrapy.Spider):
    name = "prof_spider"     # Name of the scraper

    def start_requests(self):
        urls = ['http://csrankings.org/#/index?all&world.html']   
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)
        
        with open('prof.csv', mode ='r',encoding='utf8')as file: 
            csvFile = csv.reader(file)
            next(csvFile) 
            prof_data_list = []
            for lines in csvFile:
                if(lines[-1] == 'scholarid'):
                    continue
                # print("before call back")
                yield scrapy.Request(url = lines[2])
                print(response.text)
                prof_data_list.append({"Name": lines[0], "University_name": lines[1], "Research_Interests": [], "Publications": [], "Scholar_ID": lines[-1]})

    
    def parse_homepage(self,response):
        print("aagaya")
        print(response.text)

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
