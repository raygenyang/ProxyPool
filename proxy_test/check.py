import requests
import time

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
    # try:
    #     # 超过20秒的代理就不要了
    #     # print(name, proxy, time.time())
    #     r = requests.get('http://www.baidu.com', proxies=proxies, timeout=20, verify=False)
    #     if r.status_code != 200:
    #         return False
    # except Exception as e:
    #     return False
    try:
        # 超过20秒的代理就不要了
        r = requests.get('http://httpbin.org/ip', proxies=proxies, timeout=5, verify=False)
        if r.status_code == 200:
            ip_count += 1
            print(name + '\t', time.time(), proxy, '有效', r.elapsed.seconds, r.elapsed.microseconds/1000000, ip_count, proxy_count)
            return True
    except Exception as e:
        return False
