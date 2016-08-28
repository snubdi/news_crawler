# -*- coding: utf-8 -*-

import sys, traceback
import re
import time
import json
import urllib, urllib2
import time
from datetime import datetime, timedelta
from urlparse import urlparse, parse_qs
import scrapy
from tutorial.items import MainichiArticleItem
import MySQLdb
from scrapy.http import Request, FormRequest
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from _curses import meta
import os
sys.path.append(os.path.abspath("/var/www/html/asan/asan/rakes"))
from jpRake import *


class MainichiSpider(scrapy.Spider):
    name = 'mainichi'
    allowed_domains = ['mainichi.jp']
    start_urls = ['http://mainichi.jp/']
    dont_filter = False
    page = 1
    '''
    Starting point.
    Request login page
    '''

    def __init__(self, *args, **kwargs):

        self.start_urls = [self.get_query_url()]
        super(MainichiSpider, self).__init__(*args, **kwargs)

    '''
    Get the query url
    '''

    @staticmethod
    def get_query_url(page=1):
        return 'http://mainichi.jp/flash/' + str(page)

    '''
    Starting point
    Retrieve the news link from the list of search results.
    Args:
     response - the response object pertaining to the search results page
    '''

    def parse(self, response):

        news_list = response.xpath('//section[@class="newslist"]//ul[@class="list-typeA typeA-date"]/li')
        cnt = 0
        for news_article in news_list:
            try:
                # news link
                news_url = 'http://mainichi.jp' + news_article.xpath('.//a/@href').extract()[0]

                # news aid
                news_aid = urlparse(news_url)[2]
                news_aid = news_aid[news_aid.find("articles/") + 8:news_aid.find(".")].replace('/', '')

                # news title
                news_title = news_article.xpath('./a/text()').extract()
                news_title = ''.join(news_title)
                # news date
                news_date = news_article.xpath('.//span[@class="date"]/text()').extract()[0]

                news_date = time.strptime(filter(unicode.isdigit, news_date), '%Y%m%d%H%M')
                news_date = time.strftime('%Y-%m-%d %H:%M:%S', news_date)

                article = MainichiArticleItem()
                article['url'] = news_url
                article['aid'] = news_aid
                article['title'] = news_title
                article['date'] = news_date

                req = scrapy.Request(news_url, callback=self.parse_news, dont_filter=self.dont_filter)
                req.meta['article'] = article

                yield req
                cnt += 1
            except Exception, e:
                print 'ERROR!!!!!!!!!!!!!  '
                print traceback.print_exc(file=sys.stdout)
                # pass

        print 'read %s articles' % cnt
        print 'read %s page' % self.page
        if self.page < 20:
            self.page += 1
            req = scrapy.Request(self.get_query_url(self.page), callback=self.parse, dont_filter=self.dont_filter)
            yield req
        else:
            return

    '''
    Retrieve the comment count link from a given news article.
    Args:
     response - the response object pertaining to the news article page
    '''

    def parse_news(self, response):

        article = response.meta['article']
        # news content
        news_content = response.xpath(
            './/div[@id="main"]//div[@class="main-text"]/p[@class="txt"]/text()').extract()
        news_content = ' '.join(news_content).strip()

        #Get keywords and tagged_text
        rake = jpRake()
        keywords_list = rake.run(news_content)
        keywords = '\n'.join(keywords_list)
        tagged_text = rake.get_tagged_text()

        article['keywrods'] = keywords
        article['tagged_text'] = tagged_text
        article['contents'] = news_content
        #print article
        yield article

    def parse_date(self, orig_date_str):
        new_time = time.strptime('-'.join(ctime), '%Y-%m-%d-%H-%M')
        return new_time
