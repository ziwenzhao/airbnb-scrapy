# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class AirbnbScrapeItem(scrapy.Item):
    # define the fields for your item here like:
    home_type = scrapy.Field()
    description = scrapy.Field()
    room = scrapy.Field()
    amenity = scrapy.Field()
    rating = scrapy.Field()
    review_count = scrapy.Field()
    price = scrapy.Field()
    is_new = scrapy.Field()
    is_superhost = scrapy.Field()
    image = scrapy.Field()
    detail_page = scrapy.Field()
    
