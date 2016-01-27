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
from pymongo import errors

from scrapy.exceptions import DropItem
from scrapy import settings
import logging

from scrapy_mongodb import MongoDBPipeline

class DuplicatesPipeline(MongoDBPipeline):

    def process_item(self, item, spider):
        # if the connection exists, don't save it
        matching_item = self.collection.find_one(
            {#'session_id': item['session_id'],
             'tweet_id': item['tweet_id'],
             'user_name': item['user_name']}
        )
        if matching_item is not None:
            Tracer()()
            raise DropItem(
                "Duplicate found for %s, %s" %
                (item['user_name'], item['tweet_id'])
            )
        else:
            return item


class MongoDBPipeline_test(object):
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
            Tracer()()
            print self.style.ERROR("ERROR(MongodbPipeline): %s"%(str(e),))
            traceback.print_exc()

    def close_spider(self, spider):
        Tracer()()
        self.client.close()


    def process_item(self, item, spider):
        tweet_detail = {
            'tweet_id': item.get('tweet_id'),
            # 'convo_url': item.get('convo_url', ''),
            # 'is_retweet': item.get('is_retweet'),
            'user_id': item.get('user_id'),
            'user_screen_name': item.get('user_screen_name'),
            'user_name': item.get('user_name'),
            'text': item.get('text'),
            'created_at_ts': item.get('created_at_ts'),
            'image_url': item.get('image_url', []),
            'supplement': item.get('supplement',[]),
            'keyword': item.get('keyword', []),
            'num_retweets': item.get('num_retweets'),
            'num_favorites': item.get('num_retweets'),
            'update_time': datetime.datetime.utcnow(),
        }
        # collection_name = item.__class__.__name__
        '''
        Checking if record exists in MongoDB
        '''
        try:
            # Tracer()()
            result=self.db["tweet_detail"].insert(tweet_detail)
            item["mongodb_id"] = str(result)
            # Tracer()()
            # DuplicatesPipeline.ids_seen.add(item['tweet_id'])
            return item
        # except Exception as e:
        except errors.DuplicateKeyError as dke:
            raise DropItem("Duplicate item found: %s" % item)
            traceback.print_exc()
        except Exception as e:
            logging.log(logging.ERROR,"ERROR(MongodbPipeline): %s"%(str(e),) )   
            traceback.print_exc()



