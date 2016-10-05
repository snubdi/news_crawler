
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
from tutorial.items import NaverArticleItem, NaverCommentItem
import MySQLdb
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from pyvirtualdisplay import Display
from scrapy.http import TextResponse
import os
#sys.path.append(os.path.abspath("/var/www/html/asan/asan/database"))
sys.path.append(os.path.abspath("/var/www/html/asan/asan/rakes"))
from korRAKE_002 import *

class NaverQuickSpider(scrapy.Spider):
    name = 'Naver_quick'
    allowed_domains = ['naver.com']
    start_urls = []

    s_date = ''
    e_date = ''
    c_date = ''
    page_cnt = 1
    dont_filter = False
    agency_list = []
    '''
    Constructor
    '''
    def __init__(self, start_date = '', end_date = '',check_date = '', *args, **kwargs):
        self.s_date = start_date
        self.e_date = end_date
        self.c_date = check_date
        if check_date == '':
            #Default Check_date is today
            today = datetime.now() + timedelta(days = -0)
            self.c_date = today.strftime("%Y%m%d")
            print self.c_date
        #self.start_urls = [self.get_query_url(self.c_date, self.page_cnt)]
        self.start_urls = self.get_query_url(self.c_date, self.page_cnt)
        super(NaverQuickSpider, self).__init__(*args, **kwargs)
        self.display = Display(visible=0, size=(1280, 1024))
        self.display.start()
        profile = webdriver.FirefoxProfile()
        profile.native_events_enabled = True
        self.driver = webdriver.Firefox(profile)

    def __del__(self):

        self.driver.close()
        self.driver.quit()
        self.display.stop()
        print '************************************************************************'
        print 'CLOSED!!!'
    '''
    Get the query url
    '''
    def get_query_url(self, check_date, page):
        #qs = {'query': keyword}
        #'http://news.naver.com/main/list.nhn?sid1=001&mid=sec&mode=LSD&listType=paper' \
        #return 'http://news.naver.com/main/list.nhn?sid1=001&mid=sec&mode=LSD&' \
        '''
        return 'http://news.naver.com/main/list.nhn?mode=LSD&mid=sec&sid1=001&listType=paper' \
                + '&date=' + check_date \
                + '&page=' + str(page) \
        '''
        #return 'http://news.naver.com/main/list.nhn?mode=LSD&mid=sec&sid1=001&listType=paper' + '&date=' + check_date + '&page=' + str(page)
        return ['http://news.naver.com/main/list.nhn?oid=032&listType=paper&mid=sec&mode=LPOD&date='+ check_date + '&page=1',
        'http://news.naver.com/main/list.nhn?oid=032&listType=paper&mid=sec&mode=LPOD&date='+ check_date + '&page=2',
        'http://news.naver.com/main/list.nhn?oid=032&listType=paper&mid=sec&mode=LPOD&date='+ check_date + '&page=3',
        'http://news.naver.com/main/list.nhn?oid=032&listType=paper&mid=sec&mode=LPOD&date='+ check_date + '&page=4',
        'http://news.naver.com/main/list.nhn?oid=028&listType=paper&mid=sec&mode=LPOD&date='+ check_date + '&page=1',
        'http://news.naver.com/main/list.nhn?oid=028&listType=paper&mid=sec&mode=LPOD&date='+ check_date + '&page=2',
        'http://news.naver.com/main/list.nhn?oid=028&listType=paper&mid=sec&mode=LPOD&date='+ check_date + '&page=3',
        'http://news.naver.com/main/list.nhn?oid=020&listType=paper&mid=sec&mode=LPOD&date='+ check_date + '&page=1',
        'http://news.naver.com/main/list.nhn?oid=020&listType=paper&mid=sec&mode=LPOD&date='+ check_date + '&page=2',
        'http://news.naver.com/main/list.nhn?oid=020&listType=paper&mid=sec&mode=LPOD&date='+ check_date + '&page=3',
        'http://news.naver.com/main/list.nhn?oid=020&listType=paper&mid=sec&mode=LPOD&date='+ check_date + '&page=11',
        'http://news.naver.com/main/list.nhn?oid=020&listType=paper&mid=sec&mode=LPOD&date='+ check_date + '&page=12',
        'http://news.naver.com/main/list.nhn?oid=020&listType=paper&mid=sec&mode=LPOD&date='+ check_date + '&page=13',
        'http://news.naver.com/main/list.nhn?oid=023&listType=paper&mid=sec&mode=LPOD&date='+ check_date + '&page=1',
        'http://news.naver.com/main/list.nhn?oid=023&listType=paper&mid=sec&mode=LPOD&date='+ check_date + '&page=2',
        'http://news.naver.com/main/list.nhn?oid=023&listType=paper&mid=sec&mode=LPOD&date='+ check_date + '&page=3',
        'http://news.naver.com/main/list.nhn?oid=023&listType=paper&mid=sec&mode=LPOD&date='+ check_date + '&page=4',
        'http://news.naver.com/main/list.nhn?oid=023&listType=paper&mid=sec&mode=LPOD&date='+ check_date + '&page=5',
        'http://news.naver.com/main/list.nhn?oid=023&listType=paper&mid=sec&mode=LPOD&date='+ check_date + '&page=6',
        'http://news.naver.com/main/list.nhn?oid=025&listType=paper&mid=sec&mode=LPOD&date='+ check_date + '&page=1',
        'http://news.naver.com/main/list.nhn?oid=025&listType=paper&mid=sec&mode=LPOD&date='+ check_date + '&page=2',
        'http://news.naver.com/main/list.nhn?oid=025&listType=paper&mid=sec&mode=LPOD&date='+ check_date + '&page=3',
        'http://news.naver.com/main/list.nhn?oid=025&listType=paper&mid=sec&mode=LPOD&date='+ check_date + '&page=4',
        ]


    '''
    Starting point
    Retrieve the news link from the list of search results.
    Args:
     response - the response object pertaining to the search results page
    '''
    def parse(self, response):
        # next page end condition
        #next_button = response.xpath('//td[@class="content"]//div[@class="paging"]/a[@class="next"]')
        #if self.page_cnt >10:
        '''
        if len(next_button) == 0 and self.page_cnt >= int(response.xpath('//td[@class="content"]//div[@class="paging"]/a/text()').extract()[-1]):
            print "!!!!!!!!!!!!!get max page" + str(self.page_cnt)
            return
        '''
        # determine whether to go ahead with parse or not
        news_list= response.xpath('//td[@class="content"]//div[@id="main_content"]//li')

        #print 'Page %s' % self.page_cnt
        print 'news_size is :' + str(len(news_list))
        cnt = 0
        for news_article in news_list:
            try:

                # news agency
                agency = news_article.xpath('.//span[@class="writing"]/text()').extract()[0]

                '''
                if agency not in [u'경향신문',u'중앙일보',u'한겨레',u'동아일보',u'조선일보']:
                    continue
                '''
                # naver news link
                news_url = news_article.xpath('.//a/@href').extract()[0]

                #naver news title
                news_title = news_article.xpath('.//a/text()').extract()[0]

                #naver news date
                news_date = news_article.xpath('.//span[@class="date"]/text()').extract()[0]

                #naver news paper
                news_position = news_article.xpath('.//span[@class="paper"]/text()').extract()[0]

                # parse news link to get aid and oid
                parsed_news_url = urlparse(news_url)

                #host_part = parsed_news_url[1]
                query_string = parse_qs(parsed_news_url[4])

                # populate article item
                #if query_string['oid'][0] != '32':
                #    continue
                article = NaverArticleItem()
                article['aid'] = query_string['aid'][0]
                article['oid'] = query_string['oid'][0]
                article['agency'] = agency
                article['date'] = news_date
                article['title'] = news_title
                article['position'] = news_position

                req = scrapy.Request(news_url, callback = self.parse_news, dont_filter = self.dont_filter)

                article['referer'] = response.url
                req.meta['article'] = article
                #print article
                yield req

                cnt += 1
            except Exception, e:
                print 'ERROR!!!!!!!!!!!!!  URL :'
                print traceback.print_exc(file = sys.stdout)
                #pass

        print 'read %s articles' % cnt

        #self.page_cnt += 1
        #next_page_url = self.get_query_url(self.c_date, self.page_cnt)
        #yield scrapy.Request(next_page_url, callback = self.parse, dont_filter = self.dont_filter)


    '''
    Retrieve the comment count link from a given news article.
    Args:
     response - the response object pertaining to the news article page
    '''
    def parse_news(self, response):

        # populate the rest of the article
        article = response.meta['article']
        article['url'] = response.url

        title = ''
        date = ''

        parsed_response_url = urlparse(response.url)
        host_part = parsed_response_url[1]

        if host_part == 'entertain.naver.com':
            title = response.css('p.end_tit').xpath('.//text()').extract()[0]
            date = response.css('div.article_info > span.author > em').xpath('.//text()').extract()[0]
            date = time.strftime('%Y-%m-%d %H:%M:00', self.parse_date(date))
            contents = ' '.join(response.css('div#articeBody').xpath('.//text()').extract()).strip()
        elif host_part == 'sports.news.naver.com':
            title = response.css('div.articlehead > h4').xpath('.//text()').extract()[0]
            date = response.css('div.info_article > span.time').xpath('.//text()').extract()[0]
            contents = ' '.join(response.css('div.article > div').xpath('.//text()').extract()).strip()

        else:
            title = response.css('div.article_info > h3').xpath('.//text()').extract()[0]
            date = response.css('div.article_info > div.sponsor > span.t11').xpath('.//text()').extract()[0]
            contents = ' '.join(response.css('div#articleBodyContents').xpath('.//text()').extract()).strip()

        #Use run() from korRAKE002.py to get keywords and tagged_text
        #tres = korRake(contents)
        #res = tres.run()
        #keywords = '|||'.join(res[0])
        #tagged_text = res[1]

        tres = korRake()
        keywords_list = tres.run(contents)
        keywords = '\n'.join(keywords_list)
        tagged_text = tres.get_tagged_text()

        #keywords = run(contents)
        #tagged_text = get_tagged_text(contents,contents)

        article['title'] = title
        article['contents'] = contents
        article['date'] = date
        article['keywords'] = keywords
        article['tagged_text'] = tagged_text

        yield article
        comment_url = response.url + '&m_view=1'
        req = scrapy.Request(comment_url, callback = self.comment_parse, dont_filter = self.dont_filter)
        req.meta['article'] = article
        yield req

    def comment_parse(self, response):

        #try:
        print response.url
        aid = response.meta['article']['aid']
        date = response.meta['article']['date']
        self.driver.get(response.url)
        time.sleep(3)

        while True:
            button_more = self.driver.find_element_by_xpath('//a[@class="u_cbox_btn_more __cbox_page_button"]')
            try:
                button_more.click()
            except:
                break

        resp = TextResponse(url=self.driver.current_url, body=self.driver.page_source, encoding='utf-8')
        for site in resp.xpath('.//ul[@class="u_cbox_list"]/li'):
            username = site.xpath('.//span[@class="u_cbox_nick"]/text()').extract()
            like_count = site.xpath('.//em[@class="u_cbox_cnt_recomm"]/text()').extract()
            dislike_count = site.xpath('.//em[@class="u_cbox_cnt_unrecomm"]/text()').extract()
            contents = site.xpath('.//span[@class="u_cbox_contents"]/text()').extract()
            comment = NaverCommentItem()
            comment['aid'] = aid
            comment['username'] = username
            comment['like_count'] = like_count
            comment['dislike_count'] = dislike_count
            comment['contents'] = ''.join(contents)
            comment['date'] = date
            yield comment
        '''
        finally:
            if self.driver != None:
                self.driver.close()
                self.driver.quit()
            if self.display != None:
                self.display.stop()
         '''

    '''
    Parse a date string in the form of '2015.07.10 오후 2:39' and return a time object
    Args:
     orig_date_str - the origina string to parse
    Returns:
     python time object
    '''
    def parse_date(self, orig_date_str):

        # date is in the form of '2015.07.10 오후 2:39'
        # change to python time object
        regex_res = re.match(u'^(\d{4}\.\d{2}\.\d{2})(.*?)(\d{1,2}:\d{2})$', orig_date_str, re.M|re.S)

        am_or_pm = regex_res.group(2).strip()
        if am_or_pm == u'\uc624\uc804':
            am_or_pm = 'AM'
        elif am_or_pm == u'\uc624\ud6c4':
            am_or_pm = 'PM'

        new_time_str = '%s %s %s' % (
            regex_res.group(1),
            regex_res.group(3),
            am_or_pm
        )

        new_time = time.strptime(new_time_str, '%Y.%m.%d %I:%M %p')
        return new_time

    '''
    Debug method - update deleted column
    '''
    def update_deleted(self, url):

        try:
            conn = MySQLdb.connect(
                    host = 'localhost',
                    user = 'mers',
                    passwd = 'Kb459CKS7nQLsHbD',
                    charset = 'utf8'
                    )
            cur = conn.cursor()
            conn.select_db('mers')

            sql = "update articles set deleted = 'Y' where url = '%s'" % (url)
            cur.execute(sql)
            conn.commit()
            cur.close()
            conn.close()
        except MySQLdb.Error, e:
            print 'MySQL error %d: %s' % (e.args[0], e.args[1])


    '''
    Debug method - update the given count
    '''

    def update_count(self, tpe, cnt):
        try:
            conn = MySQLdb.connect(
                    host = 'localhost',
                    user = 'mers',
                    passwd = 'Kb459CKS7nQLsHbD',
                    charset = 'utf8'
                    )
            cur = conn.cursor()
            conn.select_db('mers')

            sql = 'update counts set v = v + %s where k = "%s"' % (cnt, tpe)
            cur.execute(sql)
            conn.commit()
            cur.close()
            conn.close()
        except MySQLdb.Error, e:
            print 'MySQL error %d: %s' % (e.args[0], e.args[1])

    '''
    Debug method - insert the given url
    '''

    def update_url(self, url):
        try:
            conn = MySQLdb.connect(
                    host = 'localhost',
                    user = 'mers',
                    passwd = 'Kb459CKS7nQLsHbD',
                    charset = 'utf8'
                    )
            cur = conn.cursor()
            conn.select_db('mers')

            sql = 'insert into urls set url = "%s"' % url
            cur.execute(sql)
            conn.commit()
            cur.close()
            conn.close()
        except MySQLdb.Error, e:
            print 'MySQL error %d: %s' % (e.args[0], e.args[1])
