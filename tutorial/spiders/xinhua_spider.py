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
from tutorial.items import *
import MySQLdb
import os
sys.path.append(os.path.abspath("/var/www/html/asan/asan/rakes"))
from ChRake import *


class XinhuaSpider(scrapy.Spider):
    name = 'xinhua'
    allowed_domains = ['xinhuanet.com']
    start_urls = []
    dont_filter = False
    news_category = ''
    '''
    Constructor
    '''
    def __init__(self, categeory = '', *args, **kwargs):

        if categeory == '':
            self.news_category = 'politics'
        else:
            self.news_category = categeory
        self.start_urls = [self.get_query_url(categeory)]
        super(XinhuaSpider, self).__init__(*args, **kwargs)

    '''
    Get the query url
    '''
    def get_query_url(self,news_category):
        _category = {
              '':'http://www.xinhuanet.com/politics/news_politics.xml',
              'politics': 'http://www.xinhuanet.com/politics/news_politics.xml',
              'world': 'http://www.xinhuanet.com/world/news_world.xml',
              'local': 'http://www.xinhuanet.com/local/news_province.xml'
        }
        return _category[news_category]



    '''
    Starting point
    Retrieve the news link from the list of search results.
    Args:
     response - the response object pertaining to the search results page
    '''
    def parse(self, response):

        news_list= response.xpath('//item')
        cnt = 0
        for news_article in news_list:
            try:
                # news link
                news_url = news_article.xpath('.//link/text()').extract()[0]
                #news aid
                news_aid = urlparse(news_url)[2]
                news_aid = "1-" + news_aid[news_aid.find("_")+1:news_aid.find(".")]
                #if news_aid != '1-1116912399':
                #    continue
                # news title
                news_title = news_article.xpath('.//title/text()').extract()[0]

                # news date
                news_date = ''.join(news_article.xpath('./text()').extract())

                article = XinhuaArticleItem()
                article['url'] = news_url
                article['aid'] = news_aid
                article['title'] = news_title
                #
                article['date'] = news_date
                article['category'] = self.news_category

                req = scrapy.Request(news_url, callback = self.parse_news, dont_filter = self.dont_filter)
                req.meta['article'] = article

                yield req

                cnt += 1
            except Exception, e:
                print 'ERROR!!!!!!!!!!!!!  URL :'
                print traceback.print_exc(file = sys.stdout)
                #pass

        print 'read %s articles' % cnt



    '''
    Retrieve the comment count link from a given news article.
    Args:
     response - the response object pertaining to the news article page
    '''
    def parse_news(self, response):

        article = response.meta['article']

        news_date = time.strftime('%Y-%m-%d %H:%M:%S', self.parse_date(article['date']))

        news_content = response.xpath('.//div[@id="center"]/div[@id="article"]/div[@class="article"]//text()').extract()
        news_content = ' '.join(news_content).strip()
        if len(news_content) <5:
            news_content = response.xpath('.//div[@class="main pagewidth"]/div[@id="content"]/p/text()').extract()
            news_content = ' '.join(news_content).strip()

        news_author = response.xpath('.//div[@id="center"]/div[@id="article"]//em[@id="source"]//text()').extract()
        if len(news_author)>0:
            news_author = news_author[0]
        else:
            news_author = response.xpath('.//div[@class="main_tit"]/div[@class="info"]/span[@id="source"]//text()').extract()[0]

        #Get keywords and tagged_text
        rake = ChRake()
        keywords_list = rake.run(news_content)
        keywords = '\n'.join(keywords_list)
        tagged_text = rake.get_tagged_text()

        #Populate
        article['contents'] = news_content
        article['date'] = news_date
        article['agency'] = news_author
        article['keywords'] = keywords
        article['tagged_text'] = tagged_text

        yield article
        #for comment page
        #comment_url = response.xpath('.//div[@id="da-comment"]//a[@target="_blank"]/@href').extract()

        comment_url = 'http://comment.home.news.cn/a/newsComm.do?_ksTS=1444922731622_49&callback=jsonp50&newsId=' + article['aid']

        print comment_url
        #if len(comment_url) >0:
        req = scrapy.Request(comment_url, callback = self.parse_comment, dont_filter = True)
        req.meta['newsId'] = article['aid']
        yield req
        '''comment_check_url = 'http://m.news.naver.com/api/comment/count.json'

        comment_count_data = {
            'gno' : 'news' + article['oid'] + ',' + article['aid']
        }

        req = scrapy.FormRequest(comment_check_url, formdata = comment_count_data, callback = self.parse_comment_count, dont_filter = self.dont_filter)
        req.meta['article'] = article

        return req
        '''

    def parse_comment(self, response):

        json_response = json.loads(response.body[8:-3])

        for comment in json_response['contentAll']:
            comment_time = datetime.fromtimestamp(int(comment['commentTime']/1000))#.strftime('%d %m %Y %H:%M:%S')
            #print comment_time
            comment_item = XinhuaCommentItem()
            comment_item['date'] = comment_time.strftime('%Y-%m-%d %H:%M:%S')
            comment_item['comment_id'] = comment['commentId']
            comment_item['aid'] = response.meta['newsId']
            comment_item['username'] = comment['userId']
            if comment['upAmount'] == None:
                comment_item['like_count'] = 0
            else:
                comment_item['like_count'] = comment['upAmount']
            comment_item['contents'] = comment['content']
            print comment_item
            yield comment_item
    '''
    Parse a date string in the form of '2015.07.10 오후 2:39' and return a time object
    Args:
     orig_date_str - the origina string to parse
    Returns:
     python time object
    '''
    def parse_date(self, orig_date_str):

        # date is in the form of 'Mon,12-Oct-2015 14:35:37 GMT'
        # change to python time object
        _known = {
              'Jan': '01',
              'Feb': '02',
              'Mar': '03',
              'Apr': '04',
              'May': '05',
              'Jun': '06',
              'Jul': '07',
              'Aug': '08',
              'Sep': '09',
              'Oct': '10',
              'Nov': '11',
              'Dec': '12',
        }
        parsed_time= orig_date_str.split(',')[1].split()
        month = parsed_time[0].split('-')[1]
        if month in _known:
            month = _known[month]
        date = parsed_time[0].split('-')[0]+' '+month+' '+parsed_time[0].split('-')[2]
        new_time_str = date + ' ' +parsed_time[1]
        new_time = time.strptime(new_time_str, '%d %m %Y %H:%M:%S')
        return new_time

    '''
    Debug method - update deleted column
    '''

