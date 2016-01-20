from scrapy import log
from settings import USER_AGENT_LIST

import random
import telnetlib
import time


# 49% ip change
class RetryChangeProxyMiddleware(object):
    def process_request(self, request, spider):
        if random.choice(xrange(1,100)) <= 49:
            log.msg('Changing proxy')
            tn = telnetlib.Telnet('127.0.0.1', 9051)
            tn.read_until("Escape character is '^]'.", 2)
            tn.write('AUTHENTICATE "<PASSWORD HERE>"\r\n')
            tn.read_until("250 OK", 2)
            tn.write("signal NEWNYM\r\n")
            tn.read_until("250 OK", 2)
            tn.write("quit\r\n")
            tn.close()
            log.msg('>>>> Proxy changed. Sleep Time')
            time.sleep(10)



# # 30% useragent change
# class RandomUserAgentMiddleware(object):
#     def process_request(self, request, spider):
#         if random.choice(xrange(1,100)) <= 30:
#             log.msg('Changing UserAgent')
#             ua  = random.choice(USER_AGENT_LIST)
#             if ua:
#                 request.headers.setdefault('User-Agent', ua)
#             log.msg('>>>> UserAgent changed')