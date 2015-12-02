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
def load_user_list(abs_path):
    # user_screen_names = []
    # with open(abs_path, 'r') as f:
    # # usr_screen_names = f.readlines()
    #     for line in f:
    #         cleanedLine = line.strip()
    #         if cleanedLine: # is not empty
    #             user_screen_names.append(cleanedLine)
    user_screen_names = [line.rstrip('\n') for line in open(abs_path)]
    return user_screen_names

# Tracer()()
file_abs_path = os.path.abspath(
	'../screen_names/test.txt'
	)
usr_screen_names = load_user_list(file_abs_path)
runner = CrawlerRunner(get_project_settings())
dfs = set()
for usr_screen_name in usr_screen_names:
    q = 'from:'+usr_screen_name
    spider = runner.crawl('search', domain='twitter.com', query=q)
    dfs.add(spider)
defer.DeferredList(dfs).addBoth(lambda _: reactor.stop())
log.msg('Reactor activated...')
reactor.run()# the script will block here until all crawling jobs are finished
log.msg('Reactor stopped.')
