import scrapy.cmdline as cmd
import requests
import json
import re
import time
import random


# 记录文件中读取的电影名
movies = []
# 记录文件中的url及通过电影名得到的url
urls = set()

# ***********************************************************从文件中获取电影名**********************************

# 读取文件中的电影名入队列
def read_movies():
    with open('movies.txt', 'r') as f:
        lines = f.readlines()
        for line in lines:
            line = line.strip('\n').strip(' ')
            movies.append(line)

    if len(movies) > 0:
        get_url()

def get_url():
    # 请求该电影的详情页面
    base_url = 'https://api.douban.com/v2/movie/search?q='
    for movie in movies:
        search_url = base_url + movie
        response = requests.get(search_url)
        movie_url = parse(response)
        if re.match(r"https://movie.douban.com/subject/\d+/", movie_url):
            print(movie, movie_url)
            urls.add(movie_url)
        time.sleep(1)
        # break

def parse(response):
    text = json.loads(response.text)
    subjects = text['subjects']
    if len(subjects) > 0:
        subject = subjects[0]
        return subject['alt']


# ***********************************************************从文件中直接获取url**********************************

def read_urls():
    with open('urls.txt', 'r') as f:
        lines = f.readlines()
        for line in lines:
            line = line.strip('\n').strip(' ')
            urls.add(line)

def save_urls():
    with open('start_urls.txt', 'w') as f:
        for url in urls:
            url += '\n'
            f.write(url)
    f.close()

if __name__ == '__main__':
    read_movies()
    read_urls()
    save_urls()
    print(urls)
    cmd.execute("scrapy crawl black_".split())
