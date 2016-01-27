#!/usr/bin/python
#-*-coding:utf-8-*-

import random
from scrapy import signals
from scrapy.downloadermiddlewares.useragent import UserAgentMiddleware

from IPython.core.debugger import Tracer
import logging

class RotateUserAgentMiddleware(UserAgentMiddleware):
    """
        a useragent middleware which rotate the user agent when crawl websites
        
        if you set the USER_AGENT_LIST in settings,the rotate with it,if not,then use the default user_agent_list attribute instead.
    """
    #the default user_agent_list composes chrome,I E,firefox,Mozilla,opera,netscape
    #for more user agent strings,you can find it in http://www.useragentstring.com/pages/useragentstring.php
    """
    Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.31 (KHTML, like Gecko) Chrome/26.0.1410.43 Safari/537.31
    """
    def __init__(self, settings, user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36'):
        super(
            RotateUserAgentMiddleware, self
            ).__init__()
        self.user_agent = user_agent     
        # Tracer()()
        user_agent_list_file = settings.get('USER_AGENT_LIST')
        if not user_agent_list_file:
            # If USER_AGENT_LIST_FILE settings is not set,
            # Use the default USER_AGENT or whatever was
            # passed to the middleware.
            ua = settings.get('USER_AGENT', user_agent)
            self.user_agent_list = [ua]
        else:
            with open(user_agent_list_file, 'r') as f:
                self.user_agent_list = [line.strip() for line in f.readlines()]

    @classmethod
    def from_crawler(cls, crawler):
        obj = cls(crawler.settings)
        crawler.signals.connect(obj.spider_opened,
                                signal=signals.spider_opened)
        return obj

    def process_request(self, request, spider):
        try:
            if random.choice(xrange(1,100)) <= 33:
                user_agent = random.choice(self.user_agent_list)
                if user_agent:
                    logging.log(logging.DEBUG,'Change user agent to :'+user_agent)
                    # Tracer()()
                    request.headers.setdefault('User-Agent', user_agent)
        except Exception, e:
            Tracer()()
            logging.log( logging.DEBUG,"ERROR(RotateUserAgentMiddleware): %s"%(str(e),))
            traceback.print_exc()