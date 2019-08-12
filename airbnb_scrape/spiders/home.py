# -*- coding: utf-8 -*-
import scrapy
import re
import time
from selenium import webdriver
from scrapy.selector import Selector
from selenium.webdriver.chrome.options import Options
from airbnb_scrape.items import AirbnbScrapeItem

class HomeSpider(scrapy.Spider):
    name = 'home'
    allowed_domains = ['www.airbnb.ca']
    start_urls = ['http://www.airbnb.ca']
    results = []

    def get_rating(self, home_selector):
        rating = home_selector.xpath('.//div[@class="_tghtxy2"]/text()').get()
        if rating is not None:
            return float(rating)
        rating = home_selector.xpath('.//span[@class="_rs3rozr"]/@aria-label').get()
        if rating is not None:
            return rating.split()[1]
        return None

    def get_review_count(self, home_selector):
        review_count = home_selector.xpath('.//div[@class="_10qgzd5i"]/following-sibling::span[@class="_krjbj"]/text()').get()
        if review_count is not None:
            return int(review_count.split()[0])
        review_count = home_selector.xpath('.//span[@class="_q27mtmr"]/following-sibling::span[@class="_krjbj"]/text()').get()
        if review_count is not None:
            return int(review_count.split()[0])
        return None
    
    
    def extractData(self):
        self.scrapy_selector = Selector(text = self.driver.page_source)
        home_selectors = self.scrapy_selector.xpath('//div[@class="_fhph4u"]/div[@class="_8ssblpx"]')
        for home_selector in home_selectors:
            home_type = home_selector.xpath('.//span[@class="_1xxanas2"]/span/text()').get()
            description = home_selector.xpath('.//div[@class="_1dss1omb"]/text()').get()
            room = u'\u00B7'.join(home_selector.xpath('.//div[@class="_1jlnvra2"]/div/text()').getall())
            amenity = u'\u00B7'.join(home_selector.xpath('.//div[@class="_1jlnvra2"]/text()').getall())
            rating = self.get_rating(home_selector)
            review_count = self.get_review_count(home_selector)
            print('get review count')
            print(review_count)
            price = re.search(r'\d+', home_selector.xpath('.//span[@class="_1p3joamp"]/span[@class="_krjbj"]/following-sibling::text()').get()).group()
            is_new = True if home_selector.xpath('.//span[@class="_1p2weln"][contains(., "NEW")]').get() is not None else False
            is_superhost = True if home_selectors[7].xpath('.//span[@class="_1plk0jz1"][contains(., "Superhost")]').get() is not None else False
                
            
            home_item = AirbnbScrapeItem(home_type = home_type, description = description, room = room, amenity = amenity, rating = rating, review_count = review_count, price = price, is_new = is_new, is_superhost = is_superhost)
            print('home_item is')
            print(home_item)

    def close_driver(self):
##	self.driver.close()
        pass



    def start_request_with_selenium(self):
	header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'}
	options = Options()
	options.add_argument("--disable-notifications")
	options.add_argument("--incognito")
	options.add_argument("--disable-extensions")
	options.add_argument(" --disable-gpu")
	options.add_argument(" --disable-infobars")
	options.add_argument(" -–disable-web-security")
	options.add_argument("--no-sandbox") 		
	caps = options.to_capabilities()
	self.driver = webdriver.Chrome('/Users/ziwenzhao/Desktop/chromedriver', desired_capabilities=caps)
	self.driver.get('https://www.airbnb.ca/s/Montreal--QC/homes?refinement_paths%5B%5D=%2Fhomes&place_id=ChIJDbdkHFQayUwR7-8fITgxTmU&query=Montreal%2C%20QC&search_type=filter_change&s_tag=KhBNmEQ3&checkin=2019-08-15&checkout=2019-08-22&adults=1&room_types%5B%5D=Entire%20home%2Fapt')

    def parse(self, response):
    	self.start_request_with_selenium()
    	self.extractData()
    	self.close_driver()

	

	
