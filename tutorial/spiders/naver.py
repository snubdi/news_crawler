# -*- coding: utf-8 -*-

import sys, traceback
import re
import time
import json
import urllib
from urlparse import urlparse, parse_qs
import scrapy
from tutorial.items import Naver2ArticleItem
from urllib import quote, unquote
import MySQLdb
#import datetime

class NaverSpider(scrapy.Spider):
    name = 'naver'
    allowed_domains = ['naver.com']
    start_urls = []

    s_date = ''
    e_date = ''
    page_cnt = 1
    #dont_filter = False

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
        super(NaverSpider, self).__init__(*args, **kwargs)


    '''
    Get the query url
    '''
    def get_query_url(self, start_date, end_date, keyword):
        #qs = {'query': keyword}

        '''
        return 'http://news.naver.com/main/search/search.nhn' \
                + '?query=%B1%B9%B9%E6%BA%CE' \
                + '&startDate=' + start_date \
                + '&endDate=' + end_date \
                + '&page=' + str(page) \
        '''

        '''
        article = NaverArticleItem()
        article['start_date'] = start_date
        article['end_date'] = end_date
        article['keyword'] = keyword

        '''

        return 'http://news.naver.com/main/search/search.nhn' \
                + '?query=' + keyword.decode('utf8').encode('euc-kr') \
                + '&startDate=' + start_date \
                + '&endDate=' + end_date \
                + '&page=1'


    '''
    Starting point
    Retrieve the news link from the list of search results.
    Args:
     response - the response object pertaining to the search results page
    '''
    def parse(self, response):

        '''
        # determine whether to go ahead with parse or not
        result_header = response.css('div.result_header > span.result_num').xpath('.//text()').extract()[0].strip()
        res = re.match(u'^\((\d+).*?(\d+).*?\)$', result_header, re.M|re.S)

        start_rec = int(res.group(1))
        total_rec = int(res.group(2))

        print 'Record %s of %s' % (start_rec, total_rec)
        '''
        if 1 < 2:

            #print 'Page %s' % self.page_cnt

            #cnt = 0
            print response.xpath('//div[@class="srch_result_area"]//ul[@class="srch_lst"]/li')
            news_article = response.xpath('//div[@class="srch_result_area"]//ul[@class="srch_lst"]/li')

            try:
                article = Naver2ArticleItem()
                # news agency
                article['agency'] = news_article.xpath('//div[@class="info"]//span[@class="press"]/text()').extract()[0]
                # naver news link

                news_url = news_article.xpath('div/a/@href').extract()[0]
                article['url'] = news_url
                # news title
                article['title'] = ''.join(news_article.xpath('//div[@class="ct"]//text()').extract())
                # news date
                article['date'] = news_article.xpath('//div[@class="info"]//span[@class="time"]/text()').extract()[0].replace('.','-')
                # start date
                article['start_date'] = self.s_date
                # end date
                article['end_date'] = self.e_date
                # key word
                article['keyword'] = self.k_word
                yield article
            except Exception, e:
                print 'ERROR!!!!!!!!!!!!!  URL :' + news_url
                print traceback.print_exc(file = sys.stdout)
                pass

            related_article = response.xpath('//div[@class="related_group"]/ul/li')
            try:
                article = Naver2ArticleItem()
                # news agency
                article['agency'] = related_article.xpath('//p[@class="info"]//span[@class="press"]/text()').extract()[0]
                # news link

                news_url = related_article.xpath('a/@href').extract()[0]
                article['url'] = news_url
                # news title
                article['title'] = ''.join(related_article.xpath('a//text()').extract())
                # news date
                article['date'] = related_article.xpath('//p[@class="info"]//span[@class="time"]/text()').extract()[0].replace('.','-')
                # start date
                article['start_date'] = self.s_date
                # end date
                article['end_date'] = self.e_date
                # key word
                article['keyword'] = self.k_word
                # related news
                article['related_news'] = 'Y'
                yield article

            except Exception, e:
                print 'ERROR!!!!!!!!!!!!!  URL :' + news_url
                print traceback.print_exc(file = sys.stdout)
                pass






