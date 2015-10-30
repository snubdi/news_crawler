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
            lastday = str(datetime.date.today() - datetime.timedelta(days=1))
            year = lastday[0:4]
            month = lastday[5:7]
            day = lastday[8:10]
            #return 'http://news.163.com/special/0001220O/news_json.js'
            jsurl = 'http://snapshot.news.163.com/wgethtml/http+!!news.163.com!special!0001220O!news_json.js/'+year+'-'+month+'/'+day+'/0.js'
            response = urllib2.urlopen(jsurl)
            html_gbk = response.read()

            # gbk-->utf8
            html_utf = html_gbk.decode("gbk").encode("utf-8")

            # transfer to std json format
            js = self.GetMiddleStr(html_utf,'var data={"category":','],[]]};')
            js_0 = js.replace('[','')
            js_1 = js_0.replace(']','')
            js_2 = js_1.replace('"news":','')
            news_json ='[' + js_2 + ']'

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
            title =  response.xpath('//div[@class="ep-content"]//h1[@id="h1title"]/text()').extract()
            #print title

            agency = response.xpath('//div[@class="ep-content"]//a[@id="ne_article_source"]/text()').extract()
            #print agency

            content = response.xpath('//div[@class="ep-content"]//div[@id="endText"]/p/text()').extract()

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

            #get page source
            pageSource = urllib2.urlopen(news_url).read().decode("gbk").encode("utf-8")
            #get boardId from page source
            c = re.search(r"(?<=boardId = ).+?(?=$)",pageSource,re.M)
            boardID = self.GetMiddleStr(c.group(),'"','",')

            comment_url = comment_url_base + boardID + '/' +  aid + '_1.html'
            print '=============' + comment_url
            req = scrapy.Request(comment_url, callback = self.parse_comment, dont_filter = self.dont_filter)
            req.meta['aid'] = aid
            yield req
        except Exception, e:
            print 'Parse_news ERROR!!!!!!!!!!!!!  URL :'+ article['url']
            print traceback.print_exc(file = sys.stdout)

    def parse_comment(self, response):
        # print '==============================' + response.url
        aid = response.meta['aid']
        res = urllib2.urlopen(response.url)
        # res = urllib2.urlopen(r'http://comment.news.163.com/cache/newlist/news_guonei8_bbs/B18LQ7NT0001124J_1.html')
        #comment json url is encoded by utf-8
        html_utf = res.read()

        check_null = self.GetMiddleStr(html_utf,'var newPostList={"newPosts":',',"')
        if check_null.decode('utf-8') == 'null' : return

        #transfer to std json format
        js = self.GetMiddleStr(html_utf,'var newPostList={"newPosts":','}],')
        news_json = js + '}]'


        hjson = json.loads(news_json, encoding ="utf-8")
        print 'comment size is :' + str(len(hjson))


        for items in hjson:
            try:

                if items.has_key('d'):
                    items.pop('d')

                max_reply = str(len(items))

                for key in items:
                    if key == max_reply:
                        comment_dic = items[key]

                comment = NeteaseCommentItem()
                comment['date'] = comment_dic['t']
                comment['aid'] = aid
                comment['username'] = comment_dic['n']
                comment['contents'] = comment_dic['b']
                comment['like_count'] = comment_dic['v']
                comment['dislike_count'] = comment_dic['a']
                comment['comment_id'] = comment_dic['p']
                yield comment
            except Exception, e:
                print 'Parse_comment ERROR!!!!!!!!!!!!!  :'
                print items
                print traceback.print_exc(file = sys.stdout)

        page = response.url[response.url.rfind('_')+1:response.url.rfind('.html')]
        #print page
        next_comment_url = response.url[:response.url.rfind('_')+1]
        next_comment_url +=str(int(page)+1) + '.html'
        print next_comment_url
        yield scrapy.Request(next_comment_url, callback = self.parse_comment)
