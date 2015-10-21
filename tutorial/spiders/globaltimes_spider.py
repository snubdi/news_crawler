# -*- coding: utf-8 -*-

import sys, traceback
import re
import time
import json
import urllib
import urllib2
from urlparse import urlparse, parse_qs
import scrapy
from tutorial.items import GlobaltimesArticleItem,GlobaltimesCommentItem
import MySQLdb
import datetime
from _elementtree import Comment
from pycparser.c_ast import Default

class GlobaltimesSpider(scrapy.Spider):
    name = 'globaltimes'
    allowed_domains = ['huanqiu.com']
    start_urls = ["http://roll.huanqiu.com/topnews.html",
                  "http://roll.huanqiu.com/topnews_2.html",
                  "http://roll.huanqiu.com/topnews_3.html",
                  "http://roll.huanqiu.com/topnews_4.html",
                  "http://roll.huanqiu.com/topnews_5.html",
                  "http://roll.huanqiu.com/topnews_6.html",
                  "http://roll.huanqiu.com/topnews_7.html",
                  "http://roll.huanqiu.com/topnews_8.html",
                  "http://roll.huanqiu.com/topnews_9.html",
                  "http://roll.huanqiu.com/topnews_10.html",
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
            sites = response.xpath('//*[@id="panesT"]/div[1]/div[1]/ul/li')

            #get the url of news from the news list
            for site in sites:
                article = GlobaltimesArticleItem()
                article['title'] = site.xpath('a/text()').extract()
                article['date'] = site.xpath('em/text()').extract()
                url = site.xpath('a/@href').extract()
                news_url = ''.join(url)
                
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

            agency = response.xpath('//*[@id="source_baidu"]/a/text()').extract()
            article['agency'] = agency[0]

            url = response.url
            aid = url[-12:-5]
            article['aid'] = aid
            article['url'] = url

            content_1 = response.xpath('//*[@id="text"]/p/text()').extract()
            content = ''.join(content_1)
            article['contents'] = content
            
            category = response.xpath('//*[@id="topC"]/div[1]/a[2]/text()').extract()
            category_1 = category[0]
            article['category'] = category_1

            #determine whether there has a next page
            if response.xpath('//*[@id="pages"]/a[2]/@href'):
                
                next_url = response.xpath('//*[@id="pages"]/a[2]/@href').extract()
                next_url_1 = ''.join(next_url)
                req = scrapy.Request(next_url_1, callback = self.parse_next_page)
                req.meta['article'] = article
                req.meta['contents'] = ''.join(content_1)
                yield req
                
            
            else:
                yield response.meta['article']

            
            #get json url of comments
            get_url = 'http://commentn.huanqiu.com/api/v2/async?a=comment&m=source_info&appid=e8fcff106c8f&sourceid='+aid+'&url='+url
            get_url_read = urllib2.urlopen(get_url)
            get_id = get_url_read.read()
            json_id = get_id[45:69]
            comment_json_url = 'http://commentn.huanqiu.com/api/v2/async?a=comment&m=comment_list&sid='+json_id+'&n=15&p=1&appid=e8fcff106c8f&callback=comment_list'
            comment_req = scrapy.Request(comment_json_url, callback = self.parse_comment)
            comment_req.meta['aid'] = aid
            yield comment_req
            
            
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

            content_1 = response.xpath('//*[@id="text"]/p/text()').extract()
            content_1_1 = ''.join(content_1)

            #merger this page's content with previous content
            content_2 = content + content_1_1
            article['contents'] = content_2
            

            this_page = response.url
            count = this_page[-6:-5]
            
            count_1 = int(count)+1
            
            str_1 = '//*[@id="pages"]/a['+str(count_1)+']/text()'
            str_2 = '//*[@id="pages"]/a['+str(count_1)+']/@href'
            count_2 = response.xpath(str_1).extract()

            #determine whether there has a next page
            if u'\u4e0b\u4e00\u9875' in count_2:
                yield article

            else:
                next_url = response.xpath(str_2).extract()
                next_url_1 = str(next_url[0])
                req = scrapy.Request(next_url_1, callback = self.parse_next_page)
                req.meta['article'] = article
                req.meta['contents'] = content_2
                yield req
       
        except Exception, e:
            print 'Parse_next_page ERROR!!!!!!!!!!!!!  :'+response.url
            print traceback.print_exc(file = sys.stdout)


    '''
    Retrieve the comment of a given news
    Args:
     response - the response object pertaining to the json page of comment
    '''
    def parse_comment(self, response):
        aid = response.meta['aid']
        json_read = urllib2.urlopen(response.url)
        json_content = json_read.read()

        
        if len(json_content) > 70:
            
            json_content_0 = json_content.replace(';try{ comment_list({"code":22000,"msg":"success","data":[','[')
            json_content_1 = json_content_0.replace(']}); }catch(e){}',']')
            json_content_2 = json_content_1.replace('"user":{','"user":[{')
            json_content_3 = json_content_2.replace('}}','}]}')

        
            #read json
            comment_json = json.loads(json_content_3)

            for items in comment_json:
                try:
                    comment = GlobaltimesCommentItem()
                    comment['aid'] = aid
                    comment['comment_id'] = items['_id']
                    comment['like_count'] = items['n_active']
                    comment['contents'] = items['content']
                    comment_time = time.localtime(items['ctime'])
                    comment_time_1 = time.strftime('%Y-%m-%d %H:%M:%S', comment_time)
                    comment['date'] = comment_time_1
                    comment['username'] = items['user'][0].get('nickname')
                
                
                    yield comment
                except Exception, e:
                    print 'Parse_comment ERROR!!!!!!!!!!!!!  :'
                    print items
                    print traceback.print_exc(file = sys.stdout)

        else:
            print 'no comments'
        
        
        
        




            
