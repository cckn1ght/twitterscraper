import os
import sys
import io
from twisted.internet import reactor
from twisted.internet import defer
from scrapy.crawler import CrawlerRunner
from scrapy.utils.project import get_project_settings
from scrapy import log
# from scrapy import signals
# from twitterscraper.spiders.search import SearchSpider

from IPython.core.debugger import Tracer

'''Loading the list of users' screen_name '''


runner = CrawlerRunner(get_project_settings())

q = 'from:TangTotoro'
d = runner.crawl('search', domain='twitter.com', query=q)

d.addBoth(lambda _: reactor.stop())
log.msg('Reactor activated...')
reactor.run()# the script will block here until all crawling jobs are finished
log.msg('Reactor stopped.')