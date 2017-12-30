from gevent import monkey
monkey.patch_all()
import gevent
from gevent.pool import Pool
from gevent.queue import Queue, PriorityQueue
import requests
import settings
import logging


def spawn(pool=gevent):
    def decorator(func):
        def wrapper(*args, **kwargs):
            rst = pool.spawn(func, *args, **kwargs)
            return rst
        return wrapper
    return decorator


class Request(requests.Request):
    def __init__(self, url, method='GET', callback=None, meta={}, **kwargs):
        super(Request, self).__init__(method, url, **kwargs)
        self.callback = callback
        self.meta = meta
        self.retries = 0
        self._prepare()

    def _prepare(self):
        default_headers = getattr(settings, 'DEFAULT_REQUEST_HEADERS', {})
        for k, v in default_headers.items():
            self.headers.setdefault(k, v)
        if self.cookies is None:
            self.cookies = getattr(settings, 'DEFAULT_COOKIES', {})
        self.user_agent = getattr(settings, 'DEFAULT_USER_AGENT', None)
        if self.user_agent:
            self.headers.setdefault('User-Agent', self.user_agent)

    def __lt__(self, r):
        return False


class Crwaler(object):
    pool_size = getattr(settings, 'CONCURRENT_REQUESTS', 10)
    pool = Pool(pool_size)
    item_q = Queue(maxsize=10000)
    proxy_q = Queue(maxsize=100)
    __crwalers = {}

    def __new__(cls, *args, **kwargs):
        spider = args[0]
        if Crwaler.__crwalers.get(spider.name, None) is None:
            Crwaler.__crwalers[spider.name] = super(Crwaler, cls).__new__(cls)
        return Crwaler.__crwalers[spider.name]

    def __init__(self, spider):
        self.proxy_enable = getattr(spider, 'proxy_enable', None) or getattr(settings, 'PROXY_ENABLE', False)
        self.spider = spider
        self.download_delay = getattr(spider, 'download_delay', None) or getattr(settings, 'DOWNLOAD_DELAY', 0.01)
        self.downloader = Downloader(self)
        self.request_q = PriorityQueue(maxsize=5000)
        self.count = 1
        self.started = False

    def crwal(self):
        if not self.started and self.request_q.empty():
            for request in self.spider.start_request():
                if isinstance(request, Request):
                    self.put_request(request)
                elif isinstance(request, dict):
                    self.process_item(request)
        self.started = True

        while True:
            if self.request_q.qsize() > 0:
                request = self.get_request()
                proxies = None
                if self.proxy_enable:
                    proxies = self.get_proxies()
                if proxies is not None:
                    setattr(request, 'proxies', proxies)
                else:
                    gevent.sleep(self.download_delay)
                self.process_request(request)
            gevent.sleep(0.001)

    def put_request(self, request):
        priority = getattr(request, 'priority', 0)
        self.request_q.put((-priority, request))

    def get_request(self):
        _, request = self.request_q.get()
        return request

    @spawn(pool)
    def process_request(self, request):
        response = self.downloader.download(request)
        self.process_response(response, callback=request.callback)

    def process_response(self, response, callback=None):
        if response is None:
            return
        if isinstance(response, Request):
            self.put_request(response)
        elif callable(callback):
            for rsp in callback(response):
                if isinstance(rsp, Request):
                    self.put_request(rsp)
                elif isinstance(rsp, dict):
                    self.process_item(rsp)

    def process_item(self, item):
        # print(item)
        self.item_q.put(item)

    def get_proxies(self, proxy=None):
        if proxy is None:
            if self.proxy_q.empty():
                return None
            else:
                proxy = self.proxy_q.get()
        proxies = {
            'http': proxy,
            'https': proxy
        }
        return proxies

    @staticmethod
    def item_to_proxy(item):
        proxy = '{}://{}:{}'.format(item['protocol'].lower(), item['ip'], item['port'])
        return proxy


class Downloader(object):
    def __init__(self, crwaler=None):
        self.crwaler = crwaler
        self.session = requests.Session()
        self.max_retries = getattr(settings, 'MAX_RETRIES', 0)
        self.timeout = getattr(settings, 'DOWNLOAD_TIMEOUT', 15)
        self.allow_redirects = getattr(settings, 'ALLOW_REDIRECTS', True)
        self.proxies = getattr(settings, 'PROXIES', None)

    def download(self, request):
        prepared = self.session.prepare_request(request)
        max_retries = getattr(request, 'max_retries', None) or self.max_retries
        timeout = getattr(request, 'timeout', None) or self.timeout
        allow_redirects = getattr(request, 'allow_redirects', None) or self.allow_redirects
        proxies = getattr(request, 'proxies', None) or self.proxies
        try:
            response = self.session.send(prepared, proxies=proxies, allow_redirects=allow_redirects, timeout=timeout)
            if response.status_code == 200:
                logging.debug('{}[{}] Successed.'.format(request.url, response.status_code))
                return response
        except Exception as e:
            logging.exception(request.url)
        if request.retries < max_retries:
            request.retries += 1
            return request
        else:
            return None




