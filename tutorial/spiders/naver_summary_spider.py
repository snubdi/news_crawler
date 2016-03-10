
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
from tutorial.items import NaverSummaryItem, NaverSummaryDeletedItem
import MySQLdb
import langid


class NaverSummarySpider(scrapy.Spider):
    name = 'naver_summary'
    allowed_domains = ['naver.com']
    start_urls = ['']
    s_date = ''
    e_date = ''
    c_date = ''
    page_cnt = 1
    dont_filter = False
    agency_list = []
    sid1 = [100, 101, 102, 103, 104, 105, 106, 107]
    '''
    Constructor
    '''
    def __init__(self, start_date='', end_date='', check_date='', *args, **kwargs):
        self.s_date = start_date
        self.e_date = end_date
        self.c_date = check_date
        if check_date == '':
            yesterday = datetime.now() + timedelta(days=-0)
            self.c_date = yesterday.strftime("%Y%m%d")
            print self.c_date
        self.start_urls = [self.get_query_url(self.c_date, self.page_cnt, self.sid1[0]),
                           self.get_query_url(self.c_date, self.page_cnt, self.sid1[1]),
                           self.get_query_url(self.c_date, self.page_cnt, self.sid1[2]),
                           self.get_query_url(self.c_date, self.page_cnt, self.sid1[3]),
                           self.get_query_url(self.c_date, self.page_cnt, self.sid1[4]),
                           self.get_query_url(self.c_date, self.page_cnt, self.sid1[5]),
                           self.get_query_url(self.c_date, self.page_cnt, self.sid1[6]),
                           self.get_query_url(self.c_date, self.page_cnt, self.sid1[7])
                           ]
        super(NaverSummarySpider, self).__init__(*args, **kwargs)
        

    '''
    Get the query url
    '''
    def get_query_url(self, check_date, page, sid1):
        return 'http://news.naver.com/main/list.nhn?' + 'sid1=' + str(sid1) + '&mid=sec&mode=LSD&' \
                + '&date=' + check_date \
                + '&page=' + str(page) \
                

    '''
    Starting point
    Retrieve the news link from the list of search results.
    Args:
     response - the response object pertaining to the search results page
    '''
    def parse(self, response):
        # next page end condition
        next_button = response.xpath('//td[@class="content"]//div[@class="paging"]/a[@class="next"]')
        # if self.page_cnt >10:
        if len(next_button) == 0 and self.page_cnt >= int(response.xpath('//td[@class="content"]//div[@class="paging"]/a/text()').extract()[-1]):
            print "!!!!!!!!!!!!!get max page" + str(self.page_cnt)
            return
        # get news list
        news_list = response.xpath('//td[@class="content"]//div[@id="main_content"]//li')
        print 'Page %s' % self.page_cnt
        print 'news_size is :' + str(len(news_list))
        cnt = 0
        
        for news_article in news_list:
            try:                
                # news agency
                agency = news_article.xpath('.//span[@class="writing"]/text()').extract()[0]
                # selected agency
                if agency not in [u'경향신문', u'중앙일보', u'한겨레', u'동아일보', u'조선일보',
                                  u'연합뉴스', u'데일리안', u'오마이뉴스', u'매일경제', u'한국경제',
                                  u'한국일보', u'국민일보', u'서울신문', u'노컷뉴스']:
                    continue
                # naver news link
                news_url = news_article.xpath('.//a/@href').extract()[0]
                print '@@@@@@@@@@@@@@@@@@@@@'
                print news_url
                pos_aid = news_url.find('aid=')
                aid = news_url[pos_aid + 4:]                
                # naver news title
                news_title = ''.join(news_article.xpath('.//a/text()').extract()).strip()
                news_title = news_title.replace(u'(종합)', '').replace(u'(종합2보)', '')
                # naver news date
                news_date = news_article.xpath('.//span[@class="date"]/text()').extract()[0]
                # parse news link to get aid and oid
                parsed_news_url = urlparse(news_url)               
                # host_part = parsed_news_url[1]
                query_string = parse_qs(parsed_news_url[4])
                
                summary_1 = ''.join(news_article.xpath('dl/dd/text()').extract()).strip()
                
                delete_part = re.compile(r'\[.*?\]')
                summary_1 = delete_part.sub('', summary_1)
                news_title_1 = delete_part.sub('', news_title)                
                delete_part_2 = re.compile(r'\(.*?\)')
                summary = delete_part_2.sub('', summary_1)
                news_title_2 = delete_part_2.sub('', news_title_1)
                delete_part_3 = re.compile(r'\<.*?\>')
                news_title = delete_part_3.sub('', news_title_2)
                
                if agency == u'연합뉴스':
                    print '####################################################################'
                    pos_1 = summary.find(u'=')
                    summary = summary[pos_1 + 1:]
                          
                elif agency == u'오마이뉴스':
                    summary = summary.replace(u'오마이뉴스', '').replace(u'▲', '')
                
                if 'sid1=100' in response.url:
                    category = u'politics'
                elif 'sid1=101' in response.url:
                    category = u'economy'
                elif 'sid1=102' in response.url:
                    category = u'society'
                elif 'sid1=103' in response.url:
                    category = u'life'
                elif 'sid1=104' in response.url:
                    category = u'world'
                elif 'sid1=105' in response.url:
                    category = u'it'
                elif 'sid1=106' in response.url:
                    category = u'entertainment'
                elif 'sid1=107' in response.url:
                    category = u'sports'
                    pos_aid = news_url.find('article_id=')
                    aid = news_url[pos_aid + 11:]
                    pos_oid_1 = news_url.find('office_id=')
                    pos_oid_2 = news_url.find('&article_id')
                    oid = news_url[pos_oid_1 + 10: pos_oid_2]
                    news_url = 'http://sports.news.naver.com/general/news/read.nhn?oid=' + oid + '&aid=' + aid
                    
                title_filt = [u'그래픽', u'카메라뉴스', u'카드뉴스', u'부고', u'부음',
                              u'사진', u'영상', u'포토', u'인사', u'▲', u'◇', u'◆',
                              u'경향신문', u'중앙일보', u'한겨레', u'동아일보', u'조선일보',
                              u'연합뉴스', u'데일리안', u'오마이뉴스', u'매일경제', u'한국경제',
                              u'한국일보', u'국민일보', u'서울신문', u'뉴데일리', u'노컷뉴스',
                              u'한경', u'매경', 'MBN', 'WOW', u'머니투데이', u'더벨', u'퀴즈',
                              u'?', u'속보']
                
                if any(t in news_title for t in title_filt):
                    print '%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%'
                    article_deleted = NaverSummaryDeletedItem()
                    article_deleted['aid'] = aid
                    # article['oid'] = query_string['oid'][0]
                    article_deleted['agency'] = agency
                    article_deleted['date'] = news_date
                    article_deleted['title'] = news_title
                    article_deleted['summary'] = summary
                    article_deleted['url'] = news_url
                    article_deleted['category'] = category
                    req_dele = scrapy.Request(news_url, callback=self.parse_news_deleted)
                    article_deleted['referer'] = response.url
                    req_dele.meta['article_deleted'] = article_deleted
                    yield req_dele
                    
                else:
                    
                    # populate article item
                    # if query_string['oid'][0] != '32':
                    #    continue                
                    article = NaverSummaryItem()
                    article['aid'] = aid
                    # article['oid'] = query_string['oid'][0]
                    article['agency'] = agency
                    article['date'] = news_date
                    article['title'] = news_title
                    article['summary'] = summary
                    article['summary_unfilt'] = summary_1
                    article['url'] = news_url
                    article['category'] = category
                    # article['position'] = news_position
                    req = scrapy.Request(news_url, callback=self.parse_news)
                    article['referer'] = response.url
                    req.meta['article'] = article
                    yield req
                
                cnt += 1
            except Exception, e:
                print 'ERROR!!!!!!!!!!!!!  URL :' 
                print traceback.print_exc(file=sys.stdout)
                # pass

        print 'read %s articles' % cnt
        
        self.page_cnt += 1
        pos = response.url.find('page=')
        next_page_url = response.url[:pos + 5] + str(self.page_cnt)
        yield scrapy.Request(next_page_url, callback=self.parse, dont_filter=self.dont_filter)
    
    def parse_news(self, response):
        
        # populate the rest of the article
        article = response.meta['article']
        agency = response.meta['article']['agency']
        parsed_response_url = urlparse(response.url)
        host_part = parsed_response_url[1]

        if host_part == 'entertain.naver.com':
            contents = ' '.join(response.xpath('//*[@id="articeBody"]/text()').extract()).strip()
        elif 'sports' in response.url:
            # contents = ' '.join(response.css('div.article > div').xpath('.//text()').extract()).strip()
            contents = ' '.join(response.xpath('//div[@id="newsEndContents"]/text()').extract()).strip()
        else:
            contents = ' '.join(response.xpath('//div[@id="articleBodyContents"]/text()').extract()).strip()
        
        if u'영상' in contents:
            return
        '''
        if any(t in contents for t in contents_filts_1):
            print 'copy right!!!!!!!!!!!!!!!!!!!!!'
            return
        '''
        if len(contents) < 300:
            print 'too short!!!!!!!!!!!!!!!!!!!!!!'
            return
        
        article['contents_unfilt'] = contents
        delete_part = re.compile(r'\[.*?\]')
        contents_1 = delete_part.sub('', contents)
        delete_part_2 = re.compile(r'\(.*?\)')
        contents_2 = delete_part_2.sub('', contents_1)
        delete_part_3 = re.compile(r'\<.*?\>')
        contents = delete_part_3.sub('', contents_2)
               
        contents_filts = [u'그래픽', u'카메라뉴스', u'카드뉴스', u'부고', u'부음',
                          u'사진', u'포토', u'인사', u'[', u'▲', u'◇', u'◆',
                          u'경향신문', u'중앙일보', u'한겨레', u'동아일보', u'조선일보',
                          u'연합뉴스', u'데일리안', u'오마이뉴스', u'매일경제', u'한국경제',
                          u'한국일보', u'국민일보', u'서울신문', u'뉴데일리', u'노컷뉴스',
                          u'한경', u'매경', 'MBN', 'WOW', u'머니투데이', u'더벨',
                          u'동아닷컴', u'사진=동아DB', u'사진=동아 DB', u'사진=동아닷컴DB',
                          u'시민기자', u'저작권자', u'정치BAR_말풍선 브리핑', u'사진=채널A 캡처',
                          u'동아', u'기자']
        
        for contents_filt in contents_filts:
            if contents_filt in contents:
                 #print contents
                 contents = contents.replace(contents_filt, '')
                 print '!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'
                 #print contents
        
        if agency == u'연합뉴스':
            pos_1 = contents.find(u'=')
            contents = contents[pos_1 + 1:]
        
        contents_splited = contents.split()
        contents_splited = filter(self.filter_func, contents_splited)
        contents = ' '.join(contents_splited)
        contents_splited_2 = contents.split('.')
        contents_splited_2 = filter(self.filter_func_2, contents_splited_2)
        contents = '.'.join(contents_splited_2)
        
        
        language_contents = langid.classify(contents)
        if language_contents[0] != "ko":
            print 'language !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'
            return 
        
        article['summary'] = contents[0 : 70]
        article['contents'] = contents
        yield article
    
    def parse_news_deleted(self, response):
        
        article_deleted = response.meta['article_deleted']
        agency = response.meta['article_deleted']['agency']
        parsed_response_url = urlparse(response.url)
        host_part = parsed_response_url[1]

        if host_part == 'entertain.naver.com':
            contents = ' '.join(response.css('div#articeBody').xpath('.//text()').extract()).strip()
        elif host_part == 'sports.news.naver.com':
            contents = ' '.join(response.css('div.article > div').xpath('.//text()').extract()).strip()
        else:
            contents = ' '.join(response.css('div#articleBodyContents').xpath('.//text()').extract()).strip()
        article_deleted['contents'] = contents
        yield article_deleted
        

    def filter_func(self, contents_sp):
        contents_filt_2 = [u'@', 'DB', u'=', u'ⓒ', u'©']
        if all(t not in contents_sp for t in contents_filt_2):
            return contents_sp
        
    def filter_func_2(self, contents_sp):
        if u'캡처' not in contents_sp:
            return contents_sp
    
        
