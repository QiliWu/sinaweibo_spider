# -*- coding: utf-8 -*-
import scrapy
import re
from scrapy import Request, FormRequest
import time
import json
from sinaweibo.items import WeiboTopicItem, WeiboInfoItem, TopicUserItem
from scrapy.selector import Selector
from w3lib.html import remove_tags


class WeiboSpider(scrapy.Spider):
    name = 'weibo'
    # allowed_domains = ['weibo.com']
    #从微博领域开始
    start_urls = ['http://v6.bang.weibo.com/czv/domainlist?luicode=40000050']

    def parse(self, response):
        """爬取微博全部领域列表"""
        domainlist = response.css('ul.clearfix a::text').extract()
        linklist = response.css('ul.clearfix a::attr(href)').extract()

        for i in range(len(domainlist)):
            topic = domainlist[i]

            tname = re.match(r'/czv/(.*?)\?luicode.*', linklist[i]).group(1)
            link = 'http://v6.bang.weibo.com/czv/{0}?period=month'.format(tname)
            yield Request(url=link, callback=self.parse_domain_url, meta={'topic':topic})


    def parse_domain_url(self, response):
        match = re.match(r'.*?"currentDate":(\d+).*?"pagetype":"(\d+)".*?"domainId":(\d+).*', response.text, re.S)
        date = match.group(1)
        type = match.group(2)
        domainId = int(match.group(3))
        post_data = {'type': type,
                     'period': 'month',
                     'date': date,
                     'pagesize': '100',
                     'page': '1',
                     'domainId': str(domainId),
                     '_t': '0'}
        post_url = 'http://v6.bang.weibo.com/aj/wemedia/rank?ajwvr=6&__rnd={0}'
        headers = {'Content-Type':'application/x-www-form-urlencoded',
                             'X-Requested-With': 'XMLHttpRequest',
                             'Referer':response.url}
        yield FormRequest(url=post_url.format(int(time.time()*1000)),
                          method='POST',
                          formdata=post_data,
                          headers=headers,
                          callback=self.parse_domain_detail,
                          meta={'domainId':domainId})

        topicitem = WeiboTopicItem()
        #领域ID
        topicitem['domainId'] = domainId
        #领域名称
        topicitem['topic'] = response.meta['topic']
        #领域博主排行榜url
        topicitem['topic_url'] = response.url
        yield topicitem


    def parse_domain_detail(self, response):
        result = json.loads(response.text)
        datalist = result['data']['rankData']
        cookies = {'SINAGLOBAL': '6766495850665.497.1501852555183',
                   'SUB': '_2AkMtfS1zf8NxqwJRmP0TzmziboRyywzEieKbIdyoJRMxHRl-yT9kqlEitRB6XNyh2MtIX_786TcqrC_9KhHomc2jrviO',
                   'SUBP': '0033WrSXqPxfM72-Ws9jqgMF55529P9D9WWTsTi36AWHDVnU2ITVs6AB',
                   'UM_distinctid': '1621ce4477d161-044b65bce7d5c1-b353461-100200-1621ce4477ecc',
                   'UOR': 'news.youth.cn,widget.weibo.com,www.baidu.com',
                   '_s_tentry': '-',
                   'Apache': '811175706409.3062.1526986486457',
                   'TC-Page-G0': '1e758cd0025b6b0d876f76c087f85f2c'}
        for data in datalist:
            useritem = TopicUserItem()
            #领域ID
            useritem['domainId'] = response.meta['domainId']
            #博主ID
            useritem['uid'] = data['uid']

            #博主影响力分数
            useritem['score'] = float(data['score'])
            #博主排名
            useritem['rank'] = int(data['seq'])
            #博主简介
            useritem['description'] = data['desc']
            #博主用户名
            useritem['uname'] = data['screen_name']
            #博主微博主页url
            useritem['user_url'] = data['profile_url']
            #博主头像url
            useritem['img_url'] = data['profile_img_url']

            #请求微博个人主页时需要带上cookie
            yield Request(url=data['profile_url'],
                          cookies=cookies,
                          callback=self.parse_user_weibo,
                          meta={'useritem':useritem})


    def parse_user_weibo(self, response):
        useritem = response.meta['useritem']
        match_1 = re.match(
            r'.*?<strong class=\\"W_f\d+\\">(\d+)<.*?<strong class=\\"W_f\d+\\">(\d+)<.*?<strong class=\\"W_f\d+\\">(\d+)<.*',
            response.text, re.S)
        #博主关注人数
        useritem['following_num'] = int(match_1.group(1)) if match_1 else 0
        #博主的粉丝数
        useritem['follower_num'] = int(match_1.group(2)) if match_1 else 0
        #博主发表微博数
        useritem['weibo_num'] = int(match_1.group(3)) if match_1 else 0

        match_level= re.match(r'.*微博等级(\d+).*', response.text, re.S)
        #微博账号等级
        useritem['account_level'] = int(match_level.group(1))

        match_addr = re.match(r'.*W_ficon ficon_cd_place S_ficon.*?<span.*?>(.+?)<.*',response.text, re.S)
        addr = match_addr.group(1).strip() if match_addr else ''
        #博主所在城市
        useritem['address'] = re.sub(r'(\s|\\r|\\t|\\n)', '', addr)

        match_college = re.match(r'.*>毕业于.*?<a.*?>(.+?)<.*',
                              response.text, re.S)
        # 毕业院校
        useritem['college'] = match_college.group(1) if match_college else ''

        match_birth = re.match(r'.*W_ficon ficon_constellation S_ficon.*?<span.*?>(.+?)<.*', response.text, re.S)
        birth = match_birth.group(1) if match_birth else ''
        #博主生日
        useritem['birthday'] = re.sub(r'(\s|\\r|\\t|\\n)', '', birth)
        #性别
        if 'W_icon icon_pf_male' in response.text:
            useritem['gender'] = 'male'
        elif 'W_icon icon_pf_female' in response.text:
            useritem['gender'] = 'female'
        else:
            useritem['gender'] = 'undefined'

        yield useritem

        #请求微博内容的json数据
        domain = re.match(r".*CONFIG\['domain'\]='(\d+?)'.*", response.text, re.S).group(1)
        pl_name = re.match(r'.*domid":"(Pl_Official_MyProfileFeed__\d+)".*', response.text, re.S).group(1)
        page_id = domain + useritem['uid']
        script_uri = '/u/'+useritem['uid']

        weibo_url = 'https://weibo.com/p/aj/v6/mblog/mbloglist?ajwvr=6&domain={0}&is_hot=1&pagebar={1}&pl_name={2}&id={3}&script_uri={4}&feed_type=0&page=1&pre_page=1&domain_op={0}&__rnd={5}'
        #微博内容是json, 每页15条，爬取前60条
        for pagebar in range(4):
            yield Request(url=weibo_url.format(domain, pagebar, pl_name, page_id, script_uri, int(time.time()*1000)),
                          callback=self.parse_weibo_detail)

    def parse_weibo_detail(self, response):

        r = json.loads(response.text)
        data = r['data']
        selector = Selector(text=data)
        weibolist = selector.css('div[action-type="feed_list_item"]')
        for weibo in weibolist:
            weiboitem = WeiboInfoItem()
            #微博编号
            #有时候一个博主主页会有重复相同的微博，他们的mid是一样的。在插入数据库时会因为重复键而去除
            weiboitem['mid'] = weibo.css('div::attr(mid)').extract()[0]
            #发布者名称
            weiboitem['uname'] = weibo.css('a.W_f14.W_fb.S_txt1::text').extract()[0]
            #发布日期
            weiboitem['pub_date'] = weibo.css('a[node-type="feed_list_item_date"]::attr(title)').extract()[0]
            #微博内容
            weibotext = weibo.css('div[node-type="feed_list_content"]').extract()
            co = re.compile(u'[\U00010000-\U0010ffff]')   #去除表情符号
            clean_weibotext = co.sub('', remove_tags(''.join(weibotext)).strip())
            weiboitem['weibotext'] = clean_weibotext
            # 微博图片链接
            weiboimg= weibo.css('li[action-type="feed_list_media_img"] img::attr(src)').extract_first()
            weiboitem['weiboimg'] = ('https:'+weiboimg) if weiboimg else ''
            #转发数
            try:
                weiboitem['forward_nums'] = int(weibo.css('span[node-type="forward_btn_text"] em::text').extract()[1])
            except:
                weiboitem['forward_nums'] = 0
            #留言数
            try:
                weiboitem['comment_nums'] = int(weibo.css('span[node-type="comment_btn_text"] em::text').extract()[1])
            except:
                weiboitem['comment_nums'] = 0
            #点赞数
            try:
                weiboitem['praised_nums'] = int(weibo.css('span[node-type="like_status"] em::text').extract()[1])
            except:
                weiboitem['praised_nums'] = 0
            yield weiboitem









