
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
from tutorial.items import NaverSummaryItem
import MySQLdb


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
    sid1 = [100,101,102,103,104,105,106,107]
    '''
    Constructor
    '''
    def __init__(self, start_date = '', end_date = '',check_date = '', *args, **kwargs):
        self.s_date = start_date
        self.e_date = end_date
        self.c_date = check_date
        if check_date == '':
            yesterday = datetime.now() + timedelta(days = -1)
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
        #qs = {'query': keyword}
        #'http://news.naver.com/main/list.nhn?sid1=001&mid=sec&mode=LSD&listType=paper' \
        
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
        #if self.page_cnt >10:
        if len(next_button) == 0 and self.page_cnt >= int(response.xpath('//td[@class="content"]//div[@class="paging"]/a/text()').extract()[-1]):
            print "!!!!!!!!!!!!!get max page" + str(self.page_cnt)
            return
        # determine whether to go ahead with parse or not
        news_list= response.xpath('//td[@class="content"]//div[@id="main_content"]//li')

        print 'Page %s' % self.page_cnt
        print 'news_size is :' + str(len(news_list))
        cnt = 0
        
        for news_article in news_list:
            try:
                
                # news agency
                agency = news_article.xpath('.//span[@class="writing"]/text()').extract()[0]

                if agency not in [u'경향신문',u'중앙일보',u'한겨레',u'동아일보',u'조선일보',
                                  u'연합뉴스',u'데일리안',u'오마이뉴스',u'스포츠서울',u'스포츠조선']:
                    continue
                # naver news link
                news_url = news_article.xpath('.//a/@href').extract()[0]
                
                #naver news title
                news_title = ''.join(news_article.xpath('.//a/text()').extract()).strip()
                
                #naver news date
                news_date = news_article.xpath('.//span[@class="date"]/text()').extract()[0]
                
                # parse news link to get aid and oid
                parsed_news_url = urlparse(news_url)
                
                #host_part = parsed_news_url[1]
                query_string = parse_qs(parsed_news_url[4])
                
                contents = ''.join(news_article.xpath('dl/dd/text()').extract()).strip()
                
                if 'sid1=100' in response.url:
                    category = u'정치'
                elif 'sid1=101' in response.url:
                    category = u'경제'
                elif 'sid1=102' in response.url:
                    category = u'사회'
                elif 'sid1=103' in response.url:
                    category = u'생활/문화'
                elif 'sid1=104' in response.url:
                    category = u'세계'
                elif 'sid1=105' in response.url:
                    category = u'IT/과학'
                elif 'sid1=106' in response.url:
                    category = u'연예'
                elif 'sid1=107' in response.url:
                    category = u'스포츠'
                
                # populate article item
                #if query_string['oid'][0] != '32':
                #    continue                
                article = NaverSummaryItem()
                article['aid'] = query_string['aid'][0]
                #article['oid'] = query_string['oid'][0]
                article['agency'] = agency
                article['date'] = news_date
                article['title'] = news_title
                article['contents'] = contents
                article['url'] = news_url
                article['category'] = category
                #article['position'] = news_position
                
                yield article
                
                cnt += 1
            except Exception, e:
                print 'ERROR!!!!!!!!!!!!!  URL :'
                print traceback.print_exc(file = sys.stdout)
                #pass

        print 'read %s articles' % cnt
        
        self.page_cnt += 1
        pos = response.url.find('page=')
        next_page_url = response.url[:pos + 5] + str(self.page_cnt)
        yield scrapy.Request(next_page_url, callback = self.parse, dont_filter = self.dont_filter)


