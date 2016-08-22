# -*- coding: utf-8 -*-

import re
import MySQLdb
from tutorial.items import *

from tutorial.spiders.netease_spider_byday import NeteaseSpiderByDay
from tutorial.spiders.netease_spider import NeteaseSpider
from tutorial.spiders.naver_quick_spider import NaverQuickSpider
from tutorial.spiders.peoplenet_spider import PeoplenetSpider
from tutorial.spiders.globaltimes_spider import GlobaltimesSpider
from tutorial.items import PeoplenetArticleItem, PeoplenetCommentItem
from tutorial.spiders.ce_spider import CeSpider
from tutorial.items import CeArticleItem
from tutorial.spiders.xinhua_spider import XinhuaSpider
from tutorial.items import GlobaltimesArticleItem, GlobaltimesCommentItem
from tutorial.spiders.yahoonews_spider import YahoonewsSpider
from tutorial.spiders.yomiuri_spider import YomiuriSpider
from tutorial.items import YahoonewsArticleItem, YahoonewsCommentItem
from tutorial.spiders.sankei_spider import SankeiSpider
from tutorial.items import SankeiArticleItem
from tutorial.spiders.asahi_spider import AsahiSpider
from tutorial.items import AsahiArticleItem
from tutorial.spiders.nikkei_spider import NikkeiSpider
from tutorial.items import NikkeiArticleItem
from tutorial.spiders.mainichi_spider import MainichiSpider
from tutorial.spiders.cnn_spider import CnnSpider
from tutorial.items import CnnArticleItem
from tutorial.spiders.fox_spider import FoxSpider
from tutorial.items import FoxArticleItem
from tutorial.spiders.msnbc_spider import MsnbcSpider
from tutorial.items import MsnbcArticleItem
from tutorial.spiders.naver_summary_spider import NaverSummarySpider
from tutorial.items import NaverSummaryItem, NaverSummaryDeletedItem
from tutorial.spiders.lexisnexis_spider import LexisNexisSpider
from tutorial.spiders.naver_tv_spider import NaverTvSpider

# Define your item pipelines here
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

class TutorialPipeline(object):
    def process_item(self, item, spider):
        return item

class MySQLPipeline(object):

    db_host = 'localhost'
    db_name = 'mers'
    db_user = 'mers'
    db_pw = 'Kb459CKS7nQLsHbD'

    def open_spider(self, spider):

        if isinstance(spider,NeteaseSpider):
            self.db_name = 'internetNews'
            self.db_user = 'mers_zhwang'
            self.db_pw = 'Khhd7ALtc8XLhwVK'
        elif isinstance(spider,NeteaseSpiderByDay):
            self.db_name = 'internetNews'
            self.db_user = 'mers_zhwang'
            self.db_pw = 'Khhd7ALtc8XLhwVK'
        elif isinstance(spider,CeSpider):
            self.db_name = 'internetNews'
            self.db_user = 'mers_zhwang'
            self.db_pw = 'Khhd7ALtc8XLhwVK'
        elif isinstance(spider,PeoplenetSpider):
            self.db_name = 'internetNews'
            self.db_user = 'mers_hwyun'
            self.db_pw = 'buECAs5ePudeB92R'
        elif isinstance(spider, NaverQuickSpider):
            self.db_name = 'internetNews'
            self.db_user = 'mers_hwyun'
            self.db_pw = 'buECAs5ePudeB92R'
        elif isinstance(spider, XinhuaSpider):
            self.db_name = 'internetNews'
            self.db_user = 'mers_hwyun'
            self.db_pw = 'buECAs5ePudeB92R'
        elif isinstance(spider, GlobaltimesSpider):
            self.db_name = 'internetNews'
            self.db_user = 'mers_hwyun'
            self.db_pw = 'buECAs5ePudeB92R'
        elif isinstance(spider, YahoonewsSpider):
            self.db_name = 'internetNews'
            self.db_user = 'mers_hwyun'
            self.db_pw = 'buECAs5ePudeB92R'
        elif isinstance(spider, SankeiSpider):
            self.db_name = 'internetNews'
            self.db_user = 'mers_hwyun'
            self.db_pw = 'buECAs5ePudeB92R'
        elif isinstance(spider, YomiuriSpider):
            self.db_name = 'internetNews'
            self.db_user = 'mers_hwyun'
            self.db_pw = 'buECAs5ePudeB92R'
        elif isinstance(spider, AsahiSpider):
            self.db_name = 'internetNews'
            self.db_user = 'mers_hwyun'
            self.db_pw = 'buECAs5ePudeB92R'
        elif isinstance(spider, NikkeiSpider):
            self.db_name = 'internetNews'
            self.db_user = 'mers_hwyun'
            self.db_pw = 'buECAs5ePudeB92R'
        elif isinstance(spider, MainichiSpider):
            self.db_name = 'internetNews'
            self.db_user = 'mers_hwyun'
            self.db_pw = 'buECAs5ePudeB92R'
        elif isinstance(spider, CnnSpider):
            self.db_name = 'internetNews'
            self.db_user = 'mers_hwyun'
            self.db_pw = 'buECAs5ePudeB92R'
        elif isinstance(spider, FoxSpider):
            self.db_name = 'internetNews'
            self.db_user = 'mers_hwyun'
            self.db_pw = 'buECAs5ePudeB92R'
        elif isinstance(spider, MsnbcSpider):
            self.db_name = 'internetNews'
            self.db_user = 'mers_hwyun'
            self.db_pw = 'buECAs5ePudeB92R'
        elif isinstance(spider, NaverSummarySpider):
            self.db_name = 'internetNews'
            self.db_user = 'mers_hwyun'
            self.db_pw = 'buECAs5ePudeB92R'
        elif isinstance(spider, LexisNexisSpider):
            self.db_name = 'internetNews'
            self.db_user = 'mers_hwyun'
            self.db_pw = 'buECAs5ePudeB92R'
        elif isinstance(spider, NaverTvSpider):
            self.db_name = 'internetNews'
            self.db_user = 'mers_hwyun'
            self.db_pw = 'buECAs5ePudeB92R'
        try:
            self.conn = MySQLdb.connect(
                    host = self.db_host,
                    user = self.db_user,
                    passwd = self.db_pw,
                    charset = 'utf8'
                    )
            self.cur = self.conn.cursor()
            self.conn.select_db(self.db_name)
        except MySQLdb.Error, e:
            print 'MySQL error %d: %s' % (e.args[0], e.args[1])

    def close_spider(self, spider):
        self.cur.close()
        self.conn.close()

    def process_item(self, item, spider):
        values = []

        table_name = ''
        if isinstance(item, NaverArticleItem):
            table_name = 'articles_naver'
        elif isinstance(item, NeteaseArticleItem):
            table_name = 'articles_163'
        elif isinstance(item, CeArticleItem):
            table_name = 'articles_ce'
        elif isinstance(item, NeteaseCommentItem):
            table_name = 'comments_163'
        elif isinstance(item, NaverCommentItem):
            # cleansing
            # ㅋㅋㅋㅋㅋㅋ/ㅎㅎㅎㅎㅎㅎ => ㅋ/ㅎ
            item['contents'] = re.sub(u'ㅋ{3,}', u'ㅋ', item['contents'], flags = re.M | re.S)
            item['contents'] = re.sub(u'ㅎ{3,}', u'ㅎ', item['contents'], flags = re.M | re.S)
            table_name = 'comments_naver'

        elif isinstance(item, PeoplenetArticleItem):
            table_name = 'articles_people'
            #sql = u'insert into peoplenet_articles (agency,aid,contents,date,title,url,category) values (%s,%s,%s,%s,%s,%s,%s)'
            #sql = u'insert into articles_people (agency,aid,contents,date,title,url,category) values (%s,%s,%s,%s,%s,%s,%s)'
            #self.cur.execute(sql, (item['agency'],item['aid'],item['contents'],item['date'],item['title'],item['url'],item['category']))
            #return item
        elif isinstance(item, PeoplenetCommentItem):
            table_name = 'comments_people'
            #comment_sql = u'insert into peoplenet_comments (aid,date,username,like_count,contents) values (%s,%s,%s,%s,%s,)'
            #comment_sql = u'insert into comments_people (aid,date,username,like_count,contents,comment_id) values (%s,%s,%s,%s,%s,%s)'
            #self.cur.execute(comment_sql, (item['aid'],item['date'],item['username'],item['like_count'],item['contents'],item['comment_id']))
            #return item
        elif isinstance(item, XinhuaArticleItem):
            table_name = 'articles_xinhua'
        elif isinstance(item, XinhuaCommentItem):
            table_name = 'comments_xinhua'
        elif isinstance(item, GlobaltimesArticleItem):
            table_name = 'articles_globaltimes'
        elif isinstance(item, GlobaltimesCommentItem):
            table_name = 'comments_globaltimes'
        elif isinstance(item, YahoonewsArticleItem):
            table_name = 'articles_yahoonews'
        elif isinstance(item, YahoonewsCommentItem):
            table_name = 'comments_yahoonews'
        elif isinstance(item, SankeiArticleItem):
            table_name = 'articles_sankei'
        elif isinstance(item, YomiuriArticleItem):
            table_name = 'articles_yomiuri'
        elif isinstance(item, AsahiArticleItem):
            table_name = 'articles_asahi'
        elif isinstance(item, NikkeiArticleItem):
            table_name = 'articles_nikkei'
        elif isinstance(item, MainichiArticleItem):
            table_name = 'articles_mainichi'
        elif isinstance(item, CnnArticleItem):
            table_name = 'articles_cnn'
        elif isinstance(item, FoxArticleItem):
            table_name = 'articles_fox'
        elif isinstance(item, MsnbcArticleItem):
            table_name = 'articles_msnbc'
        elif isinstance(item, NaverSummaryItem):
            table_name = 'summary_naver'
        elif isinstance(item, NaverSummaryDeletedItem):
            table_name = 'summary_naver_deleted'
        elif isinstance(item, LexisnexisArticleItem):
            table_name = 'articles_lexisnexis'
        sql = u'insert into ' + table_name + ' ('
        for key in item.keys():
            sql += key
            sql += ','
        sql = sql[:-1]
        sql += ') values ('
        for i in item.items():
            values.append((i[1]))
            sql += '%s,'
        sql = sql[:-1]
        sql += ')'
        self.cur.execute(sql, values)
        self.conn.commit()

        return item

