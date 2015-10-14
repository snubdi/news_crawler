# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.item import Item, Field
from scrapy.contrib.loader import XPathItemLoader
from scrapy.contrib.loader.processor import TakeFirst

class TutorialItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class MbcArticleItem(scrapy.Item):
    aid = scrapy.Field()
    date = scrapy.Field()
    reporter = scrapy.Field()
    title = scrapy.Field()
    contents = scrapy.Field()
    url = scrapy.Field()

class NaverArticleItem(scrapy.Item):
    aid = scrapy.Field()
    oid = scrapy.Field()
    date = scrapy.Field()
    agency = scrapy.Field()
    title = scrapy.Field()
    contents = scrapy.Field()
    url = scrapy.Field()
    referer = scrapy.Field()
    position = scrapy.Field()

class NaverCommentItem(scrapy.Item):
    date = scrapy.Field()
    aid = scrapy.Field()
    username = scrapy.Field()
    like_count = scrapy.Field()
    dislike_count = scrapy.Field()
    contents = scrapy.Field()

class NeteaseArticleItem(scrapy.Item):
    aid = scrapy.Field()
    oid = scrapy.Field()
    date = scrapy.Field()
    category = scrapy.Field()
    agency = scrapy.Field()
    title = scrapy.Field()
    contents = scrapy.Field()
    url = scrapy.Field()
    referer = scrapy.Field()

class NeteaseCommentItem(scrapy.Item):
    date = scrapy.Field()
    aid = scrapy.Field()
    username = scrapy.Field()
    like_count = scrapy.Field()
    dislike_count = scrapy.Field()
    contents = scrapy.Field()

class PeoplenetArticleItem(scrapy.Item):
    aid = scrapy.Field()
    #oid = scrapy.Field()
    date =scrapy.Field()
    agency = scrapy.Field()
    title = scrapy.Field()
    contents = scrapy.Field()
    url = scrapy.Field()
    #referer = scrapy.Field()
    category = scrapy.Field()

class PeoplenetCommentItem(scrapy.Item):
    date = scrapy.Field()
    aid = scrapy.Field()
    username = scrapy.Field()
    like_count = scrapy.Field()
    dislike_count = scrapy.Field()
    contents = scrapy.Field()
    comment_id = scrapy.Field()

class CeArticleItem(scrapy.Item):
    aid = scrapy.Field()
    date = scrapy.Field()
    agency = scrapy.Field()
    title = scrapy.Field()
    contents = scrapy.Field()
    url = scrapy.Field()
    category = scrapy.Field()
