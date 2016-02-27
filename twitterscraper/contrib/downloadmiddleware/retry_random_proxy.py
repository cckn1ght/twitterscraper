import random
from scrapy import signals
from scrapy.downloadermiddlewares.retry import RetryMiddleware
from twitterscraper.contrib.downloadmiddleware.randomproxy import RandomProxy

from IPython.core.debugger import Tracer
import logging

class RetryRandomProxy(RetryMiddleware):
    
    def _retry(self, request, reason, spider):
        retries = request.meta.get('retry_times', 0) + 1
        if retries <= self.max_retry_times:
            logger.debug("Retrying %(request)s (failed %(retries)d times): %(reason)s",
                         {'request': request, 'retries': retries, 'reason': reason},
                         extra={'spider': spider})
            retryreq = request.copy()
            retryreq.meta['retry_times'] = retries
            retryreq.dont_filter = True
            retryreq.priority = request.priority + self.priority_adjust
            return retryreq
        else:

            logger.debug("Gave up retrying %(request)s (failed %(retries)d times): %(reason)s",
                         {'request': request, 'retries': retries, 'reason': reason},
                         extra={'spider': spider})