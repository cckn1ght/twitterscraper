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





