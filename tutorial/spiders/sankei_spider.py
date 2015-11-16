# -*- coding: utf-8 -*-

import sys, traceback
import re
import time
import json
import urllib
import urllib2
from urlparse import urlparse, parse_qs
import scrapy
from tutorial.items import SankeiArticleItem
import MySQLdb
import datetime


class SankeiSpider(scrapy.Spider):
    name = 'sankei'
    allowed_domains = ['sankei.com']
    start_urls = ["http://www.sankei.com/flash/newslist/flash-n1.html",
                  "http://www.sankei.com/affairs/newslist/affairs-n1.html",
                  "http://www.sankei.com/politics/newslist/politics-n1.html",
                  "http://www.sankei.com/world/newslist/world-n1.html",
                  "http://www.sankei.com/economy/newslist/economy-n1.html",
                  "http://www.sankei.com/column/newslist/column-n1.html",
                  "http://www.sankei.com/sports/newslist/sports-n1.html",
                  "http://www.sankei.com/entertainments/newslist/entertainments-n1.html",
                  "http://www.sankei.com/life/newslist/life-n1.html",
                  "http://www.sankei.com/region/newslist/tohoku-n1.html",
                  "http://www.sankei.com/region/newslist/kanto-n1.html",
                  "http://www.sankei.com/region/newslist/chubu-n1.html",
                  "http://www.sankei.com/region/newslist/kinki-n1.html",
                  "http://www.sankei.com/region/newslist/chushikoku-n1.html",
                  "http://www.sankei.com/region/newslist/kyushu-n1.html"
                  ]


    '''
    Starting point
    Retrieve news links from news list pages
    Args:
     response - the response object pertaining to the list page
    '''
    def parse(self, response):
        try:
            #get news list
            sites = response.xpath('//*[@id="primary"]/section/ul/li')

            #get the url of news from the news list
            for site in sites:
                article = SankeiArticleItem()
                article['title'] = site.xpath('a/text()').extract()[0]
                article['date'] = site.xpath('span/time/text()').extract()[0].replace('.','-')
                news_url = ''.join(site.xpath('a/@href').extract()).replace('../..', 'http://www.sankei.com')
                pos_1 = news_url.find("news")
                pos_2 = news_url.find("-n1")
                aid = news_url[pos_1 + 12: pos_2]
                article['url'] = news_url
                article['aid'] = aid
            
                req = scrapy.Request(news_url, callback = self.parse_news)
                req.meta['article'] = article
                yield req

            pos_3 = response.url.find("-n")
            pos_4 = response.url.find(".html")
            page_count = response.url[pos_3 + 2 : pos_4]
            
            #determine whether there has a next page
            if response.xpath('//*[@id="primary"]/section/div//a[@class="pageNext"]'):
                next_url = response.url[: pos_3 + 2] + str(int(page_count) + 1) + response.url[pos_4:]
                yield scrapy.Request(next_url, callback = self.parse)
                
                
        except Exception, e:
            print 'ERROR!!!!!!!!!!!!!  URL :'
            print traceback.print_exc(file = sys.stdout)


    '''
    Retrieve news links from news list pages
    Args:
     response - the response object pertaining to the list page
    '''

    def parse_news(self, response):
        try:
            
            article = response.meta['article']

            article['agency'] = u'産経ニュース'

            content_1 = response.xpath('//*[@id="primary"]/section/article/div[2]/p/text()').extract()
            content = ''.join(content_1)
            article['contents'] = content
            
            news_url = response.url
            if 'sports' in news_url:
                article['category'] = u'スポーツ'
            elif 'life' in news_url:
                article['category'] = u'ライフ'
            elif 'affairs' in news_url:
                article['category'] = u'事件'
            elif 'column' in news_url:
                article['category'] = u'コラム'
            elif 'entertainments' in news_url:
                article['category'] = u'エンタメ'
            elif 'world' in news_url:
                article['category'] = u'国際'
            elif 'economy' in news_url:
                article['category'] = u'経済'
            elif 'politics' in news_url:
                article['category'] = u'政治'
            elif 'region' in news_url:
                article['category'] = u'地方'
            elif 'premium' in news_url:
                article['category'] = u'ホーム'
            elif 'west' in news_url:
                article['category'] = u'WESTトップ'
            else:
                article['category'] = u'その他'
            
            
            pos_1 = response.url.find("-n")
            pos_2 = response.url.find(".html")
            page_count = response.url[pos_1 + 2 : pos_2]
            #determine whether there has a next page
            if response.xpath('//div[@class="pagenator"]'):
                next_url = response.url[: pos_1 + 2] + str(int(page_count) + 1) + response.url[pos_2:]
                req = scrapy.Request(next_url, callback = self.parse_next_page)
                req.meta['article'] = article
                req.meta['contents'] = content
                yield req
            else:
                yield article
            

        except Exception, e:
            print 'Parse_news ERROR!!!!!!!!!!!!!  URL :'+ response.url
            print traceback.print_exc(file = sys.stdout)    



    '''
    Retrieve the contents of next page of a given news
    Args:
     response - the response object pertaining to the next page
    '''
    
    def parse_next_page(self, response):
        try:
            article = response.meta['article']
            content = response.meta['contents']

            content_1 = response.xpath('//*[@id="primary"]/section/article/div[2]/p/text()').extract()
            content_1_1 = ''.join(content_1)

            #merger this page's content with previous content
            content_2 = content + content_1_1
            article['contents'] = content_2


            pos_1 = response.url.find("-n")
            pos_2 = response.url.find(".html")
            page_count = response.url[pos_1 + 2 : pos_2]
            next_page = response.xpath('//*[@id="primary"]/section/div/a[@class="pageNext"]/@href').extract()[0]

            #determine whether there has a next page
            if 'more' in next_page:
                yield article
            else:
                next_url = response.url[: pos_1 + 2] + str(int(page_count) + 1) + response.url[pos_2:]
                req = scrapy.Request(next_url, callback = self.parse_next_page)
                req.meta['article'] = article
                req.meta['contents'] = content_2
                yield req
       
        except Exception, e:
            print 'Parse_next_page ERROR!!!!!!!!!!!!!  :'+response.url
            print traceback.print_exc(file = sys.stdout)
    


