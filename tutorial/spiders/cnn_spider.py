# -*- coding: utf-8 -*-
import sys, traceback
import scrapy
from tutorial.items import CnnArticleItem
import MySQLdb
import datetime


class CnnSpider(scrapy.Spider):
    name = 'cnn'
    allowed_domains = ['cnn.com']
    start_urls = ["http://edition.cnn.com/specials/last-50-stories"]


    '''
    Starting point
    Retrieve news links from news list pages
    Args:
     response - the response object pertaining to the list page
    '''
    def parse(self, response):
        try:
            #get news list
            sites = response.xpath('//ul[@class="cn cn-list-large-horizontal cn--idx-0 cn-"]/li')
            #get the url of news from the news list
            for site in sites:
                article = CnnArticleItem()
                article['title'] = site.xpath('.//span[@class="cd__headline-text"]/text()').extract()
                url = site.xpath('.//h3[@class="cd__headline"]/a/@href').extract()
                news_url = 'http://edition.cnn.com' + ''.join(url)
                #filter out news that don't have transcription
                if 'videos' not in news_url:
                    req = scrapy.Request(news_url, callback = self.parse_news)
                    req.meta['article'] = article
                    yield req

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
            #set agency
            article['agency'] = 'CNN'
            #get url of news
            url = response.url
            article['url'] = url
            #get contents
            content_1 = response.xpath('//p[@class="zn-body__paragraph"]/text()').extract()
            content = ''.join(content_1)
            article['contents'] = content
            #get date of news
            pos = url.find('.com/')
            date = url[pos + 5 : pos + 15].replace('/','-')
            hour_minute = ''.join(response.xpath('//p[@class="update-time"]/text()').extract())
            pos_1 = hour_minute.find('dated')
            hour_minute_1 = hour_minute[pos_1 + 6 : pos_1 + 10]
            hour_minute_2 = hour_minute_1[0 : 2] + ':' + hour_minute_1[2 :] + ':00'
            article['date'] = date.ljust(11) + hour_minute_2
            #get category of news
            article['category'] = response.url.split("/")[-3]
            yield article

        except Exception, e:
            print 'Parse_news ERROR!!!!!!!!!!!!!  URL :'+ response.url
            print traceback.print_exc(file = sys.stdout)



