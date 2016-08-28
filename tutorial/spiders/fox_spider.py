# -*- coding: utf-8 -*-
import sys, traceback
import scrapy
from tutorial.items import FoxArticleItem
import MySQLdb
import datetime
import os
sys.path.append(os.path.abspath("/var/www/html/asan/asan/rakes"))
from rake import *


class FoxSpider(scrapy.Spider):
    name = 'fox'
    allowed_domains = ['foxnews.com']
    start_urls = ["http://www.foxnews.com/"]


    '''
    Starting point
    Retrieve news links from news list pages
    Args:
     response - the response object pertaining to the list page
    '''
    def parse(self, response):
        try:
            #get news list
            sites = response.xpath('//section[@id="latest"]/ul/li/a')
            #get the url of news from the news list
            for site in sites:
                article = FoxArticleItem()
                url = site.xpath('@href').extract()
                news_url = ''.join(url)
                #filter out news that don't have transcription
                if 'video' not in news_url:
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
            #get article title
            article['title'] = response.xpath('//h1[@itemprop="headline"]/text()').extract()
            #set agency
            article['agency'] = 'FOX'
            #get url of news
            url = response.url
            article['url'] = url
            #get contents
            if 'entertainment' in response.url:
                content = ''.join(response.xpath('//div[@itemprop="articleBody"]//p/text()').extract())
            else:
                content = ''.join(response.xpath('//div[@class="article-text"]/p/text()').extract())
            #Get keywords
            rake = Rake()
            keywords_list = rake.run(content)
            keywords = '\n'.join(keywords_list)
            article['contents'] = content
            article['keywords'] = keywords
            #get date of news
            date_time = response.xpath('//time[@itemprop="datePublished"]/@datetime').extract()[0]
            date_time_1 = date_time[0:16].replace('T',' ') + ':00'
            article['date'] = date_time_1
            #get category of news
            article['category'] = response.url.split("/")[3]
            yield article

        except Exception, e:
            print 'Parse_news ERROR!!!!!!!!!!!!!  URL :'+ response.url
            print traceback.print_exc(file = sys.stdout)



