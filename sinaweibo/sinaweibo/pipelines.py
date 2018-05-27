# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html


class SinaweiboPipeline(object):
    def process_item(self, item, spider):
        return item

import MySQLdb
import MySQLdb.cursors
from twisted.enterprise import adbapi

class MysqlTwistedPipeline(object):
    # 通过twisted 实现数据库的异步操作
    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):
        dbparams = dict(
            host='127.0.0.1',
            user='root',
            password='password',
            database='sina',
            charset='utf8',
            cursorclass=MySQLdb.cursors.DictCursor,
            use_unicode=True
        )
        dbpool = adbapi.ConnectionPool('MySQLdb', **dbparams)
        return cls(dbpool)

    def process_item(self, item, spider):
        query = self.dbpool.runInteraction(self.do_insert, item)
        query.addErrback(self.handle_error, item)
        return item

    def handle_error(self, failure, item):
        print(failure)

    def do_insert(self, cursor, item):
        sql, params = item.get_insert_sql()
        cursor.execute(sql, params)
        print('成功插入一条item: %s' % item.__class__)