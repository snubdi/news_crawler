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
from tutorial.items import MsnbcArticleItem
import MySQLdb


class MsnbcSpider(scrapy.Spider):
    name = 'msnbc'
    allowed_domains = ['nbcnews.com']
    start_urls = []

    s_date = ''
    e_date = ''
    c_date = ''
    page_cnt = 1
    dont_filter = True
    agency_list = []
    '''
    Constructor
    '''

    def __init__(self, *args, **kwargs):
        self.start_urls = self.get_query_url()
        super(MsnbcSpider, self).__init__(*args, **kwargs)

    '''
    Get the query url
    '''

    def get_query_url(self):
        return ['http://www.nbcnews.com/news/us-news',
                'http://www.nbcnews.com/news/world',
                'http://www.nbcnews.com/politics',
                'http://www.nbcnews.com/health',
                'http://www.nbcnews.com/tech',
                'http://www.nbcnews.com/science',
                'http://www.nbcnews.com/pop-culture',
                'http://www.nbcnews.com/business',
                'http://www.nbcnews.com/news/investigations',
                'http://www.nbcnews.com/news/latino',
                'http://www.nbcnews.com/news/asian-america',
                'http://www.nbcnews.com/news/nbcblk']

    '''
    Starting point
    Retrieve the news link from the list of search results.
    Args:
     response - the response object pertaining to the search results page
    '''

    def parse(self, response):
        # next page end condition
        news_list = response.xpath('//div[@class="container"]//div[@class="row"]//div[contains(@class,"story-link")]')
        print 'news_size is :' + str(len(news_list))
        cnt = 0
        for news_article in news_list:
            try:
                # naver news link
                news_url = news_article.xpath('.//a/@href').extract()[0]
                if news_url.find("http") == -1:
                    news_url = "http://www.nbcnews.com" + news_url
                # naver news title
                news_title = news_article.xpath('.//h3/text()').extract()[0]

                news_id = news_url[news_url.rfind("/") + 1:]

                article = MsnbcArticleItem()
                article['aid'] = news_id
                article['title'] = news_title
                article['url'] = news_url

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
        # populate the rest of the article
        article = response.meta['article']
        if "/slideshow/" in article['url'] or "/video/" in article['url']:
            return
        elif "http://www.nbcchicago.com/" in article['url'] or "http://www.nbclosangeles.com" in article[
            'url'] or "http://www.nbcnewyork.com" in article['url'] or "http://www.nbcbayarea.com/" in article['url']:
            news_content = response.xpath('.//div[@class="articleText"]/p/text()').extract()
            news_time = response.xpath('.//meta[@http-equiv="last-modified"]/@content').extract()
            news_time = news_time[0].replace("@", " ").replace("PST", "")
        elif "http://www.today.com/" in article['url']:
            news_content = response.xpath('.//div[@class="entry-container"]/p/text()').extract()
            news_time = response.xpath('.//meta[@name="DC.date.issued"]/@content').extract()[0]
            news_time = news_time.replace("T", " ")
            news_time = news_time[:news_time.find(".")]
        else:
            news_content = response.xpath('.//div[@class="article-body"]/p/text()').extract()
            news_time = response.xpath('.//time[@itemprop="datePublished"]/@datetime').extract()[0]
            news_time = news_time.replace("T", " ")
            news_time = news_time[:news_time.find(".")]
        article['contents'] = ' '.join(news_content)
        article['date'] = news_time

        yield article
