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
from tutorial.items import AsahiArticleItem
import MySQLdb
from scrapy.http import Request, FormRequest
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.contrib.spiders import CrawlSpider, Rule
from _curses import meta
import os
sys.path.append(os.path.abspath("/var/www/html/asan/asan/rakes"))
from jpRake import *

class AsahiSpider(scrapy.Spider):
    name = 'asahi'
    allowed_domains = ['asahi.com']
    start_urls = ['http://www.asahi.com/']
    headers = {
               "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
               "Accept-Encoding": "gzip, deflate",
               "Accept-Language": "zh-CN,zh;q=0.8,en;q=0.6",
               "Cache-Control": "max-age=0",
               "Connection": "keep-alive",
               "Content-Type": "application/x-www-form-urlencoded",
               "Referer": "https://digital.asahi.com/login/",
               "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.86 Safari/537.36"
               }


    '''
    Starting point.
    Request login page
    '''
    def start_requests(self):
        return [Request("https://digital.asahi.com/login/", meta = {'cookiejar' : 1}, callback = self.post_login)]


    '''
    Submit form data and login
    '''
    def post_login(self, response):
        print 'login~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'

        return [FormRequest.from_response(response,
                                          meta = {'cookiejar': response.meta['cookiejar']},
                                          headers = self.headers,
                                          formdata = {
                                                      'jumpUrl': 'http://www.asahi.com/?',
                                                      'ref': '',
                                                      'login_id': 'snubdi@gmail.com',
                                                      'login_password': 'snubdi38511'},
                                          callback = self.after_login)]

    '''
    Request to news list page after login
    '''
    def after_login(self, response):
        print 'login@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@'
        print response.url
        date = time.strftime('%Y%m%d', time.localtime(time.time()))
        #news list url based on date
        url_1 = 'http://www.asahi.com/shimen/' + date + 'ev/index_tokyo_list.html'
        url_2 = 'http://www.asahi.com/shimen/' + date + '/index_tokyo_list.html'
        #url_1 = 'http://www.asahi.com/shimen/20151124ev/index_tokyo_list.html'
        #url_2 = 'http://www.asahi.com/shimen/20151124/index_tokyo_list.html'


        yield scrapy.Request(url_1, headers = self.headers, meta = {'cookiejar': response.meta['cookiejar']}, callback = self.parse)
        yield scrapy.Request(url_2, headers = self.headers, meta = {'cookiejar': response.meta['cookiejar']}, callback = self.parse)


    '''
    Retrieve news link from news list page
    Args:
     response - the response object pertaining to the news list page
    '''
    def parse(self, response):
        try:
            print '########################################################'
            print response.url

            sites = response.xpath('//div[@class="Section"]//li')

            for site in sites:
                article = AsahiArticleItem()
                #get news url
                news_url = 'http://digital.asahi.com' + site.xpath('a/@href').extract()[0]
                print news_url
                article['url'] = news_url

                req = scrapy.Request(news_url, headers = self.headers, meta = {'cookiejar': response.meta['cookiejar']}, callback = self.parse_news)
                req.meta['article'] = article
                yield req


        except Exception, e:
            print 'ERROR!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!   URL :'
            print traceback.print_exc(file = sys.stdout)


    '''
    Retrieve news contents of news
    Args:
     response - the response object pertaining to the news page
    '''
    def parse_news(self, response):
        try:
            article = response.meta['article']
            #agency of news
            article['agency'] = u'朝日新聞'

            #title of news
            article['title'] = response.xpath('//*[@id="MainInner"]/div[1]/div/h1/text()').extract()[0]

            pos_1 = response.url.find('cles')
            pos_2 = response.url.find('.html')
            #get aid of news
            article['aid'] = response.url[pos_1 + 5: pos_2]

            date = response.xpath('//*[@id="MainInner"]/div[1]/div/p/text()').extract()[0]
            #get date of news
            article['date'] = date.replace(u'年','-').replace(u'月','-').replace(u'日',' ').replace(u'時',':').replace(u'分',':')
            #get contents of news
            contents = ''.join(response.xpath('//div[@class="ArticleText"]//text()').extract()).strip()
            #article['contents'] = ''.join(response.xpath('//div[@class="ArticleText"]//text()').extract()).strip()
            #Get keywords and tagged_text
            rake = jpRake()
            keyowrds_list = rake.run(contents)
            keywords = '\n'.join(keywords_list)
            tagged_text = rake.get_tagged_text()

            article['keywords'] = keywords
            article['tagged_text'] = tagged_text
            article['contents'] = contents

            yield article

        except Exception, e:
            print 'Parse_news ERROR!!!!!!!!!!!!!  URL :'+ response.url
            print traceback.print_exc(file = sys.stdout)



