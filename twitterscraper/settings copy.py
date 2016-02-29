# -*- coding: utf-8 -*-

# Scrapy settings for twitterscraper project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#     http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
#     http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'twitterscraper'

SPIDER_MODULES = ['twitterscraper.spiders']
NEWSPIDER_MODULE = 'twitterscraper.spiders'


# Crawl responsibly by identifying yourself (and your website) on the user-agent
# USER_AGENT = 'twitterscraper (+http://www.yourdomain.com)'

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See http://scrapy.readthedocs.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY=0.1
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN=16
#CONCURRENT_REQUESTS_PER_IP=16

# Disable cookies (enabled by default)
#COOKIES_ENABLED=False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED=False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
#}

# Enable or disable spider middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'twitterscraper.middlewares.MyCustomSpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
#DOWNLOADER_MIDDLEWARES = {
#    'twitterscraper.middlewares.MyCustomDownloaderMiddleware': 543,
#}

# Enable or disable extensions
# See http://scrapy.readthedocs.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See http://scrapy.readthedocs.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
   'twitterscraper.pipelines.MongoDBPipeline': 300,
   'twitterscraper.pipelines.DuplicatesPipeline': 0,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See http://doc.scrapy.org/en/latest/topics/autothrottle.html
# NOTE: AutoThrottle will honour the standard settings for concurrency and delay
AUTOTHROTTLE_ENABLED=True
# The initial download delay
AUTOTHROTTLE_START_DELAY=3
# The maximum download delay to be set in case of high latencies
AUTOTHROTTLE_MAX_DELAY=60
# Enable showing throttling stats for every response received:
AUTOTHROTTLE_DEBUG=False

# Enable and configure HTTP caching (disabled by default)
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED=True
#HTTPCACHE_EXPIRATION_SECS=0
#HTTPCACHE_DIR='httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES=[]
#HTTPCACHE_STORAGE='scrapy.extensions.httpcache.FilesystemCacheStorage'

# DOWNLOADER_MIDDLEWARES = {
#     'twitterscraper.contrib.downloadmiddleware.google_cache.GoogleCacheMiddleware':50,
#     'scrapy.contrib.downloadermiddleware.useragent.UserAgentMiddleware': None,
#     'twitterscraper.contrib.downloadmiddleware.rotate_useragent.RotateUserAgentMiddleware':400,
# }



# Retry many times since proxies often fail
RETRY_TIMES = 10
# Retry on most error codes since proxies fail for different reasons
RETRY_HTTP_CODES = [500, 503, 504, 400, 403, 404, 408]

DOWNLOADER_MIDDLEWARES = {
    'twitterscraper.contrib.downloadmiddleware.google_cache.GoogleCacheMiddleware':543,
    'scrapy.contrib.downloadermiddleware.useragent.UserAgentMiddleware': None,
    'twitterscraper.contrib.downloadmiddleware.rotate_useragent.RotateUserAgentMiddleware':643,
    'scrapy.contrib.downloadermiddleware.retry.RetryMiddleware': 743,
    # Fix path to this module
    'twitterscraper.contrib.downloadermiddleware.randomproxy.RandomProxy': 843,
    'scrapy.contrib.downloadermiddleware.httpproxy.HttpProxyMiddleware': 943,
}

# DOWNLOADER_MIDDLEWARES = {
#     'twitterscraper.contrib.downloadmiddleware.google_cache.GoogleCacheMiddleware':50,
#     'scrapy.contrib.downloadermiddleware.useragent.UserAgentMiddleware': None,
#     'twitterscraper.contrib.downloadmiddleware.rotate_useragent.RotateUserAgentMiddleware':400,
#     'scrapy.contrib.downloadermiddleware.retry.RetryMiddleware': 90,
#     # Fix path to this module
#     'twitterscraper.contrib.downloadermiddleware.randomproxy.RandomProxy': 100,
#     'scrapy.contrib.downloadermiddleware.httpproxy.HttpProxyMiddleware': 110,
# }

GOOGLE_CACHE_DOMAINS = ['twitter.com',]

# Proxy list containing entries like
# http://host1:port
# http://username:password@host2:port
# http://host3:port
# ...
PROXY_LIST = '_reliable_list.txt'
LOG_FILE = "logs/scrapy.log"


MONGODB_SERVER = "localhost"
MONGODB_PORT = 27017
MONGODB_DB = "tweets"
MONGODB_COLLECTION = "echinacea"
