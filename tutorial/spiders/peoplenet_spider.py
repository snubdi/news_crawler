# -*- coding: utf-8 -*-

import sys, traceback
import re
import time
import json
import urllib
import urllib2
from urlparse import urlparse, parse_qs
import scrapy
from tutorial.items import PeoplenetArticleItem,PeoplenetCommentItem
import MySQLdb
import datetime
from scrapy.selector import Selector
from scrapy.http import HtmlResponse

class PeoplenetSpider(scrapy.Spider):
    name = 'peoplenet'
    allowed_domains = ['people.com.cn']
    start_urls = []

    s_date = ''
    page_cnt = 1
    dont_filter = False
    

    '''
    Constructor
    '''
    def __init__(self, search_date = '2015-08-01', *args, **kwargs):
        self.s_date = search_date
        self.start_urls = [self.get_query_url(self.s_date)]
        print self.start_urls


    '''
    Get the query url
    '''
    def get_query_url(self, search_date):
        return 'http://news.people.com.cn/210801/211150/index.js?_=1442260367583'

    
    '''
    Starting point
    Retrieve the news link from json
    Args:
     response - the response object pertaining to the json page
    '''
    def parse(self, response):

        try:
            #Get news.people.com.cn's data
            response = urllib2.urlopen(r'http://news.people.com.cn/210801/211150/index.js?_=1442260367583')
            html_utf = response.read()
            

            #transfer to json format
            js = html_utf.replace('{"items":','')
            js_0 = js.replace(']}',']')
            
            
            #read json
            hjson = json.loads(js_0)
            for items in hjson:
                article = PeoplenetArticleItem()
                article['aid'] = items['id']
                article['date'] = items['date']
                article['title'] = items['title']
                article['url'] = items['url']
                news_url = items['url']


                req = scrapy.Request(news_url, callback = self.parse_news, dont_filter = self.dont_filter)
                req.meta['article'] = article
                yield req
                
        except Exception, e:
            print 'ERROR!!!!!!!!!!!!!  URL :'
            print traceback.print_exc(file = sys.stdout)

            
    '''
    Retrieve the next page's contents of news from the given news
    Args:
     response - the response object pertaining to the next page of a given news
    '''
    def parse_next_page(self, response):

        try:
            #get the contents of last page
            article = response.meta['article']
            content = response.meta['contents']

            #get the contents of this page
            content_1 = response.xpath('//*[@id="p_content"]/p/text()').extract()
            content_1_1 = ''.join(content_1)

            #join the contents of this page to the contents of last page
            content_2 = content + content_1_1
            article['contents'] = content_2

            #determine whether there have next page
            this_page = response.url
            count = this_page[-6:-5]
            count_1 = int(count) + 1
            str_1 = '//*[@id="p_content"]/div[3]/a['+str(count_1)+']'
            
            if response.xpath(str_1):
                str_2 = str_1 + '/@href'
                next_url_0 = response.xpath(str_2).extract()
                pos = this_page.find("/n/")
                next_url = this_page[:pos]+str(next_url_0[0])
                req = scrapy.Request(next_url, callback = self.parse_next_page, dont_filter = self.dont_filter)
                req.meta['article'] = article
                req.meta['contents'] = content_2
                yield req
                
            else:
                yield article
        except Exception, e:
                print 'Parse_next_page ERROR!!!!!!!!!!!!!  :'
                print items
                print traceback.print_exc(file = sys.stdout)
        

    '''
    1: Retrieve the next page of a news if have
    2: Retrieve the comment json page of a given news
    Args:
     response - the response object pertaining to the news page
    '''
    def parse_news(self, response):
        try:
            #get the rest of the article
            article = response.meta['article']
            agency = response.xpath('//*[@id="p_origin"]/a/text()').extract()
            content_1 = response.xpath('//*[@id="p_content"]/p/text()').extract()
            article['agency'] = agency[0]
            

            #get the cagegory of news
            category_url = response.url
            if 'world' in category_url:
                article['category'] = '国际'
            elif 'politics' in category_url:
                article['category'] = '时政'
            elif 'finance' in category_url:
                article['category'] = '财经'
            elif 'money' in category_url:
                article['category'] = '金融'
            elif 'energy' in category_url:
                article['category'] = '能源'
            elif 'legal' in category_url:
                article['category'] = '法治'
            elif 'society' in category_url:
                article['category'] = '社会'
            elif 'hm' in category_url:
                article['category'] = '港澳'
            elif 'pic' in category_url:
                article['category'] = '图片'
            elif 'tw' in category_url:
                article['category'] = '台湾'
            elif 'sports' in category_url:
                article['category'] = '体育'
            elif 'military' in category_url:
                article['category'] = '军事'
            elif 'health' in category_url:
                article['category'] = '健康'
            elif 'theory' in category_url:
                article['category'] = '理论'
            elif 'opinion' in category_url:
                article['category'] = '观点'
            elif 'media' in category_url:
                article['category'] = '传媒'
            elif 'ent' in category_url:
                article['category'] = '娱乐'
            elif 'it.people' in category_url:
                article['category'] = 'IT'
            elif 'env' in category_url:
                article['category'] = '环保'
            elif 'tc' in category_url:
                article['category'] = '通信'
            elif 'homea' in category_url:
                article['category'] = '家电'
            elif 'house' in category_url:
                article['category'] = '房产'
            elif 'ccnews' in category_url:
                article['category'] = '央企'
            elif 'scitech' in category_url:
                article['category'] = '科技'
            elif 'culture' in category_url:
                article['category'] = '文化'
            elif 'yuqing' in category_url:
                article['category'] = '舆情'
            elif 'lady' in category_url:
                article['category'] = '时尚'
            elif 'game' in category_url:
                article['category'] = '游戏'
            elif 'comic' in category_url:
                article['category'] = '动漫'
            elif 'npc.people' in category_url:
                article['category'] = '人大新闻'
            elif 'usa.people' in category_url:
                article['category'] = '美国'
            elif 'shipin' in category_url:
                article['category'] = '食品'
            elif 'edu.people' in category_url:
                article['category'] = '教育'
            elif 'gongyi' in category_url:
                article['category'] = '公益'
            elif 'jiaju' in category_url:
                article['category'] = '家居'
            elif 'qipai' in category_url:
                article['category'] = '棋牌'
            elif 'www.people' in category_url:
                article['category'] = '人民微博'
            else:
                article['category'] = '其他'

            article['contents'] = ''.join(content_1)
            
            if response.xpath('//*[@id="p_content"]/div[3]'):
            
                next_url_0 = response.xpath('//*[@id="p_content"]/div[3]/a[2]/@href').extract()
                pos = category_url.find("/n/")
                next_url = category_url[:pos]+str(next_url_0[0])
                req = scrapy.Request(next_url, callback = self.parse_next_page, dont_filter = self.dont_filter)
                req.meta['article'] = article
                req.meta['contents'] = ''.join(content_1)
                yield req
                 
            
            else:
                yield response.meta['article']


            #get the json url of comments
            comment_url = category_url
            comment_json_url = 'http://bbs1.people.com.cn/api/news.do?action=lastNewsComments&newsId='+article['aid']   
            req = scrapy.Request(comment_json_url, callback = self.parse_comment, dont_filter = self.dont_filter)
            yield req
                        

        except Exception, e:
            print 'Parse_news ERROR!!!!!!!!!!!!!  URL :'+ article['url']
            print traceback.print_exc(file = sys.stdout)
            

    '''
    Retrieve the comment of a given news
    Args:
     response - the response object pertaining to the json page of comment
    '''
    def parse_comment(self, response):

        #get aid of comments
        comment_url = response.url
        aid = comment_url[-8:]
        
        
        #open comment json url
        comment_json_read = urllib2.urlopen(response.url)
        comment_json_0 = comment_json_read.read()
        comment_json_1 = unicode(comment_json_0, 'gbk')
        comment_json_2 = comment_json_1.encode("UTF-8")
        
        
        #transfer to json format
        comment_json_3 = comment_json_2.replace('\\','')
        comment_json_4 = comment_json_3.replace('["{','[{')
        comment_json_5 = comment_json_4.replace('}"]','}]')
        comment_json_6 = comment_json_5.replace('}","{','},{')


        #read json
        comment_json = json.loads(comment_json_6)
        for items in comment_json:
            try:
                comment = PeoplenetCommentItem()
                comment['date'] = items['createTime']
                comment['like_count'] = items['voteYes']
                comment['username'] = items['userNick']
                comment['contents'] = items['postTitle']
                comment['comment_id'] = items['postId']
                comment['aid'] = aid
                yield comment
            except Exception, e:
                print 'Parse_comment ERROR!!!!!!!!!!!!!  :'
                print items
                print traceback.print_exc(file = sys.stdout)
        

        
        
        
            

            
            
            
            
