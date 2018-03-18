from scrapy.spiders import CrawlSpider
import random
import time
import os
import urllib
import urllib.request
from PIL import Image
from scrapy.http import Request, FormRequest, HtmlResponse
from scrapy import signals

class Spider_Black(CrawlSpider):

    name = 'black_'
    error = 0
    page = 0
    allowed_domain = ['movie.douban.com', 'www.douban.com', 'accounts.douban.com']
    start_urls = ['https://movie.douban.com/subject/26972275/']

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(Spider_Black, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider

    def spider_closed(self):
        print('Spider closed, 共爬了', self.page, '页')

    def start_requests(self):
        return [Request('https://www.douban.com/accounts/login?source=movie', meta={'cookiejar': 1}, callback=self.post_login, dont_filter=True)]

    def post_login(self, response):
        captcha_id = response.xpath('//input[@name="captcha-id"]/@value').extract_first()
        captcha_image_url = response.xpath('//img[@id="captcha_image"]/@src').extract_first()
        if captcha_image_url is None:
            print("登录时无验证码")
            formdata = {
                "source": "movie",
                # "redir": "https://movie.douban.com/",
                "form_email": "1693348468@qq.com",
                "form_password": "cl19961102",
                "login":"登录",
            }
        else:
            print("登录时有验证码")
            # 将图片验证码下载到本地
            urllib.request.urlretrieve(captcha_image_url, 'captcha.jpeg')
            # 打开图片，以便我们识别图中验证码
            try:
                im = Image.open('captcha.jpeg')
                im.show()
            except:
                pass
            # 手动输入验证码
            captcha_solution = input('根据打开的图片输入验证码:')
            formdata = {
                "source": "movie",
                # "redir": "https://movie.douban.com/",
                "form_email": "1693348468@qq.com",
                "form_password": "cl19961102",
                "captcha-solution": captcha_solution,
                "captcha-id": captcha_id,
                "login": "登录",
            }

        print("登录中")
        # 提交表单
        return FormRequest.from_response(response,
                                         meta={"cookiejar": response.meta["cookiejar"]},
                                         formdata=formdata,
                                         callback=self.parse,
                                         dont_filter=True)

    #  来源：https://www.cnblogs.com/littleseven/p/5677414.html
    def _requests_to_follow(self, response):
        """重写加入cookiejar的更新"""
        if not isinstance(response, HtmlResponse):
            return
        seen = set()
        for n, rule in enumerate(self._rules):
            links = [l for l in rule.link_extractor.extract_links(response) if l not in seen]
            if links and rule.process_links:
                links = rule.process_links(links)
            for link in links:
                seen.add(link)
                r = Request(url=link.url, callback=self._response_downloaded)
                # 下面这句是重写的
                r.meta.update(rule=n, link_text=link.text, cookiejar=response.meta['cookiejar'])
                yield rule.process_request(r)

    # 由初始url分别进短评和长评
    def parse(self, response):
        print(response.meta['cookiejar'])
        urls = []
        with open('start_urls.txt', 'r') as f:
            lines = f.readlines()
            for line in lines:
                line = line.strip('\n').strip(' ')
                urls.append(line)
        for url in urls:
            url_short = url + 'comments'
            url_long = url + 'reviews'
            yield Request(url=url, callback=self.save_main)
            # 短评未登录只能访问10页，因此加上cookiejar
            yield Request(url=url_short,meta={"cookiejar": response.meta['cookiejar']}, callback=self.save_short)
            yield Request(url=url_long, callback=self.save_long)

    # 保存主页
    def save_main(self, response):
        title = response.xpath(".//*[@id='content']/h1/span[1]/text()").extract()
        if title:
            title = title[0]
            cwd = os.getcwd() + '/data/'
            if not os.path.exists(cwd):
                os.makedirs(cwd)
            file = cwd + str(title) + '.html'
            with open(file, 'wb') as f:
                f.write(response.text.encode())


    # 处理短评
    def save_short(self, response):
        # 保存页面
        self.page += 1
        dir = response.xpath(".//*[@id='content']/h1/text()").extract()
        if dir:
            cwd = os.getcwd() + '/data/' + dir[0]
        else:
            cwd = os.getcwd() + '/data'
        if not os.path.exists(cwd):
            os.makedirs(cwd)
        file = cwd + '/page' + str(self.page) + '.html'
        with open(file, 'wb') as f:
            f.write(response.text.encode())

        next = response.xpath(".//*[@id='paginator']/a[@class='next']/@href").extract()
        if next:
            next_url = response.url.split('?')[0] + next[0]
            yield Request(next_url, meta={"cookiejar": response.meta['cookiejar']}, callback=self.save_short)


    # 处理长评
    def save_long(self, response):

        # 保存页面
        self.page += 1
        dir = response.xpath(".//*[@id='content']/h1/text()").extract()
        if dir:
            cwd = os.getcwd() + '/data/' + dir[0]
        else:
            cwd = os.getcwd() + '/data'
        if not os.path.exists(cwd):
            os.makedirs(cwd)
        file = cwd + '/page' + str(self.page) + '.html'
        with open(file, 'wb') as f:
            f.write(response.text.encode())

        # 追踪下一页
        next = response.xpath(".//*[@id='content']/div/div[@class='article']/div[@class='paginator']/span[@class='next']/a/@href").extract()
        if next:
            next_url = response.url.split('?')[0] + next[0]
            yield Request(next_url, callback=self.save_long)



