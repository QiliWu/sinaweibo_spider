# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class SinaweiboItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class WeiboTopicItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    topic = scrapy.Field()
    domainId = scrapy.Field()
    topic_url = scrapy.Field()

    def get_insert_sql(self):
        params = (self['topic'], self['domainId'], self['topic_url'])
        sql = """INSERT INTO weibotopic (topic, domainId, topic_url) VALUES (%s, %s, %s)"""
        return sql, params



class TopicUserItem(scrapy.Item):
    domainId = scrapy.Field()
    uid = scrapy.Field()
    rank = scrapy.Field()
    score = scrapy.Field()
    description = scrapy.Field()
    uname = scrapy.Field()
    user_url = scrapy.Field()
    img_url = scrapy.Field()
    following_num = scrapy.Field()
    follower_num = scrapy.Field()
    weibo_num = scrapy.Field()
    account_level = scrapy.Field()
    address = scrapy.Field()
    gender = scrapy.Field()
    birthday = scrapy.Field()
    college = scrapy.Field()

    def get_insert_sql(self):
        params = (self['uid'], self['domainId'], self['rank'], self['score'],
                  self['description'], self['uname'], self['user_url'], self['img_url'],
                  self['following_num'], self['follower_num'], self['weibo_num'], self['account_level'],
                  self['address'], self['gender'], self['birthday'], self['college'])

        sql = """INSERT INTO topicuser (uid, domainId, rank, score,
                                        description, uname, user_url, img_url,
                                        following_num, follower_num, weibo_num, account_level,
                                        address, gender, birthday, college) VALUES 
                                       (%s, %s, %s, %s, 
                                       %s, %s, %s, %s,
                                       %s, %s, %s, %s,
                                       %s, %s, %s, %s)"""
        return sql, params


class WeiboInfoItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    mid = scrapy.Field()
    uname = scrapy.Field()
    pub_date = scrapy.Field()
    weibotext = scrapy.Field()
    weiboimg = scrapy.Field()
    forward_nums = scrapy.Field()
    comment_nums = scrapy.Field()
    praised_nums = scrapy.Field()

    def get_insert_sql(self):
        params = (self['mid'], self['uname'], self['pub_date'], self['weibotext'],
                  self['weiboimg'], self['forward_nums'], self['comment_nums'], self['praised_nums'])

        sql = """INSERT INTO weiboinfo (mid, uname, pub_date, weibotext, weiboimg,
                                        forward_nums, comment_nums, praised_nums) VALUES 
                                       (%s, %s, %s, %s, %s, %s, %s, %s)"""
        return sql, params
