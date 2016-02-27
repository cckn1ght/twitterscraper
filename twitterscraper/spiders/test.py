# -*- coding: utf-8 -*-
import time
import datetime
import traceback
from pprint import pprint
import urlparse
from urlparse import urlunparse
from urllib import urlencode
from urllib import urlopen
from urllib import quote
import json
import re
import random
# from random import random
from bisect import bisect
# from string import decode
from bs4 import BeautifulSoup
from collections import OrderedDict

# from scrapy.spider import BaseSpider
import scrapy
import logging
# from scrapy.spiders import Spider
# from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request
from twitterscraper import items
from twitterscraper.utils.project import parse_query
# from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from IPython.core.debugger import Tracer


class SearchSpider(scrapy.Spider):
    name = "test"
    allowed_domains = ["twitter.com"]
    custom_settings= {'MONGODB_COLLECTION': 'valerian'
                      # 'LOG_FILE':'logs/echinacea/scrapy.log'
    }
    start_urls = []
    settings = get_project_settings()

    def __init__(self, domain=None, query="from:TangTotoro"):
        # super(SearchSpider, self).__init__(*args, **kwargs)
        # query = kwargs.get('query')
        session_id = datetime.datetime.utcnow().date()
        
        """
        Scrape items from twitter
        :param query:   Query to search Twitter with. Takes form of queries
        constructed with using Twitters
                        advanced search: https://twitter.com/search-advanced
        """
        self.query_str = query
        self.query = parse_query(query)
        # self.is_time_window_new = True
        self.query_keyword = query.split(',')[0]
        self.min_tweet = {}
        self.max_tweet = {}
        # self.very_last_tweet_id = "713813" #melatonin' last tweet
        self.very_last_tweet_id = "25283831" #valerian's last tweet 
        self.until_boundary = self.query['until']

        self.session_id = session_id.strftime('%Y-%m-%d')
        # Tracer()()
        url = self.construct_url(self.query)
        # Tracer()()
        self.start_urls.append(url)
        # Tracer()()

    def parse(self, response):
        # Random string is used to construct the XHR sent to twitter.com
        random_str = "BD1UO2FFu9QAAAAAAAAETAAAAAcAAAASAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
        data = json.loads(response.body_as_unicode())

        if data['new_latent_count'] > 0:
            # If the number of tweets in response is greater than 0,
            # then extract tweets from item_html
            tweets = self.extract_tweets(data['items_html'])
            for tweet in tweets:
                # push parsed item to mongoDB pipline
                yield self.parse_tweet(tweet, response)

            if len(tweets) >= 2:
                # if response.url.find('max_position') > -1:
                #     # 2016-01-31 17:51:32
                #     self.until_boundary = tweets[-1]['created_at_iso'].split(' ')[0]
                # else:
                #     self.until_boundary = self.query['until']
                # Tracer()()
                # if self.min_tweet[created_at_iso].split(' ')[0] is self.max_tweet['created_at_iso'].split(' ')[0]:
                self.until_boundary = tweets[-1]['created_at_iso'].split(' ')[0]
                # The max tweet is the last tweet in the list
                self.min_tweet = tweets[0]
                self.max_tweet = tweets[-1]

                self.max_position = "TWEET-%s-%s-%s" % (
                    self.max_tweet['tweet_id'],
                    self.min_tweet['tweet_id'],
                    random_str
                    )

                next_url = self.construct_url(
                    self.query,
                    max_position=self.max_position,
                    operater="max_position"
                    )
                print
                print "Parsed "+str(data['new_latent_count'])+" Tweets,"
                print "Next Request:" + "TWEET-%s-%s" % (
                    self.max_tweet['tweet_id'],
                    self.min_tweet['tweet_id']
                    )
                print
                # Tracer()()
                yield Request(url=next_url, callback=self.parse, dont_filter=True)
            else:
                # TODO: # jump to the yesterday of until_boundary
                # Tracer()()
                self.query['until'] = self.adjust_time_window(self.until_boundary, 0, 'backward')
                new_time_window_url = self.construct_url(self.query)
                # self.is_time_window_new = True
                yield Request(url=new_time_window_url, callback=self.parse, dont_filter=True)
            # If we have no tweets, then we can break the loop early
        else:
            if response.url is not self.start_urls[0]:
                if self.is_end():
                    # Tracer()()
                    pprint(data)
                    logging.log(logging.DEBUG, data)
                    logging.log(logging.INFO, "Reach the end of search results( " + self.query_str + " )")
                    print( "Reach the end of search results( " + self.query_str + " )")
                    return
                else:
                    # Tracer()()
                    self.query['until'] = self.adjust_time_window(self.until_boundary, 0, 'backward')
                    new_time_window_url = self.construct_url(self.query)

                    logging.log(logging.INFO,'Construct new time window: [%s,%s)'%
                        (
                            self.query['since'],
                            self.query['until']
                        )
                    )

                    yield Request(url=new_time_window_url, callback=self.parse, dont_filter=True)
                # jump to the yesterday of until_boundary
            else:
                Tracer()()
                self.query['until'] = self.adjust_time_window(self.query['until'], 1, 'backward')
                new_time_window_url = self.construct_url(self.query)
                logging.log(logging.INFO,'Construct new time window: [%s, %s)'%
                        (
                            self.query['since'],
                            self.query['until']
                        )
                    )
                yield Request(url=new_time_window_url, callback=self.parse, dont_filter=True)



    def parse_tweet(self, tweet,response):
        tweet_item = items.TwitterscraperItem()
        tweet_item['session_id'] = self.session_id
        tweet_item['tweet_id'] = tweet['tweet_id']
        tweet_item['text'] = tweet['text']
        tweet_item['user_id'] = tweet['user_id']
        tweet_item['user_screen_name'] = tweet['user_screen_name']
        tweet_item['user_name'] = tweet['user_name']
        tweet_item['created_at_ts'] = tweet['created_at_ts']
        tweet_item['created_at_iso'] = tweet['created_at_iso']
        tweet_item['num_retweets'] = tweet['num_retweets']
        tweet_item['num_favorites'] = tweet['num_favorites']
        tweet_item['keyword'] = tweet['keyword']
        tweet_item['query'] = self.query_str
        tweet_item['referring_url'] = response.request.headers.get('Referer', None) or self.start_urls[0]
        tweet_item['request_url'] = response.url
        tweet_item['quote_tweet_id'] = tweet['quote_tweet_userid']
        tweet_item['quote_tweet_userid'] = tweet['quote_tweet_userid']
        tweet_item['quote_tweet_username'] = tweet['quote_tweet_username']
        tweet_item['quote_tweet_screenname'] = tweet['quote_tweet_screenname']
        tweet_item['quote_tweet_text'] = tweet['quote_tweet_text']
        try:
            tweet_item['html'] = tweet['html']
        except Exception, e:
            traceback.print_exc()
        # Tracer()()
        return tweet_item

    def extract_tweets(self, items_html):
        """
        Parses Tweets from the given HTML
        :param items_html: The HTML block with tweets
        :return: A JSON list of tweets
        """
        try:
            soup = BeautifulSoup(items_html, "lxml")
            tweets = []
            twitter_username_re = re.compile(
                r'(?<=^|(?<=[^a-zA-Z0-9-_\.]))@([A-Za-z_]+[A-Za-z0-9_]+[A-Za-z]+[A-Za-z0-9])'
                # r'(?<=@)\w+'
                )

            for li in soup.find_all("li", class_='js-stream-item'):
                # Tracer()()
                # If our li doesn't have a tweet-id, we skip it as it's not going
                # to be a tweet.
                if 'data-item-id' not in li.attrs:
                    continue

                tweet = {
                    'tweet_id': li['data-item-id'],
                    'text': None,
                    # 'is_retweet':false,
                    'user_id': None,
                    'user_screen_name': None,
                    'user_name': None,
                    'created_at_ts': None,
                    'created_at_iso': None,
                    # 'convo_url': None,
                    # 'image_url': [],
                    'num_retweets': 0,
                    'num_favorites': 0,
                    'keyword': [],
                    'quote_tweet_id':None,
                    'quote_tweet_userid':None,
                    'quote_tweet_username' :None,
                    'quote_tweet_screenname' :None,
                    'quote_tweet_text' :None,
                    'html':None
                    }
                try:
                    tweet['html'] = str(li)
                except Exception,e:
                    Tracer()()
                    pass

                '''
                Extract tweet text
                '''
                try:
                    text_p = li.find("p", class_="tweet-text")
                    if text_p is not None:
                        tweet['text'] = text_p.get_text()                
                except Exception, e:
                    Tracer()()
                    logging.log(logging.DEBUG, "ERROR(extract_text_p): %s"%(str(e),))
                    traceback.print_exc()
                '''
                Extract quote tweet content if exists
                '''
                try:
                    quote_tweet = li.find("div", class_="QuoteTweet-innerContainer")
                    if quote_tweet is not None:
                        # Tracer()()
                        tweet['quote_tweet_id'] = quote_tweet['data-item-id']
                        tweet['quote_tweet_userid'] = quote_tweet['data-user-id']
                        tweet['quote_tweet_screenname'] = quote_tweet['data-screen-name']
                        tweet['quote_tweet_username'] = quote_tweet.find("b",class_="QuoteTweet-fullname").get_text()
                        tweet['quote_tweet_text'] = quote_tweet.find("div",class_="QuoteTweet-text").get_text()
                except Exception, e:
                    Tracer()()
                    logging.log(logging.DEBUG, "ERROR(extract_quote_tweet): %s"%(str(e),))
                    traceback.print_exc()

                # Tweet isRetweet
                # is_retweet = li.find('js-retweet-text').length is not 0

                # Tweet User ID, User Screen Name, User Name
                try:
                    user_details_div = li.find("div", class_="tweet")
                    if user_details_div is not None:
                        tweet['user_id'] = user_details_div['data-user-id']
                        tweet['user_screen_name'] = user_details_div[
                            'data-screen-name']
                        tweet['user_name'] = user_details_div['data-name']
                        # Tracer()()
                    # Tweet date
                    date_span = li.find("span", class_="_timestamp")
                    if date_span is not None:
                        # tweet['created_at'] = float(date_span['data-time-ms'])
                        tweet['created_at_ts'] = int(date_span['data-time'])
                        try:
                            # tweet['created_at_iso'] = datetime.datetime.fromtimestamp(tweet["created_at_ts"]).strftime('%Y-%m-%d %H:%M:%S')
                            tweet['created_at_iso'] = datetime.datetime.fromtimestamp(tweet["created_at_ts"]).isoformat(' ')
                        except Exception, e:
                            Tracer()()
                            logging.log(logging.DEBUG, "ERROR(extract _timestamp): %s"%(str(e),)) 
                            traceback.print_exc()

                    # Tweet Retweets
                    retweet_span = li.select(
                        "span.ProfileTweet-action--retweet > span.ProfileTweet-actionCount")
                    if retweet_span is not None and len(retweet_span) > 0:
                        tweet['num_retweets'] = int(
                            retweet_span[0]['data-tweet-stat-count'])

                    # Tweet Favourites
                    favorite_span = li.select(
                        "span.ProfileTweet-action--favorite > span.ProfileTweet-actionCount")
                    if favorite_span is not None and len(retweet_span) > 0:
                        tweet['num_favorites'] = int(
                            favorite_span[0]['data-tweet-stat-count'])
                except Exception, e:
                    Tracer()()
                    logging.log(logging.DEBUG, "ERROR(extract_tweet_meta_data): %s"%(str(e),))
                    traceback.print_exc()

                # self.parse_tweet(tweet)
                # Tracer()()#break point
                
                print
                print tweet['tweet_id']+': '+tweet['created_at_iso']+' '+'['+tweet['user_name']+']'+' '+tweet['text']
                print

                tweets.append(tweet)
            return tweets
        except Exception, e:
            Tracer()()
            logging.log(logging.DEBUG, "ERROR(extract_tweets): %s"%(str(e),))
            traceback.print_exc()

    @staticmethod
    def construct_url(query, max_position=None, operater="max_position"):
        """
        For a given query, will construct a URL to search Twitter with
        :param query: The query term used to search twitter
        :param max_position: The max_position value to select the next
        pagination of tweets
        :return: A string URL
        """
        try:
            sequent_q = ''
            for key, value in query.iteritems():
                if key is 'keyword':
                    op = value + ' '
                else:
                    op = key + ':' + value + ' '
                sequent_q += op
            
            # Tracer()()
            params = {
                'vertical': 'default',
                # Query Param
                # 'q': query+ ' '+'lang:en'+' '+'since:2007-01-19 until:2014-03-13', #st.john's wort since:2007-01-20 until:2014-03-12 
                'q': sequent_q,
                # Type Param
                'src': 'typd',
                'f':'tweets'
            }

            # If our max_position param is not None, we add it to the parameters
            if operater == "max_position":
                if max_position is not None:
                    params['include_available_features'] = '1'
                    params['include_entities'] = '1'
                    params['max_position'] = max_position
                    params['reset_error_state'] = 'false'
                    params['last_note_ts'] = int(time.time())

            elif operater == "min_position":
                if max_position is not None:
                    params['composed_count'] = '0'
                    params['include_available_features'] = '1'
                    params['include_entities'] = '1'
                    params['include_new_items_bar'] = 'true'
                    params['interval'] = '30000'
                    params['latent_count'] = '0'
                    params['min_position'] = max_position
                    params['last_note_ts'] = int(time.time())
            # url_tupple = ('https', 'twitter.com', '/i/search/timeline',
            #               '', urlencode(OrderedDict(params)), '')
            url_tupple = ['https', 'twitter.com', '/i/search/timeline',
                          '', urlencode(OrderedDict(params)), '']
            # Tracer()()
            # url_tupple = ('https', 'twitter.com', 'i/profiles/show/'+user_screen_name+'/timeline/with_replies', '', urlencode(params), '')
            return urlunparse(url_tupple)
        except Exception:
            traceback.print_exc()
            pass

    # def construct_new_time_window_url(self,window_boundary,time_window_operator='until',days=1,'')

    def adjust_time_window(self, boundary, days=1, direction='backward'):
        boundary_obj = datetime.datetime.strptime(boundary,'%Y-%m-%d')
        time_delta = datetime.timedelta(days=days)
        if direction is 'backward':
            boundary_obj = boundary_obj - time_delta
        elif direction is 'forward':
            boundary_obj = boundary_obj + time_delta
        else:
            logging.log(logging.INFO, 'Cursor is not supposed to move to %s direction '%(direction))
            traceback.print_exc()
        return boundary_obj.strftime('%Y-%m-%d')

    def is_end(self):
        '''
        Check if self.max_tweet is the very last tweet
        if yes, return True
        else, return False 

        '''
        if self.max_tweet['tweet_id'] is self.very_last_tweet_id:
            return True
        else:
            return False
        # if response.url.find('max_position') > -1:
        # # if self.is_time_window_new:
        #     if self.max_tweet['tweet_id'] is self.very_last_tweet_id:
        #         return True
        #     else:
        #         return False
        # else:
        #     if self.max_tweet['tweet_id'] is self.very_last_tweet_id:
        #         return True
        #     else:
        #         return False
