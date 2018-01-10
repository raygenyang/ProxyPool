from gevent import monkey
monkey.patch_socket()
import gevent
import proxy_spider.spider
from proxy_spider.check import check_proxy
from proxy_spider.crwaler import Crwaler, spawn
from db import RedisQueue


# 获取所有可用爬虫类
def get_all_spiders():
    all_spiders = []
    for cls in proxy_spider.spider.ProxySpider.__subclasses__():
        if getattr(cls, 'enable', None):
            all_spiders.append(cls())
    return all_spiders


# 启动爬虫
def run(spider):
    crwaler = Crwaler(spider)
    crwaler.crwal()


# 处理爬取数据
def process_item():
    # 爬取结果队列
    q = Crwaler.item_q
    # 爬虫代理队列
    pq = Crwaler.proxy_q
    # 有效代理队列
    rq = RedisQueue('ProxyPool')

    # 检查代理有效性
    @spawn(Crwaler.pool)
    def check(proxy, name):
        # print(name, proxy)
        priority = check_proxy(proxy, name)
        if priority > 0:
            # 加入到爬虫代理队列
            if not pq.full():
                pq.put(proxy)
            # 存入数据库
            rq.put((proxy, priority))

    while True:
        if q.qsize() > 0:
            item = q.get()
            proxy = Crwaler.item_to_proxy(item)
            name = item.get('name', None)
            check(proxy, name)
        # 轮询间隔1ms
        gevent.sleep(0.001)


if __name__ == '__main__':
    threads = []
    # 启动爬虫协程
    for proxy_spider in get_all_spiders():
        threads.append(gevent.spawn(run, proxy_spider))
    # 启动数据处理协程
    threads.append(gevent.spawn(process_item))
    # 等待所有协程完成
    gevent.joinall(threads)