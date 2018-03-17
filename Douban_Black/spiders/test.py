from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
import random
import time
import os
import sys
import io
from scrapy.http import Request
from scrapy import signals

class Spider_Black(CrawlSpider):

    name = 'test'
    error = 0
    page = 0
    allowed_domain = ['movie.douban.com']
    start_urls = ['https://movie.douban.com']

    # @classmethod
    # def from_crawler(cls, crawler, *args, **kwargs):
    #     spider = super(Spider_Black, cls).from_crawler(crawler, *args, **kwargs)
    #     crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
    #     return spider

    def start_requests(self):
        url = 'https://movie.douban.com'
        return [Request(url, callback=self.parse)]

    def log_error(self, cwd, error):
        file = cwd + '/error.txt'
        with open(file, 'a') as f:
            f.write(error)

    def spider_closed(self):
        print('Spider closed, 共爬了', self.page, '页')


    # 由初始url分别进短评和长评
    def parse(self, response):
        print('enen')
        urls = []
        with open('urls.txt', 'r') as f:
            lines = f.readlines()
            for line in lines:
                line = line.strip('\n').strip(' ')
                urls.append(line)
        for url in urls:
            url_short = url + 'comments'
            url_long = url + 'reviews'
            yield Request(url=url_short, callback=self.save_short)
            yield Request(url=url_long, callback=self.save_long)

    def save_short(self, response):
        print('shor')

    def save_long(self, response):
        print('long')