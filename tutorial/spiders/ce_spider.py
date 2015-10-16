# -*- coding: utf-8 -*-

import sys, traceback
import re
import time
import json
import urllib
import time
#from datetime import datetime, timedelta
from urlparse import urlparse, parse_qs
import scrapy
from tutorial.items import CeArticleItem
import MySQLdb

class CeSpider(scrapy.Spider):
    name = 'ce'
    allowed_domains = ['ce.cn']
    start_urls = []

    s_date = ''
    e_date = ''
    c_date = ''
    page_cnt = 1
    dont_filter = False
    agency_list = []
    '''
    Constructor
    '''
    def __init__(self, start_date = '', end_date = '',check_date = '', *args, **kwargs):
        self.s_date = start_date
        self.e_date = end_date
        self.c_date = check_date
        self.start_urls = [self.get_query_url(self.page_cnt)]
        super(CeSpider, self).__init__(*args, **kwargs)

    '''
    Get the query url
    '''
    def get_query_url(self, page):

        return 'http://www.ce.cn/2012sy/gd/index_'+str(page)+'.shtml'



    '''
    Starting point
    Retrieve the news link from the list of search results.
    Args:
     response - the response object pertaining to the search results page
    '''
    def parse(self, response):

        news_list= response.xpath('//td[@height="24"]')

        #print news_list
        print 'Page %s' % self.page_cnt
        print 'news_size is :' + str(len(news_list))
        cnt = 0
        for news_article in news_list:
            try:

                #news link
                news_url = news_article.xpath('.//a/@href').extract()[0].replace('../..','http://www.ce.cn')

                #news title
                news_title = news_article.xpath('.//a/text()').extract()[0]

                #news date
                news_date = news_article.xpath('.//span[@class="rq1"]/text()').extract()[0].replace('[','').replace(']','')

                # parse news link to get aid
                parsed_news_url = urlparse(news_url)
                aa = parsed_news_url.path
                aid = aa[len(aa)-23:len(aa)-6]

                # populate article item
                article = CeArticleItem()
                article['aid'] = aid
                article['date'] = news_date
                article['title'] = news_title

                req = scrapy.Request(news_url, callback = self.parse_news, dont_filter = self.dont_filter)

                req.meta['article'] = article
                yield req

                cnt += 1
            except Exception, e:
                print 'ERROR!!!!!!!!!!!!!  URL :'
                print traceback.print_exc(file = sys.stdout)
                #pass

        print 'read %s articles' % cnt

        self.page_cnt += 1
        next_page_url = self.get_query_url(self.page_cnt)
        yield scrapy.Request(next_page_url, callback = self.parse, dont_filter = self.dont_filter)


    '''
    Retrieve the comment count link from a given news article.
    Args:
     response - the response object pertaining to the news article page
    '''
    def parse_news(self, response):

        # populate the rest of the article
        article = response.meta['article']
        article['url'] = response.url

        title = ''
        date = ''

        parsed_response_url = urlparse(response.url)

        #news contents
        contents = ' '.join(response.xpath('//div[@class="TRS_Editor"]//p/text()').extract()).strip()

        #news agency
        agency_ = response.xpath('//div[@class="laiyuan"]//span[@id="articleSource"]/text()').extract()[0]
        agency = agency_[3:len(agency_)]

        #news category
        #category = response.xpath('//a[@href="../../"]//[@class="CurrChnlCls"]').extract()

        #populate agency,contents,category
        article['agency'] = agency
        article['contents'] = contents
        #article['category'] = category

        yield article


