# -*- coding: utf-8 -*-

import sys, traceback
import re
import time
import json
import urllib
from urlparse import urlparse, parse_qs
import scrapy
from tutorial.items import DaumArticleItem
from urllib import quote, unquote
import MySQLdb
#import datetime

class DaumSpider(scrapy.Spider):
    name = 'daum'
    allowed_domains = ['daum.net']
    start_urls = []

    s_date = ''
    e_date = ''
    page_cnt = 1
    dont_filter = False

    '''
    Constructor
    '''
    def __init__(self, start_date = '', end_date = '', keyword ='', *args, **kwargs):

        #self.s_date = str(datetime.date.today())
        self.s_date = start_date
        self.e_date = end_date
        self.k_word = keyword
        #self.c_date = str(datetime.date.today() - datetime.timedelta(days=1))

        self.start_urls = [self.get_query_url(self.s_date, self.e_date, self.k_word)]
        super(DaumSpider, self).__init__(*args, **kwargs)


    '''
    Get the query url
    '''
    def get_query_url(self, start_date, end_date, keyword):
        #qs = {'query': keyword}

        return 'http://search.daum.net/search?w=news' \
                + '&q=' + str(keyword).decode('utf8').encode('euc-kr') \
                + '&period=u' \
                + '&sd=' + start_date +'000000' \
                + '&ed=' + end_date + '235959' \
                + '&cluster_page=1'



    '''
    Starting point
    Retrieve the news link from the list of search results.
    Args:
     response - the response object pertaining to the search results page
    '''
    def parse(self, response):


        start_rec = 1
        total_rec = 2

        #print 'Record %s of %s' % (start_rec, total_rec)

        if start_rec < total_rec:

            #print 'Page %s' % self.page_cnt

            #cnt = 0
            #news_list = response.css('div.coll_cont > li > div.wrap_cont')
            news_list = response.xpath('//*[@id="clusterResultUL"]/li')
            #news_list_related = response.xpath('*[@id="clusterResultUL"]//div[@class="wrap_cont"]/div/div[@class="related_news"]/dl/dd')
            news_list_related = response.xpath('//*[@id="clusterResultUL"]/li/div[2]/div/div[2]//dl/dd')
            for news_article in news_list:
                try:
                    article = DaumArticleItem()
                    # news agency
                    article['agency'] = news_article.xpath('.//div[2]/div/span/text()[2]').extract()[0]

                    # news link
                    news_url = news_article.xpath('.//a/@href').extract()[0]

                    # news_title
                    article['title'] = ''.join(news_article.xpath('.//a/text()').extract())

                    # news date
                    article['date'] = news_article.xpath('.//div[2]/div/span[1]/text()[1]').extract()[0]

                    article['start_date'] = self.s_date
                    article['end_date'] = self.e_date
                    article['keyword'] = self.k_word
                    article['url'] = news_url

                    yield article
                except Exception, e:
                    print 'ERROR!!!!!!!!!!!!!  URL :'
                    print traceback.print_exc(file = sys.stdout)
                    pass
            #Parse related news
            for news_article_related in news_list_related:
                try:
                    article = DaumArticleItem()
                    # news agency
                    article['agency'] = news_article_related.xpath('.//span/text()[2]').extract()[0].strip()
                    # news link
                    news_url = news_article_related.xpath('a/@href').extract()[0]
                    #news_url = news_article_related.xpath('.//div[@class="wrap_cont"]/div/div[@class="related_news"]/dl/dd/a/@href').extract()[0]
                    # news_title

                    #article['title'] = ''.join(news_article_related.xpath('.//div[@class="wrap_cont"]/div/div[@class="related_news"]/dl/dd/a/text()').extract())
                    article['title'] = ''.join(news_article_related.xpath('a/text()').extract())

                    article['date'] = news_article_related.xpath('.//span/text()[1]').extract()[0]

                    article['start_date'] = self.s_date
                    article['end_date'] = self.e_date
                    article['keyword'] = self.k_word
                    article['url'] = news_url
                    article['related_news'] = 'Y'


                    yield article
                except Exception, e:
                    print 'ERROR!!!!!!!!!!!!!  URL :'
                    print traceback.print_exc(file = sys.stdout)
                    pass

