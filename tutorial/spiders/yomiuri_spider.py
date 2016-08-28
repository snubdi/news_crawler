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
from scrapy.http import Request, FormRequest
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from pyvirtualdisplay import Display
import os
sys.path.append(os.path.abspath("/var/www/html/asan/asan/rakes"))
from jpRake import *



class YomiuriSpider(scrapy.Spider):
    name = 'yomiuri'
    start_urls = ["https://premium.yomiuri.co.jp"]
    dont_filter = False

    def __init__(self):
        # Virtual Display for Running Selenium
        try:
            self.display = Display(visible=0, size=(1280, 1024))
            self.display.start()
            profile = webdriver.FirefoxProfile()
            profile.native_events_enabled = True
            self.driver = webdriver.Firefox(profile)
            self.driver.get("https://premium.yomiuri.co.jp/login.jsp?appType=PC&url=http%3A%2F%2Fpremium.yomiuri.co.jp%2Fpc%2F%23%2Fcheck%2Flist_NEWS%25255fMAIN")
            id = self.driver.find_element_by_xpath('//input[@name="id"]')
            password = self.driver.find_element_by_xpath('//input[@name="password"]')
            id.send_keys("ayssh1025@gmail.com")
            password.send_keys("snubdi38511")
            login = self.driver.find_element_by_xpath('//form[@id="frm"]')
            login.submit()
            time.sleep(5)
        except:
            print "!!!!!!!!!!!!!!!!error!!!!!!!!!!!!!!!!"

    def parse(self, response):
        try:
            self.driver.get('http://premium.yomiuri.co.jp/pc/#!/list_NEWS%255fMAIN')
            #print self.driver.title
            c_list = self.driver.find_elements_by_xpath(
                '//div[@class="yp_layout_template"]/div[@class="loft_article_sttl"]/a')
            c_list = [c.get_attribute("href") for c in c_list]
            for c in c_list:
                #self.parse_page(c)
                self.driver.get(c)
                time.sleep(5)
                url_list = self.driver.find_elements_by_xpath('//a[@class="yp_article_link"]')
                news_urls = [news.get_attribute("href") for news in url_list]
                for u in news_urls:
                    self.driver.get(u)
                    time.sleep(2)
                    news_aid = u[u.find(u'/news_201')+1:u.find(u'/list_NEWS')]
                    news_title = self.driver.find_element_by_xpath('//div[@class="yp_article_title"]').text
                    news_date = self.driver.find_element_by_xpath('//div[@class="yp_article_credit"]').text
                    news_date = time.strftime('%Y-%m-%d %H:%M:%S', self.parse_date(news_date))
                    news_content = self.driver.find_elements_by_xpath('//div[@class="yp_article_body"]')
                    news_content = ''.join([content.text for content in news_content])
                    #print news_content
                    rake = jpRake()
                    keywords_list = rake.run(news_content)
                    keywords = '\n'.join(keywords_list)
                    tagged_text = rake.get_tagged_text()

                    article = YomiuriArticleItem()
                    article['url'] = u
                    article['aid'] = news_aid
                    article['title'] = news_title
                    article['date'] = news_date
                    article['contents'] = news_content
                    article['keywords'] = keywords
                    article['tagged_text'] = tagged_text
                    #print article
                    yield article
        finally:
            if self.driver != None:
                self.driver.close()
                self.driver.quit()
            if self.display != None:
                self.display.stop()


    '''
    Parse a date string in the form of '2015.07.10 오후 2:39' and return a time object
    Args:
     orig_date_str - the origina string to parse
    Returns:
     python time object
    '''

    def parse_date(self, orig_date_str):
        date_str = unicode(orig_date_str)
        hour = date_str[date_str.find(u'日')+1:date_str.find(u'時')]
        min = date_str[date_str.find(u'時')+1:date_str.find(u'分')]
        time_str = date_str.replace(u'年', u'-').replace(u'月', u'-')
        time_str = time_str[:time_str.find(u'日')]
        time_str += " %02d:%02d" % (int(hour), int(min))
        new_time = time.strptime(time_str, u'%Y-%m-%d %H:%M')
        return new_time
