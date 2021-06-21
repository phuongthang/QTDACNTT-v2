# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy.exceptions import DropItem
from itemadapter import ItemAdapter
from datetime import datetime
from fbcrawl.items import FbcrawlItem, CommentsItem
import pymongo
import logging

class FbcrawlPipeline(object):

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        ## pull in information from settings.py
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE', 'items')
        )

    def open_spider(self, spider):
        ## initializing spider
        ## opening db connection
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        ## clean up when spider is closed
        self.client.close()

    def process_item(self, item, spider):
        collection_name = ''
        if(type(item) is FbcrawlItem):
            collection_name = 'post'
        elif(type(item) is CommentsItem):
            collection_name = 'comment'
        self.db[collection_name].insert(dict(item))
        logging.debug("Post added to MongoDB")
        return item