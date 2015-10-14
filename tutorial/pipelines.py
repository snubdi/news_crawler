# -*- coding: utf-8 -*-

import re
import MySQLdb
from tutorial.items import NaverArticleItem,NaverCommentItem,MbcArticleItem,NeteaseArticleItem,NeteaseCommentItem
from tutorial.spiders.netease_spider_byday import NeteaseSpiderByDay
from tutorial.spiders.netease_spider import NeteaseSpider
from tutorial.spiders.naver_quick_spider import NaverQuickSpider
from tutorial.spiders.peoplenet_spider import PeoplenetSpider
from tutorial.items import PeoplenetArticleItem, PeoplenetCommentItem
from tutorial.spiders.ce_spider import CeSpider
from tutorial.items import CeArticleItem


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
            table_name = 'articles'
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
            table_name = 'comments'

        elif isinstance(item, PeoplenetArticleItem):
            #table_name = 'peoplenet_articles'
            table_name = 'articles_people'
            #sql = u'insert into peoplenet_articles (agency,aid,contents,date,title,url,category) values (%s,%s,%s,%s,%s,%s,%s)'
            sql = u'insert into articles_people (agency,aid,contents,date,title,url,category) values (%s,%s,%s,%s,%s,%s,%s)'
            self.cur.execute(sql, (item['agency'],item['aid'],item['contents'],item['date'],item['title'],item['url'],item['category']))
            return item
        elif isinstance(item, PeoplenetCommentItem):
            #table_name = 'peoplenet_comments'
            table_name = 'comments_people'
            #comment_sql = u'insert into peoplenet_comments (aid,date,username,like_count,contents) values (%s,%s,%s,%s,%s,)'
            comment_sql = u'insert into comments_people (aid,date,username,like_count,contents,comment_id) values (%s,%s,%s,%s,%s,%s)'
            self.cur.execute(comment_sql, (item['aid'],item['date'],item['username'],item['like_count'],item['contents'],item['comment_id']))
            return item
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

