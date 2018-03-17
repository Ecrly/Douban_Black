from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
import random
import time
import os
import sys
import io
from scrapy.http import Request
from scrapy import signals
sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='utf8')


class Spider_Black(CrawlSpider):

    name = 'black'
    num = 0
    error = 0
    page = 0
    allowed_domain = ['movie.douban.com']
    start_urls = ['https://movie.douban.com/subject/6390825/comments?status=P']

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(Spider_Black, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider

    def log_error(self, cwd, error):
        file = cwd + '/error.txt'
        with open(file, 'a') as f:
            f.write(error)

    def spider_closed(self):
        print('Spider closed, 共爬了', self.page, '页', self.num, '条评论')

    def parse(self, response):
        commands = response.xpath(".//*[@id='comments']/div[@class='comment-item']/div[@class='comment']/p/text()").extract()
        self.page += 1
        print('page', self.page)
        cwd = os.getcwd() + '/data'
        if not os.path.exists(cwd):
            os.makedirs(cwd)
        file = cwd + '/commands.txt'

        with open(file, 'a') as f:
            for command in commands:
                self.num += 1
                try:
                    command = str(self.num) + '\n' + command
                    f.write(command)
                except Exception as e:
                    self.error += 1
                    err = str(self.error) + '\n' + str(e)
                    self.log_error(cwd, err)
                print(command)
                time.sleep(random.randint(0,2))


        url = 'https://movie.douban.com/subject/6390825/comments'
        add = response.xpath(".//*[@id='paginator']/a[@class='next']/@href").extract()
        if add:
            url = url + add[0]
            yield Request(url=url, callback=self.parse)
