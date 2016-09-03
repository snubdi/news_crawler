# -*- coding: utf-8 -*-

import sys, traceback
import re
import os
import time
import json
import copy
import urllib
import time
from datetime import datetime, timedelta
from urlparse import urlparse, parse_qs
import scrapy
from tutorial.items import LexisnexisArticleItem
import MySQLdb
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from pyvirtualdisplay import Display
from scrapy.http import TextResponse
sys.path.append(os.path.abspath("/var/www/html/asan/asan/rakes"))
from rake import *


class LexisNexisSpider(scrapy.Spider):
    name = 'lexisnexis'
    start_urls = []

    s_date = ''
    e_date = ''
    c_date = ''
    page_cnt = 1
    dont_filter = True
    agency_list = []
    '''
    today = datetime.now() + timedelta(days = -3)
    date = str(today)[0:10]
    year = date[0:4]
    month = date[5:7]
    day = date[8:10]
    '''
    '''
    Constructor
    '''

    def __init__(self, keyword='nation', *args, **kwargs):
        self.keyword = keyword
        self.start_urls = ['http://www.google.com']
        super(LexisNexisSpider, self).__init__(*args, **kwargs)

        self.display = Display(visible=0, size=(1280, 1024))
        self.display.start()
        profile = webdriver.FirefoxProfile()
        profile.native_events_enabled = True
        self.driver = webdriver.Firefox(profile)
        # self.driver2 = webdriver.Firefox(profile)
        self.driver.get(self.get_query_url(self.keyword))
        time.sleep(3)

    def __del__(self):

        self.driver.close()
        self.driver.quit()
        self.display.stop()
        print '************************************************************************'
        print 'CLOSED!!!'

    '''
    Get the query url
    '''

    def get_query_url(self, keyword):
        today = datetime.now() + timedelta(days = -25)
        date = str(today)[0:10]
        year = date[0:4]
        month = date[5:7]
        day = date[8:10]
        return 'http://www.lexisnexis.com/lnacui2api/api/version1/sr?sr=%28' + keyword + '%29%20and%20Date%28geq%28'+ month + '/' + day + '/' + year + '%29%29&csi=8006%2C6742%2C8213%2C8142%2C8075%2C11810%2C306884%2C247189%2C163823%2C301477&oc=00006&hgn=t&hl=t&hes=t&hnsl=t&hsl=t&hdym=t&hfb=t&ssl=f&stp=bool&icvrpg=true'
        '''
					#The New York Times
					+'%2C6742' \
					# USA TODAY
					+'%2C8213' \
					#Wall Street Journal Abstracts
					+'%2C8142' \
					#The Washington Post
					+'%2C8075' \
					#Post-Dispatch
					+'%2C11810' \
					#The Baltimore Sun
					+'%2C306884' \
					#The Philadelphia Inquirer
					+'%2C247189' \
					#Chicago Daily Herald
                    +'%2c163823'
					#Arizona Capitol Times
                    +'%2c301477'
		'''
        #return 'http://www.lexisnexis.com/lnacui2api/api/version1/sr?sr=%28' + keyword + '%29%20and%20Date%28geq%28'+ month + '/' + day + '/' + year + '%29%29&csi=8006%2C6742%2C8213%2C8142%2C8075&oc=00006&hgn=t&hl=t&hes=t&hnsl=t&hsl=t&hdym=t&hfb=t&ssl=f&stp=bool&icvrpg=true'
        #return 'http://www.lexisnexis.com/lnacui2api/api/version1/sr?sr=%28' + keyword + '%29%20and%20Date%28geq%284/5/2011%29%29&csi=8006%2C6742%2C8213%2C8142%2C8075&oc=00006&hgn=t&hl=t&hes=t&hnsl=t&hsl=t&hdym=t&hfb=t&ssl=f&stp=bool&icvrpg=true'

    def next_page(self, start_index):
        try:
            next_button = self.driver.find_element_by_xpath(
                '//table//table//table//table//table//table//td[@align="right"]/a/img[@src="images/IconPaginationNext.gif"]')
        except:
            return False
            pass
        risb = self.driver.find_element_by_xpath('//input[@name="risb"]').get_attribute("value")
        nexpage = "http://www.lexisnexis.com/lnacui2api/results/listview/listview.do?start=" + str(
            start_index) + "&sort=RELEVANCE&format=GNBLIST&risb=" + risb
        self.driver.get(nexpage)
        time.sleep(2)
        source = self.driver.find_element_by_xpath('//frame[@title="Results Content Frame"]')
        self.driver.get(source.get_attribute("src"))
        time.sleep(2)
        return True

    '''
    Starting point
    Retrieve the news link from the list of search results.
    Args:
     response - the response object pertaining to the search results page
    '''

    def parse(self, response):
        button_continue = self.driver.find_element_by_xpath('//a[@id="firstbtn"]')
        try:
            button_continue.click()
        except:
            print 'can''t find continue button '
        source = self.driver.find_element_by_xpath('//frame[@title="Results Content Frame"]')
        self.driver.get(source.get_attribute("src"))
        time.sleep(5)
        item_list = list()
        start_id = 1
        while self.next_page(start_id):
            noshade_list = self.driver.find_elements_by_xpath('//tr[@class="noshaderow1st"]')
            shade_list = self.driver.find_elements_by_xpath('//tr[@class="shaderow1st"]')
            for news in noshade_list + shade_list:
                button = news.find_element_by_xpath('.//a')
                news_title = button.text
                news_url = button.get_attribute("href")
                news_agency = news.find_element_by_xpath('.//span[@class="notranslate"]').text

                article = LexisnexisArticleItem()
                article['title'] = news_title
                article['url'] = news_url
                article['agency'] = news_agency
                item_list.append(article)
            start_id += 25
            print "++++++++++++++++++", len(item_list)
        for article in item_list:
            self.driver.get(article['url'])
            time.sleep(2)
            try:
                source = self.driver.find_element_by_xpath('//frame[@title="Results Document Content Frame"]')
                self.driver.get(source.get_attribute('src'))
                time.sleep(2)
                date_str = self.driver.find_element_by_xpath('//span[@class="verdana"]/center').text
                news_date = self.parse_date(date_str)

                news_id = self.driver.find_element_by_xpath('//input[@name="docIdentifier"]')
                news_id = news_id.get_attribute('value')

                news_content_list = self.driver.find_elements_by_xpath('//span[@class="verdana"]/p[@class="loose"]')
                news_content_list = [n.text for n in news_content_list]
                news_content = '.'.join(news_content_list)

                #Get keywords
                rake = Rake()
                keywords_list = rake.run(news_content)
                keywords = '\n'.join(keywords_list)

                #article['keywords'] = keywords
                article['aid'] = news_id
                article['date'] = news_date
                article['contents'] = news_content
                article['keywords'] = keywords
            except Exception, e:
                print 'ERROR!!!!!!!!!!!!!  URL :'
                print traceback.print_exc(file=sys.stdout)

            yield article

            # yield scrapy.Request(next_page_url, callback=self.parse, dont_filter=self.dont_filter)

    def does_element_exist(self, xpath):
        try:
            self.driver.find_element_by_xpath(xpath)
            return True
        except:
            return False

    '''
    Parse a date string in the form of '2015.07.10 오후 2:39' and return a time object
    Args:
     orig_date_str - the origina string to parse
    Returns:
     python time object
    '''

    def parse_date(self, date_str):
        _known = {
            'January': '01',
            'February': '02',
            'March': '03',
            'April': '04',
            'May': '05',
            'June': '06',
            'July': '07',
            'August': '08',
            'September': '09',
            'October': '10',
            'November': '11',
            'December': '12',
        }
        # parse date time
        date = date_str.split('\n')[0]

        news_time = date.split()[2] + '-' + _known[date.split()[0]] + '-' + date.split()[1].replace(',', '')
        return news_time
