# sinaweibo_spider
项目相关博客：
python爬取和分析新浪微博（一）：scrapy构建新浪微博榜单、博主及微博信息爬虫（https://zhuanlan.zhihu.com/p/37352273）。

python爬取和分析新浪微博（二）：微博影响力榜用户数据和微博内容的信息挖掘及可视化展示（https://zhuanlan.zhihu.com/p/37360258）

项目具体信息：
使用scrapy, mysql实现的一个新浪微博网络爬虫。将爬取到的微博领域数据，各领域榜单博主信息和博主的微博信息分别存入本地的mysql数据库对应的表格中。
使用pandas, numpy, matplotlib和wordcloud的工具对爬取到的结果进行了简单的数据分析，并生成了词云。

    1.爬虫逻辑
    爬取了V影响力榜（http://v6.bang.weibo.com/czv/domainlist?luicode=40000050）列出的微博全部领域名称及对应的各领域微博榜单链接。
    再由这些链接分别进入各领域排行榜页面，抓取 4月 月榜 排名前100的博主相关信息。获得每个博主的信息（包括博主的昵称，id, 粉丝数，关注数，微博数，性别，地址等信息）。
    进入该博主的微博主页，爬取该博主最近的前60条微博信息（包括微博内容，发表日期，转发/点赞/评论数等信息）
    
    2. 底层存储设置
    将上述三步爬取结果分别存入本地MySQL的三个数据表中。
    使用了twisted提供的adbapi包，将数据插入到数据库变为一个异步过程。
    
    3. 避免爬虫被禁的策略：
    实现了一个RandomUserAgentMiddleware， 可以不停的改变user-agent
    实现了一个ProxyMiddleware，可以不停地改变ip代理。ip购买自蘑菇ip代理(http://www.moguproxy.com)，通过不断请求蘑菇代理提供的api连接，获取ip地址，存入mysql数据库。每次发出一个请求时都随机从数据表中选取一个ip，取出的ip会先通过请求ip验证网站来验证有效性，无效的ip会被抛弃，然后重复前面的步骤，知道获取到有效的ip并将它配置给Request对象。
    
    4. 数据分析
    对各领域平均粉丝数和微博数，博主男女比，博主地理位置，粉丝最多的博主top10，微博最多的博主TOP10，点赞/转发/评论数TOP10的微博信息进行了分析，同时还对各领域微博内容进行了词云分析。

需要使用的库：
scrapy, requests, mysqldb, fake-useragent, numpy, pandas, matplotlib, wordcloud
    
