# -*- coding: utf-8 -*-

import sys, traceback
import re
import time
import json
import urllib
import time
from datetime import datetime, timedelta
from urlparse import urlparse, parse_qs
import scrapy
from tutorial.items import *
import MySQLdb


class YomiuriSpider(scrapy.Spider):
    name = 'yomiuri'
    start_urls = []
    dont_filter = False
    '''
    Constructor
    '''

    def __init__(self, *args, **kwargs):

        self.start_urls = [self.get_query_url()]
        super(YomiuriSpider, self).__init__(*args, **kwargs)

    '''
    Get the query url
    '''

    def get_query_url(self):
        return 'http://www.yomiuri.co.jp/latestnews/'

    '''
    Starting point
    Retrieve the news link from the list of search results.
    Args:
     response - the response object pertaining to the search results page
    '''

    def parse(self, response):

        news_list = response.xpath('//ul[@class="list-common list-common-latest"]/li')
        cnt = 0
        for news_article in news_list:
            try:
                # news link
                news_url = news_article.xpath('.//a/@href').extract()[0]
                # news aid
                news_aid = urlparse(news_url)[2]
                news_aid = news_aid[news_aid.rfind("/")+1:news_aid.find(".")]

                # news title
                news_title = news_article.xpath('.//span[@class="headline"]/text()').extract()[0]

                # news date
                news_date = news_article.xpath('.//span[@class="update"]/text()').extract()[0]

                article = YomiuriArticleItem()
                article['url'] = news_url
                article['aid'] = news_aid
                article['title'] = news_title
                article['date'] = news_date

                req = scrapy.Request(news_url, callback=self.parse_news, dont_filter=self.dont_filter)
                req.meta['article'] = article

                yield req
                cnt += 1
            except Exception, e:
                print 'ERROR!!!!!!!!!!!!!  URL :'
                print traceback.print_exc(file=sys.stdout)
                # pass

        print 'read %s articles' % cnt

    '''
    Retrieve the comment count link from a given news article.
    Args:
     response - the response object pertaining to the news article page
    '''

    def parse_news(self, response):

        article = response.meta['article']
        news_date = time.strftime('%Y-%m-%d %H:%M:%S', self.parse_date(article['date']))
        # news content
        news_content = response.xpath('.//div[@class="article text-resizeable"]//p[@itemprop="articleBody"]/text()').extract()
        news_content = ' '.join(news_content).strip()

        article['contents'] = news_content
        article['date'] = news_date
        print article
        yield article

    '''
    Parse a date string in the form of '2015.07.10 오후 2:39' and return a time object
    Args:
     orig_date_str - the origina string to parse
    Returns:
     python time object
    '''

    def parse_date(self, orig_date_str):

        ctime = re.findall(r"\d+\.?\d*", orig_date_str)
        new_time = time.strptime('-'.join(ctime), '%Y-%m-%d-%H-%M')
        return new_time

