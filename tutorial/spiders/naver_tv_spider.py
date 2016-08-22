# -*- coding: utf-8 -*-
import sys
import os
import scrapy
import time
from datetime import date, datetime, timedelta
from tutorial.items import NaverArticleItem, NaverCommentItem
from django.conf.urls import url
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from pyvirtualdisplay import Display
from scrapy.http import TextResponse
sys.path.append(os.path.abspath("/var/www/html/asan/asan/rakes"))
from korRAKE_002 import *

class NaverTvSpider(scrapy.Spider):
    name = 'Naver_tv'
    allowed_domains = ['naver.com']
    oid_of_tv = ['056', '214', '057', '052', '055', '448', '422', '449', '437']
    date_today = ''
    page_cnt = 1
    start_urls = []
    '''
    news_year = ''
    news_month = ['']
    news_day = ['']
    '''

    def __init__(self, *args, **kwargs):

        self.date_today = datetime.now().strftime("%Y%m%d")
        self.date_today = datetime.now() + timedelta(days=-1)
        self.date_today = self.date_today.strftime("%Y%m%d")
        '''
        self.news_year = ['2014'] #, '2014'
        self.news_month = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12'] #'01', '02', '03', '04', '05', '06', '07', '08', '09',
        self.news_day = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10',
                          '11', '12', '13', '14', '15', '16', '17', '18', '19', '20',
                          '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31']

        '''
        for oid in self.oid_of_tv:
            self.start_urls.append(self.get_start_url(oid, self.date_today, self.page_cnt))
        super(NaverTvSpider, self).__init__(*args, **kwargs)
        '''
        for year in self.news_year:
            for month in self.news_month:
                for day_of_news in self.news_day:
                    for oid in self.oid_of_tv:
                            self.start_urls.append(self.get_news_url_byday(year, month, day_of_news, self.page_cnt, oid))
        '''
        super(NaverTvSpider, self).__init__(*args, **kwargs)



    def get_news_url_byday(self, year, month, day, page, oid):
        return 'http://news.naver.com/main/tv/list.nhn?oid=' + oid + '&mid=tvh&mode=LPOD&date=' + year + month + day +'&page=' + str(page)


    def get_start_url(self, oid, date_today, page):
        return 'http://news.naver.com/main/tv/list.nhn?oid=' + oid + '&mid=tvh&mode=LPOD&date=' + date_today + '&page=' + str(page)

    def parse(self, response):
        time.sleep(1)
        '''
        next_button = response.xpath('div[@class="paging"]/a[@class="next"]')
        # if self.page_cnt >10:
        if len(next_button) == 0 and self.page_cnt >= int(response.xpath('//td[@class="content"]//div[@class="paging"]/a/text()').extract()[-1]):
            print "!!!!!!!!!!!!!get max page" + str(self.page_cnt)
            return
        '''
        news_list = response.xpath('//ul[@class="type06"]/li')

        for news_article in news_list:
            try:
                title = news_article.xpath('.//dl/dt[2]/a/text()').extract()[0]
                news_url = news_article.xpath('.//dl/dt[2]/a/@href').extract()[0]
                agency = news_article.xpath('.//dl/dd/div/span[1]/text()').extract()[0]
                date = news_article.xpath('.//dl/dd/div/span[2]/text()').extract()[0].strip()
                article = NaverArticleItem()
                article['title'] = title
                article['agency'] = agency
                article['date'] = date
                article['url'] = news_url

                req = scrapy.Request(news_url, callback=self.parse_news)
                article['referer'] = response.url
                req.meta['article'] = article
                yield req
            except Exception, e:
                print 'ERROR!!!!!!!!!!!!!  URL :' + news_url

        pos = response.url.find('&page=')
        page_count = int(response.url[pos + 6:])
        next_url = response.url[:pos + 6] + str(page_count + 1)
        print '!!!!!!!!!!!!!!!!!!!!!'
        print next_url
        if page_count < 21:
            yield scrapy.Request(next_url, callback=self.parse)

    def parse_news(self, response):
        article = response.meta['article']
        news_url = response.url
        pos_aid = news_url.find('&aid=')
        aid = news_url[pos_aid + 5 : ]
        pos_oid_start = news_url.find('oid=')
        oid = news_url[pos_oid_start + 4: pos_aid]
        article['aid'] = aid
        article['oid'] = oid

        contents = ' '.join(response.xpath('//div[@id="articleBodyContents"]//text()').extract()).strip()
        if u'sports' in response.url:
            contents = ' '.join(response.xpath('//div[@id="newsEndContents"]//text()').extract()).strip()

        tres = korRake()
        keywords = tres.run(contents)
        tagged_text = tres.get_tagged_text()
        article['keywords'] = keywords
        article['tagged_text'] = tagged_text
        article['contents'] = contents
        yield article




