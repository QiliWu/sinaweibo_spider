import requests
import json, re
import MySQLdb


class GetIP(object):
    conn = MySQLdb.connect(
        host='127.0.0.1',
        port=3306,
        user='root',
        password='passwork',
        database='ippool')
    cursor = conn.cursor()


    def get_ip_from_api(self):
        url = 'http://piping.mogumiao.com/proxy/api/get_ip_al?appKey=e5egfdseg4b454882e8894592cf3bca&count=5&expiryDate=0&format=1&newLine=2'

        r = requests.get(url=url)
        data = json.loads(r.text)
        for proxy in data['msg']:
            port = proxy['port']
            ip = proxy['ip']
            http_proxy_ip = 'http://'+ip + ':' + port
            https_proxy_ip = 'https://' + ip + ':' + port
            #print(proxy_ip)
            #多条插入使用executemany
            self.cursor.executemany(
                'INSERT INTO mogu_ip(proxy_ip) VALUES (%s)', [(http_proxy_ip,),(https_proxy_ip,)])
            self.conn.commit()
        print('成功下载新的ip')

    def check_ip(self, proxy_dict):
        # 判断ip是否可用, 不能去请求百度来验证，有可能是用本地ip请求的
        http_url = 'http://ip.chinaz.com/getip.aspx'
        try:

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36'}
            response = requests.get(
                http_url, headers=headers, proxies=proxy_dict, timeout=2)
            response.raise_for_status()
            code = response.status_code
            #print(proxy_dict)
            if code >= 200 and code < 300:
                text = response.text
                for key, value in proxy_dict.items():
                    ip = re.match(r'.*://(.*?):\d+', value).group(1)
                    if ip in text:
                        return True
                    else:
                        return False
            else:
                return False
        except BaseException:
            return False

    def get_random_valid_ip(self):
        # 从数据库提取一个有效的ip
        self.cursor.execute(
                'SELECT id, proxy_ip FROM mogu_ip ORDER BY rand() LIMIT 1')
        #print(dir(cursor))
        if self.cursor.rowcount:
            for ip_info in self.cursor.fetchall():
                id = ip_info[0]
                proxy = ip_info[1]
                key = proxy.split(':')[0]
                proxy_dict = {key: proxy}
                if self.check_ip(proxy_dict):
                    # print("有效ip:%s" % proxy)
                    return proxy_dict,proxy


                else:
                    self.cursor.execute(
                        'DELETE FROM mogu_ip WHERE id= {0}'.format(id))
                    self.conn.commit()
                    return self.get_random_valid_ip()

        else:
            print("数据库中没有ip了，重新下载新的ip")
            self.get_ip_from_api()
            return self.get_random_valid_ip()

    def close_conn(self):
        self.conn.close()

# G = GetIP()
# G.get_random_valid_ip()