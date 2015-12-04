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
from scrapy.contrib.spiders import CrawlSpider, Rule
from _curses import meta


class MainichiSpider(scrapy.Spider):
    name = 'mainichi'
    allowed_domains = ['mainichi.jp']
    start_urls = ['http://mainichi.jp/']
    dont_filter = False
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

    def get_query_url(self):
        return 'http://mainichi.jp/flash/'

    '''
    Starting point
    Retrieve the news link from the list of search results.
    Args:
     response - the response object pertaining to the search results page
    '''

    def parse(self, response):

        news_list = response.xpath('//div[@class="NewsArticle"]//ul[@class="MaiLink"]/li')
        cnt = 0
        for news_article in news_list:
            try:
                # news link
                news_url = news_article.xpath('.//a/@href').extract()[0]

                # news aid
                news_aid = urlparse(news_url)[2]
                news_aid = news_aid[news_aid.rfind("/") + 1:news_aid.find(".")]

                # news title
                news_title = news_article.xpath('.//a/text()').extract()[0]

                # news date
                #news_date = news_article.xpath('.//span[@class="update"]/text()').extract()[0]

                article = MainichiArticleItem()
                article['url'] = news_url
                article['aid'] = news_aid
                article['title'] = news_title
                #article['date'] = news_date

                req = scrapy.Request(news_url, callback=self.parse_news, dont_filter=self.dont_filter)
                req.meta['article'] = article

                yield req
                cnt += 1
            except Exception, e:
                print 'ERROR!!!!!!!!!!!!!  '
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

        # news date
        #article['date'] = response.xpath('.//div[@class="NewsArticle"]//p[@class="Credit"]/text()').extract()[0]
        news_date = response.xpath('.//meta[@name="firstcreate"]/@content').extract()
        if len(news_date) == 0:
            news_date = ''
        else:
            news_date = time.strptime(news_date[0], '%Y/%m/%d %H:%M:%S')
            news_date = time.strftime('%Y-%m-%d %H:%M:%S', news_date)
        # news content
        news_content = response.xpath(
            './/div[@class="NewsArticle"]//div[@class="NewsBody clr"]/p/text()').extract()
        news_content = ' '.join(news_content).strip()

        article['contents'] = news_content
        article['date'] = news_date
        print article
        yield article

    def parse_date(self, orig_date_str):
        new_time = time.strptime('-'.join(ctime), '%Y-%m-%d-%H-%M')
        return new_time