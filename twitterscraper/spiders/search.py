# -*- coding: utf-8 -*-
import time
import datetime
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
# from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from IPython.core.debugger import Tracer


class SearchSpider(scrapy.Spider):
    name = "search"
    allowed_domains = ["twitter.com"]
    start_urls = []
    min_tweet = None
    max_tweet = None
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
        self.query = query
        self.session_id = session_id.strftime('%Y-%m-%d')
        # Tracer()()
        url = self.construct_url(self.query)
        # Tracer()()
        self.start_urls.append(url)

    def parse(self, response):
        # Random string is used to construct the XHR sent to twitter.com
        random_str = "BD1UO2FFu9QAAAAAAAAETAAAAAcAAAASAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"

        data = json.loads(response.body_as_unicode())
        #default rate delay is 12s
        # rate_delay = self.settings['DOWNLOAD_DELAY']
        rate_delay = 6

        # delay_choices = [(1,30), (2,25), (3,20),(4,15),(5,10)]
        # delay_choices = [(1,50), (2,30), (3,10),(4,8),(5,2)] 
        delay_choices = [(0,1),(1,89), (2,4), (3,3),(4,2),(5,1)]
        # delay_choices = [(1,60), (2,20), (3,10),(4,8),(5,2)]
        # delay_choices = [(0,33),(1,56), (2,5), (3,3),(4,2),(5,1)]

        if data is not None and data['items_html'] is not None:
            tweets = self.extract_tweets(data['items_html'])
            # If we have no tweets, then we can break the loop early
            if len(tweets) == 0:
                Tracer()()
                # self.max_position = "TWEET-%s-%s-%s" % (self.max_tweet['tweet_id'], self.min_tweet['tweet_id'],random_str)
                # next_url = self.construct_url(self.query, max_position=self.max_position,operater="min_position")
                # Sleep for our rate_delay
                # time.sleep( random.uniform(0, self.settings['DOWNLOAD_DELAY']))
                pprint(data)
                logging.log(logging.DEBUG,data)
                logging.log(logging.INFO,
                    "Reach the end of search results( " + self.query + " )")
                return
                # yield Request(url=next_url, callback=self.parse)

            # If we haven't set our min tweet yet, set it now
            if self.min_tweet is None:
                self.min_tweet = tweets[0]
            elif self.min_tweet is not tweets[0]:
                self.min_tweet = tweets[0]

            # continue_search = self.save_tweets(tweets)

            # The max tweet is the last tweet in the list
            self.max_tweet = tweets[-1]

            referring_url = response.request.headers.get('Referer', None) or self.start_urls[0]
            # Tracer()()

            for tweet in tweets:
                # push parsed item to mongoDB pipline
                yield self.parse_tweet(tweet,referring_url)

            if self.min_tweet['tweet_id'] is not self.max_tweet['tweet_id']:
                self.max_position = "TWEET-%s-%s-%s" % (
                    self.max_tweet['tweet_id'],
                    self.min_tweet['tweet_id'],
                    random_str)
                #Construct next url to crawl
                next_url = self.construct_url(
                    self.query,
                    max_position=self.max_position,
                    operater="max_position")

                # Sleep for rate_delay
                # Tracer()()
                delay_multiple = self.weighted_choice(delay_choices)
                if delay_multiple is not 0:
                    delay_time = random.uniform(rate_delay*(delay_multiple-1), rate_delay*delay_multiple)
                    logging.log(logging.DEBUG,"Sleep for "+ str(delay_time) +" seconds")
                    time.sleep(delay_time)
                else:
                    logging.log(logging.DEBUG,"Sleep for "+ 0 +" seconds")

                print
                print "Next Request:" + "TWEET-%s-%s" % (
                    self.max_tweet['tweet_id'], self.min_tweet['tweet_id'])
                print
                # Tracer()()
                yield Request(url=next_url, callback=self.parse,dont_filter=True)

    def weighted_choice(self, choices):
        """
        Random select weighted choices
        :param choices: The pair of values and weights
        :return: A weighted value
        """
        # Tracer()()
        values, weights = zip(*choices)
        total = 0
        cum_weights = []
        for w in weights:
            total += w
            cum_weights.append(total)
        x = random.random() * total
        i = bisect(cum_weights, x)
        # Tracer()()
        return values[i]



    def parse_tweet(self, tweet,referring_url):
        tweet_item = items.TwitterscraperItem()
        tweet_item['session_id'] = self.session_id
        tweet_item['tweet_id'] = tweet['tweet_id']
        tweet_item['text'] = tweet['text']
        tweet_item['user_id'] = tweet['user_id']
        tweet_item['user_screen_name'] = tweet['user_screen_name']
        tweet_item['user_name'] = tweet['user_name']
        tweet_item['created_at_ts'] = tweet['created_at_ts']
        tweet_item['created_at_iso'] = tweet['created_at_iso']
        # tweet_item['convo_url'] = tweet['convo_url']
        # tweet_item['image_url'] = tweet['image_url']
        tweet_item['num_retweets'] = tweet['num_retweets']
        tweet_item['num_favorites'] = tweet['num_favorites']
        tweet_item['keyword'] = tweet['keyword']
        tweet_item['query'] = self.query
        # referring_url = response.request.headers.get('Referer', None)
        tweet_item['referring_url'] = referring_url
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
                    'keyword': []
                    }

                try:
                    text_p = li.find("p", class_="tweet-text")
                    if text_p is not None:
                        # Replace each emoji with its unicode value
                        # textElement.find('img.twitter-emoji').each((i, emoji) ->
                        #   $(emoji).html $(emoji).attr('alt')
                        # )
                        # Tacer()()
                        # pint
                        # [rint(text_p)
                        # emoji_dict = [
                        #     emoji for emoji in text_p.find_all(
                        #         "img", class_="twitter-emoji"
                        #     )
                        # ]
                        # def replace_all(text, dic):
                        #   for i, j in dic.iteritems():
                        #       text = text.replace(i, j)
                        #       return text
                        # len(emoji_dict) is not 0:
                        # for emoji in emoji_dict:
                        #     Tracer()()
                            # text_p = text_p.replace(
                            #     str(emoji), emoji['alt'].decode('ascii')
                            #     )
                        tweet['text'] = text_p.get_text()               

                        # If there is any user mention containing the query, then pass the tweet.
                        # Tracer()()
                        user_mentions = twitter_username_re.match(tweet['text'])
                        if user_mentions and any([self.query.lower() in user_mention.lower() for user_mention in user_mentions.groups()]):
                            # Tracer()()
                            logging.log(logging.DEBUG, 'Found '+self.query+' in '+ str(user_mentions.groups())+': Drop tweet '+tweet['tweet_id'])
                            continue
                        # If the keyword was found in the text and was the same with query, then accept the tweet 
                        if text_p.find("strong") and text_p.find("strong").get_text().lower() == self.query.lower():
                            tweet['keyword'] = text_p.find("strong").get_text()
                        else:
                            # The keyword is not in the text, then pass the tweet.
                            # Tracer()()
                            logging.log(logging.DEBUG, 'No '+self.query+' in the content of tweet'+': Drop tweet '+tweet['tweet_id'])
                            continue                   
                    else:
                        # Tracer()()
                        logging.log(logging.DEBUG, 'No content in the tweet'+': Drop tweet '+tweet['tweet_id'])
                        continue
                except Exception, e:
                    Tracer()()
                    logging.log(logging.DEBUG, "ERROR(extract_text_p): %s"%(str(e),))
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
                    # convo_a_tag = li.find("div",class_="stream-item-footer").find_next("a",class_="js-details")
                    # if convo_a_tag is not None:
                    #   print
                    #   print "convo_a_tag:"+ str(convo_a_tag['href'])
                    #   print
                    # tweet['convo_url'] = str(convo_a_tag)

                    # Tweet image url
                    # img_url_divs = li.select("div.js-old-photo")
                    # if len(img_url_divs) > 0:
                    #     for img_url_div in img_url_divs:
                    #         tweet['image_url'].append(img_url_div['data-image-url'])

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

        params = {
            'vertical': 'default',
            # Query Param
            'q': query+ ' '+'lang:en'+' '+ 'since:2006-03-21 until:2016-01-27', #melatonin 2015-04-09 return only one tweet
            # Type Param
            'src': 'typd'
        }

        #todo develop a query operator recognize function
        # def doit(text):
        #     import re
        #     matches=re.findall(r'\"(.+?)\"',text)
        #     # matches is now ['String 1', 'String 2', 'String3']
        #     return ",".join(matches)

        # q = doit(query) 

        # params = {
        #     'vertical': 'default',            
        #     # Type Param
        #     'src': 'typd'
        # }

        # If our max_position param is not None, we add it to the parameters
        if operater == "max_position":
            if max_position is not None:
                params['include_available_features'] = '1'
                params['include_entities'] = '1'
                params['max_position'] = max_position
                params['reset_error_state'] = 'false'

        elif operater == "min_position":
            if max_position is not None:
                params['composed_count'] = '0'
                params['include_available_features'] = '1'
                params['include_entities'] = '1'
                params['include_new_items_bar'] = 'true'
                params['interval'] = '30000'
                params['latent_count'] = '0'
                params['min_position'] = max_position
        # url_tupple = ('https', 'twitter.com', '/i/search/timeline',
        #               '', urlencode(OrderedDict(params)), '')
        url_tupple = ['https', 'twitter.com', '/i/search/timeline',
                      '', urlencode(OrderedDict(params)), '']
        # Tracer()()
        # url_tupple = ('https', 'twitter.com', 'i/profiles/show/'+user_screen_name+'/timeline/with_replies', '', urlencode(params), '')
        return urlunparse(url_tupple)
        # print urlunparse(url_tupple)
