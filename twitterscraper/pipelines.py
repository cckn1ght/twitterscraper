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
import re
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
             # 'keyword': item['keyword'],
             'user_name': item['user_name']}
        )
        if matching_item is not None:
            # Tracer()()
            raise DropItem(
                "Duplicate found for %s, %s, %s" %
                (item['user_name'], item['tweet_id'],item['keyword'])
            )
        else:
            return item
<<<<<<< HEAD
=======

class FilterNoContentPipeline(object):
    """Filter out tweet item that has no content in tweet

    """
    # def __init__(self, arg):
    #     super(FilterNoContentPipeline, self).__init__()
    #     self.arg = arg
    def process_item(self, item, spider):
        # Tracer()()
        if not item['text']:
            # Tracer()
            logging.log(logging.DEBUG, 'No content in the tweet: Drop tweet '+tweet['tweet_id'])
            raise DropItem(
                        "No content in tweet [%s] " % 
                        ( item['tweet_id'])
                        )
        return item

class FilterUserMentionPipeline(object):
    '''
    Filter out tweets that have target keyword in the user mentions within the text
    '''
    def __init__(self):
        self.twitter_username_re = re.compile(
                    r'(?<=^|(?<=[^a-zA-Z0-9-_\.]))@([A-Za-z_]+[A-Za-z0-9_]+[A-Za-z]+[A-Za-z0-9])'
                    # r'(?<=@)\w+'
                    )
        self.query = {}

    def process_item(self, item, spider):           
        for op in item['query'].split(','):
            if len(op.split(':')) == 1:
                self.query['keyword'] = op.split(':')[0]
            else:
                self.query[op.split(':')[0]] = op.split(':')[1]
        # Tracer()()  
        if "keyword" in self.query.keys():
            user_mentions = self.twitter_username_re.match(item['text'])
            if user_mentions and any([self.query['keyword'].lower() in user_mention.lower() for user_mention in user_mentions.groups()]):
                # Tracer()()
                logging.log(logging.DEBUG, "Found %s in tweet [%s]  %s: Drop tweet [%s]" % 
                    (self.query['keyword'], item['tweet_id'], item['text'],item['tweet_id'])
                    )
                raise DropItem(
                    "Found %s in tweet [%s]  %s" % 
                    (self.query['keyword'], item['tweet_id'], item['text'])
                )
        return item
>>>>>>> origin/ood-branch
