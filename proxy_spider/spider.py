from lxml import etree

from proxy_spider.crwaler import Request


class ProxySpider(object):
    name = None
    enable = False

    def __init__(self, name=None, **kwargs):
        if name is not None:
            self.name = name
        elif not getattr(self, 'name', None):
            raise ValueError("%s must have a name" % type(self).__name__)
        self.__dict__.update(kwargs)
        if not hasattr(self, 'start_urls'):
            self.start_urls = []

    def start_request(self):
        rst = []
        for url in self.start_urls:
            yield Request(url, callback=self.parse)

    def parse(self, response):
        raise NotImplemented


class XiciSpider(ProxySpider):
    name = 'xici'
    enable = True

    def start_request(self):
        for i in range(1, 1000):
            next_url = 'http://www.xicidaili.com/nn/{}'.format(str(i))
            # print(next_url, time.time())
            yield Request(next_url, callback=self.parse)

    def parse(self, response):
        tree = etree.HTML(response.text)
        selectors = tree.xpath('//*[@id="ip_list"]//tr[@class="odd"]')
        for selector in selectors:
            ip = selector.xpath('./td[2]/text()').pop()
            port = selector.xpath('./td[3]/text()').pop()
            nm = selector.xpath('./td[5]/text()').pop()
            protocol = selector.xpath('./td[6]/text()').pop()
            if nm == '高匿':
                yield dict(ip=ip, port=port, protocol=protocol, name=self.name)


class KuaidailiSpider(ProxySpider):
    name = 'kuaidaili'
    enable = True

    def start_request(self):
        for i in range(1, 1000):
            url = 'https://www.kuaidaili.com/free/inha/{}/'.format(i)
            yield Request(url, callback=self.parse)

    def parse(self, response):
        tree = etree.HTML(response.text)
        selectors = tree.xpath('//*[@id="list"]/table/tbody/tr')
        for selector in selectors:
            ip = selector.xpath('./td[@data-title="IP"]/text()').pop()
            port = selector.xpath('./td[@data-title="PORT"]/text()').pop()
            nm = selector.xpath('./td[@data-title="匿名度"]/text()').pop()
            protocol = selector.xpath('./td[@data-title="类型"]/text()').pop()
            if nm == '高匿名':
                yield dict(ip=ip, port=port, protocol=protocol, name=self.name)


class Ip66Spider(ProxySpider):
    name = '66ip'
    enable = True

    def start_request(self):
        for i in range(1, 1000):
            url = 'http://www.66ip.cn/{}.html'.format(i)
            yield Request(url, callback=self.parse)

    def parse(self, response):
        html = response.content.decode('gbk')
        tree = etree.HTML(html)
        # with open('5.html', 'w+') as f:
        #     f.write(html)
        selectors = tree.xpath('//*[@id="main"]/div/div[1]/table/tr[position()>1]')
        for selector in selectors:
            ip = selector.xpath('./td[1]/text()').pop()
            port = selector.xpath('./td[2]/text()').pop()
            nm = selector.xpath('./td[4]/text()').pop()
            protocol = 'http'
            if nm == '高匿代理':
                yield dict(ip=ip, port=port, protocol=protocol, name=self.name)


class NianshaoSpider(ProxySpider):
    name = 'nianshao'
    enable = True

    def start_request(self):
        for i in range(1, 100):
            url = 'http://www.nianshao.me/?stype=1&page={}'.format(i)
            yield Request(url, callback=self.parse)
        for i in range(1, 100):
            url = 'http://www.nianshao.me/?stype=2&page={}'.format(i)
            yield Request(url, callback=self.parse)

    def parse(self, response):
        html = response.content.decode('gbk')
        tree = etree.HTML(html)
        selectors = tree.xpath('//*[@id="main"]/div/div/table/tbody/tr')
        for selector in selectors:
            ip = selector.xpath('./td[1]/text()').pop()
            port = selector.xpath('./td[2]/text()').pop()
            nm = selector.xpath('./td[4]/text()').pop()
            protocol = selector.xpath('./td[5]/text()').pop()
            if nm == '高匿':
                yield dict(ip=ip, port=port, protocol=protocol, name=self.name)






