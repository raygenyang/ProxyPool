from gevent import monkey
monkey.patch_socket()
import gevent
import proxy_spider.spider
from proxy_test.check import check_proxy
from proxy_spider.crwaler import Crwaler,spawn


def get_all_spiders():
    all_spiders = []
    for cls in proxy_spider.spider.ProxySpider.__subclasses__():
        if getattr(cls, 'enable', None):
            all_spiders.append(cls())
    return all_spiders


def run(spider):
    crwaler = Crwaler(spider)
    crwaler.crwal()


def process_item():
    q = Crwaler.item_q
    pq = Crwaler.proxy_q
    @spawn(Crwaler.pool)
    def check(proxy, name):
        if check_proxy(proxy, name):
            # print('proxy:', proxy)
            if not pq.full():
                pq.put(proxy)
    while True:
        if q.qsize() > 0:
            item = q.get()
            # print('\t\t',item)
            proxy = Crwaler.item_to_proxy(item)
            check(proxy, item['name'])
        gevent.sleep(0.01)




if __name__ == '__main__':
    threads = []
    for proxy_spider in get_all_spiders():
        threads.append(gevent.spawn(run, proxy_spider))
    threads.append(gevent.spawn(process_item))
    gevent.joinall(threads)



