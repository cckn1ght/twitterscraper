# Copyright (C) 2013 by Aivars Kalvans <aivars.kalvans@gmail.com>
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import re
import random
import base64
import logging
# from scrapy.conri

logger = logging.getLogger('scrapy')

from IPython.core.debugger import Tracer

class RandomProxy(object):
    def __init__(self, settings):
        # Tracer()()
        self.proxy_list = settings.get('PROXY_LIST')
        self.odds = settings.get('PROXY_CHANGING_ODDS')

        try:
            fin = open(self.proxy_list)
            
        except Exception, e:
            traceback.print_exc()

        self.proxies = {}
        data = fin.readlines()
        if len(data) == 0:
            # Tracer()()
            logger.info('The proxy_list is empty')
            return
        for line in data:
            # Reconize proxy that with "http://
            # parts = re.match('(\w+://)(\w+:\w+@)?(.+)', line)
            # Reconize proxy that without "http://"
            parts = re.match('(\w+:\w+@)?(.+)', line)

            if parts is None:
                # Tracer()()
                logger.info('Did not read the line')
                return
            # Tracer()()
            # Cut trailing @
            if parts.group(1):
                user_pass = parts.group(1)[:-1]
            else:
                user_pass = ''

            self.proxies["http://"+parts.group(2)] = user_pass

        fin.close()

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    def process_request(self, request, spider):
        # Tracer()()
        # Don't overwrite with a random one (server-side state for IP)
        if 'proxy' in request.meta:
            return

        if len(self.proxies) == 0:
            raise ValueError('All proxies are unusable, cannot proceed')

        self.random_pick_proxy(request, self.odds)

    def random_pick_proxy(self, request, odds=100):
        # Change proxy here
        # Then check number of retries on the request 
        # and decide if you want to give it another chance.
        # If not - return None else
        if random.choice(xrange(1,100)) <= odds:
            proxy_address = random.choice(self.proxies.keys())
            proxy_user_pass = self.proxies[proxy_address]

            request.meta['proxy'] = proxy_address

            print ('Changing to proxy :' + proxy_address )
            logger.info('Changing to proxy [%s], %d proxies left' % (proxy_address, len(self.proxies)))

            if proxy_user_pass:
                basic_auth = 'Basic ' + base64.encodestring(proxy_user_pass)
                request.headers['Proxy-Authorization'] = basic_auth

    # def process_exception(self, request, exception, spider):
    #     try:
    #         proxy = request.meta['proxy']
    #         del self.proxies[proxy]
    #         print ('Removing failed proxy <' + proxy + '>, ' + str(len(self.proxies)) + ' proxies left')
    #         logger.info('Removing failed proxy <' + proxy + '>, ' + str(len(self.proxies)) + ' proxies left')
    #     except KeyError:
    #         pass        
    #     except Exception, e:
    #         pass  

    def process_response(self, request, response, spider):
       if response.status in [403, 400] and 'proxy' in request.meta:
           # Tracer()()
           logger.info('Response status: {0} using proxy {1} retrying request to {2}'.format(response.status, request.meta['proxy'], request.url))
           proxy = request.meta['proxy']
           del request.meta['proxy']
           
           try:
               del self.proxies[proxy]
               print ('403||404:Removing banned proxy <{0}>, {1} proxies left'.format(proxy, len(self.proxies)))
               logger.info('Remov banned proxy <{0}>, {1} proxies left'.format(proxy, len(self.proxies)))
           except KeyError:
               pass
           return request
       return response

    def process_exception(self, request, exception, spider):
        if 'proxy' in request.meta:
            # Tracer()()
            proxy = request.meta['proxy']
            del request.meta['proxy']
            # print ('Remove proxy in request.meta["proxy"]:' + proxy)
            try:
                del self.proxies[proxy]
                print ('Removed failed proxy <{0}>, {1} proxies left'.format(proxy, len(self.proxies)))
                logger.info('Removing failed proxy <{0}>, {1} proxies left'.format(proxy, len(self.proxies)))
            except KeyError:
                pass
            # self.random_pick_proxy(request, 100)
            return request
            # return request
