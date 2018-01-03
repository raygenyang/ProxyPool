import requests
import time
import gevent

proxy_count = 0
ip_count = 0


def check_proxy(proxy, name=None):
    global ip_count, proxy_count
    proxy_count += 1
    # print(name, proxy, ip_count, proxy_count)
    proxies = {
        'http': proxy,
        'https': proxy
    }
    try:
        r = requests.get('http://www.baidu.com', proxies=proxies, timeout=20, verify=False)
        if r.status_code == 200:
            ip_count += 1
            print(name + '\t', time.time(), proxy, '有效', r.elapsed.seconds, r.elapsed.microseconds/1000000, ip_count, proxy_count)
            return True
    except Exception as e:
        gevent.sleep(1)
    try:
        r = requests.get('http://www.qq.com', proxies=proxies, timeout=20, verify=False)
        if r.status_code == 200:
            ip_count += 1
            print(name + '\t', time.time(), proxy, '有效', r.elapsed.seconds, r.elapsed.microseconds/1000000, ip_count, proxy_count)
            return True
    except Exception as e:
        gevent.sleep(1)
    try:
        r = requests.get('http://www.taobao.com', proxies=proxies, timeout=20, verify=False)
        if r.status_code == 200:
            ip_count += 1
            print(name + '\t', time.time(), proxy, '有效', r.elapsed.seconds, r.elapsed.microseconds/1000000, ip_count, proxy_count)
            return True
    except Exception as e:
        gevent.sleep(1)
    try:
        r = requests.get('http://httpbin.org/ip', proxies=proxies, timeout=20, verify=False)
        if r.status_code == 200:
            ip_count += 1
            print(name + '\t', time.time(), proxy, '有效', r.elapsed.seconds, r.elapsed.microseconds/1000000, ip_count, proxy_count)
            return True
    except Exception as e:
        return False
