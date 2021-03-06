# -*- coding: utf-8 -*-

import sys, traceback
import time
import scrapy
import MySQLdb
from scrapy.http import Request, FormRequest
from tutorial.items import NikkeiArticleItem
import os
sys.path.append(os.path.abspath("/var/www/html/asan/asan/rakes"))
from jpRake import *


class NikkeiSpider(scrapy.Spider):
    name = 'nikkei'
    allowed_domains = ['nikkei.com']
    start_urls = []

    formdata = {
                'LA0010Form01': 'LA0010Form01',
                'LA0010Form01:InputEmail': 'snubdi@gmail.com',
                'LA0010Form01:InputPassword': 'snubdi38511',
                'LA0010Form01:lao': '',
                'LA0010Form01:lfao:': '',
                'LA0010Form01:j_id36': u'ログイン',
                'controlParamKey': '',
                'javax.faces.ViewState': ''
                }
    date = time.strftime('%Y%m%d', time.localtime(time.time()))
    url_paper = 'http://www.nikkei.com/paper/'
    #url_paper = 'http://www.nikkei.com/paper/morning/?b=20151203&d=0'


    '''
    Request login page
    '''
    def start_requests(self):
        return [Request("https://id.nikkei.com/lounge/nl/base/LA0010.seam", meta = {'cookiejar' : 2}, callback = self.post_login)]


    '''
    Post Form data and login
    '''
    def post_login(self, response):
        print 'login~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'
        print response.url
        #print response.body
        #get formdata from login page
        self.formdata['controlParamKey'] = response.xpath('//*[@id="j_id11"]/input[2]/@value').extract()[0]
        self.formdata['javax.faces.ViewState'] = response.xpath('//*[@id="j_id11"]/input[3]/@value').extract()[0]
        print self.formdata
        #post
        return [FormRequest.from_response(response,
                                          meta = {'cookiejar': response.meta['cookiejar']},
                                          formdata = self.formdata,
                                          callback = self.after_login, dont_filter = True)]


    '''
    Request to news paper page after login
    '''
    def after_login(self, response):
        print 'login!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'
        print response.url
        #request to news paper page but it redirect to authonly page automatically
        yield scrapy.Request(self.url_paper,
                             meta = {'cookiejar': response.meta['cookiejar']},
                             callback = self.post_authonly)


    '''
    Post authonly page before request to news paper page
    '''
    def post_authonly(self, response):
        try:

            print '@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@'
            print response.url
            #print response.body
            '''
            #get form data from authonly page
            rpid = response.xpath('//input[@name="rpid"]/@value').extract()[0]
            pxep = response.xpath('//input[@name="pxep"]/@value').extract()[0]
            rtur = response.xpath('//input[@name="rtur"]/@value').extract()[0]
            clg = response.xpath('//input[@name="clg"]/@value').extract()[0]
            dps = response.xpath('//input[@name="dps"]/@value').extract()[0]
            xp0 = response.xpath('//input[@name="xp0"]/@value').extract()[0]
            

            #post form data
            return [FormRequest(url = "https://id.nikkei.com/lounge/ep/authonly",
                                meta = {'cookiejar': response.meta['cookiejar']},
                                formdata = {'rpid': rpid,
                                            'pxep': pxep,
                                            'rtur': rtur,
                                            'clg': clg,
                                            'dps': dps,
                                            'xp0': xp0
                                            },
                                method = 'post',
                                callback = self.post_news)]
            '''
            response_type = response.xpath('//input[@name="response_type"]/@value').extract()[0]
            client_id = response.xpath('//input[@name="client_id"]/@value').extract()[0]
            redirect_uri = response.xpath('//input[@name="redirect_uri"]/@value').extract()[0]
            scope = response.xpath('//input[@name="scope"]/@value').extract()[0]
            nonce = response.xpath('//input[@name="nonce"]/@value').extract()[0]
            state = response.xpath('//input[@name="state"]/@value').extract()[0]
            x_dps = response.xpath('//input[@name="x_dps"]/@value').extract()[0]

            return [FormRequest(url = "https://id.nikkei.com/lounge/ep/connect/auth",
                                meta = {'cookiejar': response.meta['cookiejar']},
                                formdata = {'response_type': response_type,
                                            'client_id': client_id,
                                            'redirect_uri': redirect_uri,
                                            'scope': scope,
                                            'nonce' : nonce,
                                            'state': state,
                                            'x_dps': x_dps
                                            },
                                method = 'post',
                                callback = self.post_news)]
            


        except Exception, e:
            print 'ERROR!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!   URL :'
            print traceback.print_exc(file = sys.stdout)


    '''
    Post regist accounts page and redirect to news paper page
    '''
    def post_news(self, response):

        print '%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%'
        print response.url
        print response.body
        #post form data and request to news paper page
        news_list = 'https://regist.nikkei.com/ds/etc/accounts/auth?url=' + self.url_paper
        return [FormRequest(url = news_list,
                            meta = {'cookiejar': response.meta['cookiejar']},
                            formdata = {#'aa': response.xpath('//input[@name="aa"]/@value').extract()[0]
                                        'code': response.xpath('//input[@name="code"]/@value').extract()[0],
                                        'state': response.xpath('//input[@name="state"]/@value').extract()[0]},
                            callback = self.parse, dont_filter = True)]
        


    '''
    Get news url from news list
    '''
    def parse(self,response):
        print '********************************************************'
        print response.url
        try:

            #get news url from news list
            sites = response.xpath('//h4[@class="cmn-article_title"]')
            for site in sites:
                news_url = site.xpath('span/a/@href').extract()[0]
                news_url_1 = 'http://www.nikkei.com' + news_url
                print news_url_1
                yield scrapy.Request(news_url_1, meta = {'cookiejar': response.meta['cookiejar']}, callback = self.parse_news)

        except Exception, e:
            print 'Parse ERROR!!!!!!!!!!!!!  URL :' + response.url
            print traceback.print_exc(file = sys.stdout)

    '''
    Get contents of news from news page
    '''
    def parse_news(self, response):
        print '$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$'
        print response.url
        try:

            article = NikkeiArticleItem()
            #get title of news
            article['title'] = ''.join(response.xpath('//h1[@class="cmn-article_title cmn-clearfix"]/span/text()').extract()).strip()
            #get contents of news
            #article['contents'] = ''.join(response.xpath('//div[@class="cmn-article_text JSID_key_fonttxt"]/p//text()').extract()).strip()
            contents = ''.join(response.xpath('//div[@class="cmn-article_text JSID_key_fonttxt"]/p//text()').extract()).strip()
            #Get keywords and tagged_text
            rake = jpRake()
            keywords_list = rake.run(contents)
            keywords = '\n'.join(keywords_list)
            tagged_text = rake.get_tagged_text()

            article['contents'] = contents
            article['keywords'] = keywords
            article['tagged_text'] = tagged_text
            #get url of news
            article['url'] = response.url
            #set agency of news
            article['agency'] = u'日本経済新聞'
            #get aid of news
            pos = response.url.find('ng=')
            article['aid'] = response.url[pos + 3:]
            #get date of news
            date_time = self.date[0:4] + '-' + self.date[4:6] +'-' + self.date[6:] + ' ' + '03:00:00'
            article['date'] = date_time

            yield article

        except Exception, e:
            print 'Parse_news ERROR!!!!!!!!!!!!!  URL :'+ response.url
            print traceback.print_exc(file = sys.stdout)
