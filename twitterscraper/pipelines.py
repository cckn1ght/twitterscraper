# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from IPython.core.debugger import Tracer
import sys
import datetime
import traceback
import pymongo

from scrapy.exceptions import DropItem
from scrapy import settings
from scrapy import log

class MongoDBPipeline(object):
    def __init__(self):
        self.MONGODB_SERVER = "localhost"
        self.MONGODB_PORT = 27017
        self.MONGODB_DB = "tweets"


    @classmethod
    def from_crawler(cls, crawler):
        # return cls(
        #         MONGODB_SERVER=crawler.settings.get('MONGODB_SERVER', 'localhost')
        #         MONGODB_PORT=crawler.settings.get('MONGODB_PORT', 27017)
        #         MONGODB_DB=crawler.settings.get('MONGODB_DB', 'tweets')
        #     )
        cls.MONGODB_SERVER = crawler.settings.get('MONGODB_SERVER', 'localhost')
        cls.MONGODB_PORT = crawler.settings.getint('MONGODB_PORT', 27017)
        cls.MONGODB_DB = crawler.settings.get('MONGODB_DB', 'tweets')
        pipe = cls()
        pipe.crawler = crawler
        return pipe

    def open_spider(self, spider):
        try:
            # Tracer()()
            self.client = pymongo.MongoClient(self.MONGODB_SERVER, self.MONGODB_PORT) 
            self.db = self.client[self.MONGODB_DB]
        except Exception as e:
            print self.style.ERROR("ERROR(MongodbPipeline): %s"%(str(e),))
            traceback.print_exc()

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        tweet_detail = {
            'tweet_id': item.get('tweet_id'),
            # 'convo_url': item.get('convo_url', ''),
            # 'is_retweet': item.get('is_retweet'),
            'user_id': item.get('user_id'),
            'user_screen_name': item.get('user_screen_name'),
            'text': item.get('text'),
            'created_at': item.get('created_at'),
            'image_url': item.get('image_url', []),
            'num_retweets': item.get('num_retweets'),
            'num_favorites': item.get('num_retweets'),
            'update_time': datetime.datetime.utcnow(),
        }
        # collection_name = item.__class__.__name__
        result=self.db["tweet_detail"].insert(tweet_detail)
        item["mongodb_id"] = str(result)
        return item

class DuplicatesPipeline(object):

    def __init__(self):
        self.ids_seen = set()

    def process_item(self, item, spider):
        if item['tweet_id'] in self.ids_seen:
            raise DropItem("Duplicate item found: %s" % item)
        else:
            self.ids_seen.add(item['tweet_id'])
            return item
