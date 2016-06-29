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
from tutorial.items import NeteaseArticleItem,NeteaseCommentItem
import MySQLdb

class NeteaseSpider(scrapy.Spider):
    name = '163'
    allowed_domains = ['163.com']
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

        lastday = str(datetime.date.today() - datetime.timedelta(days=1))
        year = lastday[0:4]
        month = lastday[5:7]
        day = lastday[8:10]
        #return 'http://news.163.com/special/0001220O/news_json.js'
        jsurl = 'http://snapshot.news.163.com/wgethtml/http+!!news.163.com!special!0001220O!news_json.js/'+year+'-'+month+'/'+day+'/0.js'
        #jsurl = 'http://news.163.com/special/0001220O/news_json.js'
        return jsurl
    '''
    Starting point.
    Retrieve the news link from the list of search results.
    Args:
     response - the response object pertaining to the search results page
    '''
    def GetMiddleStr(self,content,startStr,endStr):
        startIndex = content.find(startStr)
        if startIndex >= 0:
            startIndex += len(startStr)
        endIndex = content.find(endStr)
        if endIndex < 0:
            endIndex = len(content)
        return content[startIndex: endIndex]


    def parse(self, response):

        try:
            #Get date
            lastday = str(datetime.date.today() - datetime.timedelta(days=2))
            year = lastday[0:4]
            month = lastday[5:7]
            day = lastday[8:10]
            #return 'http://news.163.com/special/0001220O/news_json.js'
            jsurl = 'http://snapshot.news.163.com/wgethtml/http+!!news.163.com!special!0001220O!news_json.js/'+year+'-'+month+'/'+day+'/0.js'
            #jsurl = 'http://news.163.com/special/0001220O/news_json.js'
            response = urllib2.urlopen(jsurl)
            html_gbk = response.read()

            # gbk-->utf8
            html_utf = html_gbk.decode("gbk").encode("utf-8")
            #print html_utf
            '''
            # transfer to std json format
            js = self.GetMiddleStr(html_utf,'var data={"category":','],[]]};')
            js_0 = js.replace('[','')
            js_1 = js_0.replace(']','')
            js_2 = js_1.replace('"news":','')
            js_3 = js_2.replace(',};','')
            news_json ='[' + js_3 + ']'
            '''
            pos_js = html_utf.find('"news":[')
            js = html_utf[pos_js + 9:]
            js_2 = js.replace('[]]};', '')
            js_3 = js_2.replace('[],','')
            js_3 = js_3.replace('],', ',')
            js_4 = js_3.replace('[', '')
            news_json = '[' + js_4[: -2] + ']'
            news_json = news_json.replace('},,', '},')
            print news_json

            # 'c':category  't':news title  'l':url  'p':time
            hjson = json.loads(news_json, encoding ="utf-8")
            print 'news size is :' +str(len(hjson))
            count = 0
            for items in hjson:
                count +=1
                #if count>20: break
                if count<9: continue
                #print items
                for (k, v) in items.items():
                    if k == 'p': news_time = v
                    if k == 'c': category = v
                #news_url = 'http://news.163.com/15/0815/19/B134PU1E000146BE.html'
                news_url = items['l']
                article = NeteaseArticleItem()
                article['url'] = news_url
                article['date'] = news_time
                article['category'] = category
                req = scrapy.Request(news_url, callback = self.parse_news, dont_filter = self.dont_filter)

                req.meta['article'] = article
                yield req
        except Exception, e:
            print 'ERROR!!!!!!!!!!!!!  URL :'
            print traceback.print_exc(file = sys.stdout)



    '''
    Retrieve the comment count link from a given news article.
    Args:
     response - the response object pertaining to the news article page
    '''
    def parse_news(self, response):
        try:
            # populate the rest of the article
            article = response.meta['article']
            aid = str(article['url'])[article['url'].rfind('/')+1:-5]
            title =  response.xpath('//div[@class="post_content_main"]//h1/text()').extract()
            #print title

            agency = response.xpath('//div[@class="post_time_source"]//a[@id="ne_article_source"]/text()').extract()
            #print agency

            content = response.xpath('//div[@class="post_text"]//p/text()').extract()

            article['title'] = title[0]
            article['agency'] = agency[0]
            article['aid'] = aid
            article['contents'] = ''.join(content)

            yield response.meta['article']

            #star comment parsing
            category = article['category']
            news_url = article['url']
            print '=====================' + news_url
            comment_url_base = 'http://comment.news.163.com/cache/newlist/'

            '''
            #get page source
            pageSource = urllib2.urlopen(news_url).read().decode("gbk").encode("utf-8")
            #get boardId from page source
            c = re.search(r"(?<=boardId = ).+?(?=$)",pageSource,re.M)
            boardID = self.GetMiddleStr(c.group(),'"','",')
            '''
            if category == 0:
                boardID = 'news_guonei8_bbs'
            elif category == 1:
                boardID = 'news3_bbs'
            elif category == 2:
                boardID = 'news_shehui7_bbs'
            elif category == 4:
                boardID = 'news3_bbs'
            elif category == 5:
                boardID = 'news_junshi_bbs'
            '''
            comment_url = comment_url_base + boardID + '/' +  aid + '_1.html'
            print '=============' + comment_url
            '''
            #http://comment.news.163.com/api/v1/products/a2869674571f77b5a0867c3d71db5856/threads/BQLQTMO800014SEH/
            #comments/newList?offset=0&limit=30&showLevelThreshold=72&headLimit=1&tailLimit=2&callback=getData&ibc=newspc
            comment_url = 'http://comment.news.163.com/api/v1/products/a2869674571f77b5a0867c3d71db5856/threads/' \
            + aid  + '/comments/newList?offset=0&limit=30&showLevelThreshold=72&headLimit=1&tailLimit=2&callback=getData&ibc=newspc'
            
            req = scrapy.Request(comment_url, callback = self.parse_comment, dont_filter = self.dont_filter)
            req.meta['aid'] = aid
            yield req
        except Exception, e:
            print 'Parse_news ERROR!!!!!!!!!!!!!  URL :'+ article['url']
            print traceback.print_exc(file = sys.stdout)

    def parse_comment(self, response):
        print '&&&&&&&&&&&&&&&&&&$$$$$$$$$$$$$$$$$$$$' + response.url
        aid = response.meta['aid']
        res = urllib2.urlopen(response.url)
        # res = urllib2.urlopen(r'http://comment.news.163.com/cache/newlist/news_guonei8_bbs/B18LQ7NT0001124J_1.html')
        #comment json url is encoded by utf-8
        html_utf = res.read()
        pos_commt_js_start = html_utf.find('\"comments\"')
        pos_commt_js_end = html_utf.find(',\"newListSize\"')
        js = html_utf[pos_commt_js_start + 11: pos_commt_js_end]
        
        if 'channelID' in js:
            return
        
        #comment_dic = {}
        comment_dic = json.loads(js)
        for key, value in comment_dic.items():
            try:
                comment = NeteaseCommentItem()
                comment['comment_id'] = key
                comment_contents = value
                comment['date'] = comment_contents['createTime']
                comment['username'] = comment_contents['user']['nickname']
                comment['contents'] = comment_contents['content']
                comment['like_count'] = comment_contents['vote']
                comment['dislike_count'] = comment_contents['against']
                comment['aid'] = aid
                yield comment
            except Exception, e:
                print 'Parse_comment ERROR!!!!!!!!!!!!!!!!!!!!!!!!:'
                print traceback.print_exc(file = sys.stdout)

