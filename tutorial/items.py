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

class LexisnexisArticleItem(scrapy.Item):
    aid = scrapy.Field()
    date = scrapy.Field()
    title = scrapy.Field()
    contents = scrapy.Field()
    url = scrapy.Field()
    agency = scrapy.Field()
    keywords = scrapy.Field()
    tagged_text = scrapy.Field()


class MsnbcArticleItem(scrapy.Item):
    aid = scrapy.Field()
    date = scrapy.Field()
    title = scrapy.Field()
    contents = scrapy.Field()
    url = scrapy.Field()
    keywords = scrapy.Field()
    tagged_text = scrapy.Field()

class MainichiArticleItem(scrapy.Item):
    aid = scrapy.Field()
    date = scrapy.Field()
    title = scrapy.Field()
    contents = scrapy.Field()
    url = scrapy.Field()
    keywords = scrapy.Field()
    tagged_text = scrapy.Field()

class YomiuriArticleItem(scrapy.Item):
    aid = scrapy.Field()
    date = scrapy.Field()
    title = scrapy.Field()
    contents = scrapy.Field()
    url = scrapy.Field()
    keywords = scrapy.Field()
    tagged_text = scrapy.Field()
class XinhuaCommentItem(scrapy.Item):
    date = scrapy.Field()
    aid = scrapy.Field()
    username = scrapy.Field()
    like_count = scrapy.Field()
    dislike_count = scrapy.Field()
    contents = scrapy.Field()
    comment_id = scrapy.Field()
class XinhuaArticleItem(scrapy.Item):
    aid = scrapy.Field()
    date = scrapy.Field()
    agency = scrapy.Field()
    title = scrapy.Field()
    contents = scrapy.Field()
    url = scrapy.Field()
    category = scrapy.Field()
    keywords = scrapy.Field()
    tagged_text = scrapy.Field()


class MbcArticleItem(scrapy.Item):
    aid = scrapy.Field()
    date = scrapy.Field()
    reporter = scrapy.Field()
    title = scrapy.Field()
    contents = scrapy.Field()
    url = scrapy.Field()
    keywords = scrapy.Field()
    tagged_text = scrapy.Field()

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
    keywords = scrapy.Field()
    tagged_text = scrapy.Field()

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
    keywords = scrapy.Field()
    tagged_text = scrapy.Field()

class NeteaseCommentItem(scrapy.Item):
    date = scrapy.Field()
    aid = scrapy.Field()
    username = scrapy.Field()
    like_count = scrapy.Field()
    dislike_count = scrapy.Field()
    contents = scrapy.Field()
    comment_id = scrapy.Field()

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
    keywords = scrapy.Field()
    tagged_text = scrapy.Field()

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
    keywords = scrapy.Field()
    tagged_text = scrapy.Field()
class GlobaltimesArticleItem(scrapy.Item):
    aid = scrapy.Field()
    #oid = scrapy.Field()
    date =scrapy.Field()
    agency = scrapy.Field()
    title = scrapy.Field()
    contents = scrapy.Field()
    url = scrapy.Field()
    #referer = scrapy.Field()
    category = scrapy.Field()
    keywords = scrapy.Field()
    tagged_text = scrapy.Field()

class GlobaltimesCommentItem(scrapy.Item):
    date = scrapy.Field()
    aid = scrapy.Field()
    username = scrapy.Field()
    like_count = scrapy.Field()
    #dislike_count = scrapy.Field()
    contents = scrapy.Field()
    comment_id = scrapy.Field()

class YahoonewsArticleItem(scrapy.Item):
    aid = scrapy.Field()
    #oid = scrapy.Field()
    date =scrapy.Field()
    agency = scrapy.Field()
    title = scrapy.Field()
    contents = scrapy.Field()
    url = scrapy.Field()
    #referer = scrapy.Field()
    category = scrapy.Field()
    video = scrapy.Field()
    keywords = scrapy.Field()
    tagged_text = scrapy.Field()

class YahoonewsCommentItem(scrapy.Item):
    date = scrapy.Field()
    aid = scrapy.Field()
    username = scrapy.Field()
    like_count = scrapy.Field()
    dislike_count = scrapy.Field()
    contents = scrapy.Field()
    comment_id = scrapy.Field()

class SankeiArticleItem(scrapy.Item):
    aid = scrapy.Field()
    #oid = scrapy.Field()
    date =scrapy.Field()
    agency = scrapy.Field()
    title = scrapy.Field()
    contents = scrapy.Field()
    url = scrapy.Field()
    #referer = scrapy.Field()
    category = scrapy.Field()
    video = scrapy.Field()
    keywords = scrapy.Field()
    tagged_text = scrapy.Field()

class AsahiArticleItem(scrapy.Item):
    aid = scrapy.Field()
    #oid = scrapy.Field()
    date =scrapy.Field()
    agency = scrapy.Field()
    title = scrapy.Field()
    contents = scrapy.Field()
    url = scrapy.Field()
    #referer = scrapy.Field()
    category = scrapy.Field()
    video = scrapy.Field()
    keywords = scrapy.Field()
    tagged_text = scrapy.Field()

class NikkeiArticleItem(scrapy.Item):
    aid = scrapy.Field()
    date =scrapy.Field()
    agency = scrapy.Field()
    title = scrapy.Field()
    contents = scrapy.Field()
    url = scrapy.Field()
    category = scrapy.Field()
    keywords = scrapy.Field()
    tagged_text = scrapy.Field()

class CnnArticleItem(scrapy.Item):
    aid = scrapy.Field()
    date =scrapy.Field()
    agency = scrapy.Field()
    title = scrapy.Field()
    contents = scrapy.Field()
    url = scrapy.Field()
    category = scrapy.Field()
    keywords = scrapy.Field()
    tagged_text = scrapy.Field()

class FoxArticleItem(scrapy.Item):
    aid = scrapy.Field()
    date =scrapy.Field()
    agency = scrapy.Field()
    title = scrapy.Field()
    contents = scrapy.Field()
    url = scrapy.Field()
    category = scrapy.Field()
    keywords = scrapy.Field()
    tagged_text = scrapy.Field()

class NaverSummaryItem(scrapy.Item):
    aid = scrapy.Field()
    date = scrapy.Field()
    agency = scrapy.Field()
    title = scrapy.Field()
    summary = scrapy.Field()
    summary_unfilt = scrapy.Field()
    contents = scrapy.Field()
    contents_unfilt = scrapy.Field()
    url = scrapy.Field()
    category = scrapy.Field()
    referer = scrapy.Field()

class NaverSummaryDeletedItem(scrapy.Item):
    aid = scrapy.Field()
    date = scrapy.Field()
    agency = scrapy.Field()
    title = scrapy.Field()
    summary = scrapy.Field()
    contents = scrapy.Field()
    url = scrapy.Field()
    category = scrapy.Field()
    referer = scrapy.Field()

