# -*- coding: utf-8 -*-
import scrapy
import re
from time import sleep
from selenium import webdriver
from scrapy.selector import Selector
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from airbnb_scrape.items import AirbnbScrapeItem
from selenium.webdriver.support import expected_conditions as EC
from contextlib import contextmanager

class HomeSpider(scrapy.Spider):
    name = 'home'
    allowed_domains = ['www.airbnb.ca']
    start_urls = ['http://www.airbnb.ca']

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

    def get_image(self, home_selector):
            style_text = home_selector.xpath('.//div[@class="_1i2fr3fi"]/@style').get()
            background_image_text = re.search(r'background-image.*?url\(.*?\)', style_text).group()
            begin = background_image_text.find('(') + 2
            end = background_image_text.find(')') - 2
            image_url = background_image_text[begin: end + 1]
            return image_url
    
##    This method scrapes all the images of a home. However, the time consumption is intolerable. Therefore it can only fetch the only image in the original html
##    def get_images(self, index):
##        def get_current_image():
##            self.scrapy_selector = Selector(text = self.driver.page_source)
##            style_text = self.scrapy_selector.xpath('//div[@class="_1i2fr3fi"]/@style')[index].get()
##            background_image_text = re.search(r'background-image.*?url\(.*?\)', style_text).group()
##            begin = background_image_text.find('(') + 2
##            end = background_image_text.find(')') - 2
##            image_url = background_image_text[begin: end + 1]
##            return image_url
##        
##        def scroll_and_move_to_next_button():
##            home_element = self.driver.find_elements_by_xpath('//div[@class="_8ssblpx"]')[index]
##            self.driver.execute_script('window.scroll(arguments[0], arguments[1])', home_element.location['x'], home_element.location['y'] - home_element.size['height'] / 2)
##            next_button = self.driver.find_elements_by_xpath('//div[@class="_tk908t"]/button[2]')[index]
##            ActionChains(self.driver).move_to_element(next_button).perform()
##            return next_button
##
##        images = []
##        images.append(get_current_image())
##        next_button = scroll_and_move_to_next_button()
##        wait = WebDriverWait(self.driver, 10)
##        wait.until(EC.presence_of_element_located((By.XPATH, '(//div[@class="_8ssblpx"])['+ str(index + 1) + ']//button[@class="_1rftspj9"]')))
##        while True:
##            next_button.click()
##            wait.until(EC.invisibility_of_element_located((By.XPATH, '(//div[@class="_8ssblpx"])['+ str(index + 1) + ']//div[@class="_1na7kj9b"][2]')))
##            image_url = get_current_image()
##            if image_url == images[0]:
##                break
##            else:
##                images.append(image_url)
##        return images




    def close_driver(self):
	self.driver.close()
	self.logger.info('webdriver closed')


    def close_cookie_notice(self):
        try:
            self.driver.find_element_by_xpath('//button[@title="OK"]').click()
        except Exception as e:
            self.logger.error('close cookie notice error' + str(e))


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
	self.driver = webdriver.Chrome('./chromedriver', desired_capabilities=caps)
	self.driver.get(self.url)
        self.logger.info('started request to')

    def parse(self, response):
        page_number = 1
    	self.start_request_with_selenium()
    	self.close_cookie_notice()
           
        while True:
            self.logger.info('start scraping page ' + str(page_number))
            self.scrapy_selector = Selector(text = self.driver.page_source)
            home_selectors = self.scrapy_selector.xpath('//div[@class="_fhph4u"]/div[@class="_8ssblpx"]')
            for index, home_selector in enumerate(home_selectors):
                home_type = home_selector.xpath('.//span[@class="_1xxanas2"]/span/text()').get()
                description = home_selector.xpath('.//div[@class="_1dss1omb"]/text()').get()
                room = u'\u00B7'.join(home_selector.xpath('.//div[@class="_1jlnvra2"]/div/text()').getall())
                amenity = u'\u00B7'.join(home_selector.xpath('.//div[@class="_1jlnvra2"]/text()').getall())
                rating = self.get_rating(home_selector)
                review_count = self.get_review_count(home_selector)
                price = re.search(r'\d+', home_selector.xpath('.//span[@class="_1p3joamp"]/span[@class="_krjbj"]/following-sibling::text()').get()).group()
                is_new = True if home_selector.xpath('.//span[@class="_1p2weln"][contains(., "NEW")]').get() is not None else False
                is_superhost = True if home_selector.xpath('.//span[@class="_1plk0jz1"][contains(., "Superhost")]').get() is not None else False
                image = self.get_image(home_selector)
                detail_page = self.driver.find_element_by_xpath('(//div[@class="_8ssblpx"])[' + str(index + 1) +']//a').get_attribute('href')
                home_item = AirbnbScrapeItem(home_type = home_type, description = description, room = room, amenity = amenity, rating = rating, review_count = review_count,\
                                             price = price, is_new = is_new, is_superhost = is_superhost, image = image, detail_page = detail_page)
                self.logger.debug('scrape a home item ' + str(home_item))
                yield home_item
            self.logger.info('finish scraping page ' + str(page_number))
            try:
                self.driver.get(self.driver.find_element_by_xpath('//li[not(@data-id)][@class="_r4n1gzb"]/a').get_attribute('href'))
                self.logger.info('navigated to next page')
                page_number += 1
            except Exception as e:
                self.logger.debug('check next button')
                sel = Selector(text=self.driver.page_source)
                self.logger.debug(sel.xpath('//ul[@class="_11hau3k"]/li[last()]').get())
                self.logger.error('navigate to next page fail' + str(e))
                break
    	
    	self.close_driver()

	

	
