# -*- coding: utf-8 -*-

import sys, traceback
import re
import time
import datetime
import json
import urllib
import urllib2
from urlparse import urlparse, parse_qs
import scrapy
from tutorial.items import YahoonewsArticleItem, YahoonewsCommentItem
import MySQLdb
import os
sys.path.append(os.path.abspath("/var/www/html/asan/asan/rakes"))
from jpRake import *


class YahoonewsSpider(scrapy.Spider):
    name = 'yahoonews'
    allowed_domains = ['yahoo.co.jp']
    start_urls = ["http://news.yahoo.co.jp/flash?p=1"]

    '''
    Starting point
    Retrieve news links from news list pages
    Args:
     response - the response object pertaining to the list page
    '''
    def parse(self, response):
        try:
            #get news list
            sites = response.xpath('//*[@id="main"]/div[2]/div/ul/li')

            #get the url of news from the news list
            for site in sites:
                article = YahoonewsArticleItem()
                article['title'] = site.xpath('p[1]/a/text()').extract()[0]
                article['agency'] = site.xpath('p[2]/span/text()').extract()[0]

                url = site.xpath('p[1]/a/@href').extract()
                news_url = ''.join(url)
                article['url'] = news_url

                hour_minute = site.xpath('p/text()').extract()[0]

                if u'日' in hour_minute:
                    pos = hour_minute.find(u'日')
                    hour_minute = hour_minute[pos + 4:]

                hour_minute_1 = hour_minute.replace(u'時',':').replace(u'分',':00')

                pos_1 = news_url.find("=")
                aid = news_url[pos_1 + 1:]
                article['aid'] = aid

                date = aid[0:8]
                date_1 = date[0:4] + '-' + date[4:6] + '-' +date[-2:]
                news_date = date_1.ljust(11) + hour_minute_1
                article['date'] = news_date

                #determine whether there has video in this news
                if site.xpath('p[1]/span/text()'):
                    if u'映像' in site.xpath('p[1]/span/text()').extract()[0]:
                        video = 1
                    else:
                        video = 0
                else:
                    video = 0


                req = scrapy.Request(news_url, callback = lambda response, video = video: self.parse_news(response, video))
                req.meta['article'] = article
                yield req

            pos_2 = response.url.find("=")
            page_count = response.url[pos_2 + 1:]

            #determine whether there has next page
            if int(page_count) < 41:
                next_url = response.url[:pos_2 + 1] + str(int(page_count) + 1)
                yield scrapy.Request(next_url, callback = self.parse)

        except Exception, e:
            print 'ERROR!!!!!!!!!!!!!  URL :'
            print traceback.print_exc(file = sys.stdout)

    '''
    Retrieve news links from news list pages
    Args:
     response - the response object pertaining to the news page
     video - 0 or 1 to show whether there has a video in this news
    '''
    def parse_news(self, response, video):
        time.sleep(1)
        try:

            article = response.meta['article']
            news_url = response.url

            #determine the location of content based on whether there has a video
            if video == 0:
                contents = ' '.join(response.xpath('//p[@class="ynDetailText"]//text()').extract())
                article['category'] = response.xpath('//div[@class="gnSecWrap"]//li[@class="current"]/a/text()').extract()[0]
            else:
                contents = ' '.join(response.xpath('//div[@class="ymuiContainerNopad"]//text()').extract())
                article['category'] = response.xpath('//div[@id="subNav"]/ul/li/a//span[@class="select"]/text()').extract()[0]

            content_1 = ''.join(contents).strip()

            #Get keywords and tagged_text
            rake = jpRake()
            keywords_list = rake.run(content_1)
            keywords = '\n'.join(keywords_list)
            tagged_text = rake.get_tagged_text()

            article['keywords'] = keywords
            article['tagged_text'] = tagged_text
            article['contents'] = content_1
            yield article


            comment_url = response.url.replace('hl?a','cm/main?d') + '&s=create_time&o=desc&p=1'

            yield scrapy.Request(comment_url, callback = lambda response, news_url = news_url: self.get_comment_url(response, news_url))


        except Exception, e:
            print 'Parse_news ERROR!!!!!!!!!!!!!  URL :'+ response.url
            print traceback.print_exc(file = sys.stdout)

    '''
    Retrieve comment plug in page from comment page
    Args:
     response - the response object pertaining to the comment page
     news_url - url of news page
    '''
    def get_comment_url(self, response, news_url):
        time.sleep(1)
        try:

            comment_plugin_keys = response.xpath('//div[@class="news-comment-plugin"]/@data-keys').extract()[0]
            comment_plugin_url = 'http://plugin.news.yahoo.co.jp/v1/comment/full/?origin='\
            + response.url.replace('&p=','&page=') +'&keys=' + comment_plugin_keys + '&full_page_url=' + news_url

            yield scrapy.Request(comment_plugin_url, callback = self.parse_comments)

        except Exception, e:
            print 'Get_comment_url ERROR!!!!!!!!!!!!!  URL :'+ response.url
            print traceback.print_exc(file = sys.stdout)

    '''
    Retrieve comment of a given news
    Args:
     response - the response object pertaining to the page of comment
    '''
    def parse_comments(self, response):
        time.sleep(1)
        try:

            #url_code = urllib.urlopen(response.url).getcode()
            #get comment list
            sites = response.xpath('//li[@class="commentListItem"]')
            #get each comment data in the list
            for site in sites:
                comment = YahoonewsCommentItem()
                comment['username'] = site.xpath('div/article/header/h1/a/text()').extract()[0]
                comment['comment_id'] = site.xpath('@id').extract()[0]
                comment['date'] = site.xpath('div/article/header/time/text()').extract()[0].strip().replace('/','-')
                comment['like_count'] = site.xpath('div/article/footer/ul/li[1]/a/span/em/text()').extract()[0]
                comment['dislike_count'] = site.xpath('div/article/footer/ul/li[2]/a/span/em/text()').extract()[0]
                comment['contents'] = ''.join(site.xpath('div/article/p/span/text()').extract())
                pos_1 = response.url.find('/hl?a=')
                comment['aid'] = response.url[pos_1 + 6:]
                yield comment
                #get reply data if have
                if response.xpath('//li[@class="responseItem repNew"]'):
                    replies = site.xpath('//li[@class="responseItem repNew"]')
                    for reply in replies:
                        comment = YahoonewsCommentItem()
                        comment['username'] = reply.xpath('div/article/header/h1/a/text()').extract()[0]
                        comment['comment_id'] = reply.xpath('@id').extract()[0]
                        comment['date'] = reply.xpath('div/article/header/time/text()').extract()[0].strip().replace('/','-')
                        comment['like_count'] = reply.xpath('div/article/footer/ul/li[1]/a/span/em/text()').extract()[0]
                        comment['dislike_count'] = reply.xpath('div/article/footer/ul/li[2]/a/span/em/text()').extract()[0]
                        comment['contents'] = ''.join(reply.xpath('div/article/p/span/text()').extract())
                        pos_1 = response.url.find('/hl?a=')
                        comment['aid'] = response.url[pos_1 + 6:]
                        yield comment


            pos = response.url.find('page=')
            pos_2 = response.url.find('&keys')
            page_count = response.url[pos + 5: pos_2]
            #determine whether there has next page
            if response.xpath('//*[@id="tabElem0"]/footer//li[@class="next"]/a/@href'):
                page_count = str(int(page_count) + 1)
                next_url = response.url[:pos + 5] + page_count + response.url[pos_2:]
                yield scrapy.Request(next_url, callback = self.parse_comments)


        except Exception, e:
            print 'Parse_comments ERROR!!!!!!!!!!!!!  URL :'+ response.url
            print traceback.print_exc(file = sys.stdout)








