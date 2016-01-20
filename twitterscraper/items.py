# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy import Field

class TwitterscraperItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    mongodb_id = Field()
    tweet_id = Field()
    # convo_url = Field()
    # is_retweet = Field()
    user_id = Field()
    user_screen_name = Field()
    text = Field()
    created_at = Field()
    image_url = Field()
    num_retweets = Field()
    num_favorites = Field()
    supplement = Field()
    keyword = Field()
