from scrapy.cmdline import execute
import os
import sys

path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(path)
execute(['scrapy', 'crawl', 'weibo'])